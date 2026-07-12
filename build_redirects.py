"""Find cross-host redirect candidates in FMHY's wiki resource links."""

import argparse
import concurrent.futures
import ipaddress
import json
import re
import socket
import sys
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


USER_AGENT = "FMHYFilterlist redirect checker/1.0"
DEFAULT_WIKI_URL = "https://api.fmhy.net/single-page"
MARKDOWN_LINK = re.compile(
    r"\]\((https?://(?:\\.|[^()\s]|\([^()\s]*\))+)", re.IGNORECASE
)
INTERNAL_WIKI_HOSTS = {"fmhy.net", "api.fmhy.net", "www.reddit.com", "reddit.com"}
TWO_PART_PUBLIC_SUFFIXES = {
    "co.uk", "org.uk", "com.au", "net.au", "co.nz", "com.br", "co.jp", "co.in"
}
EQUIVALENT_SERVICE_HOSTS = (
    {"discord.gg", "discord.com"},
    {"redd.it", "reddit.com"},
    {"twitter.com", "x.com"},
    {"youtu.be", "youtube.com"},
)
EXCLUDED_TARGET_HOSTS = {"accounts.google.com", "discord.com"}
TRACKING_QUERY_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def assert_public_url(url: str) -> None:
    """Reject credentials and hosts that resolve to non-public addresses."""
    parts = urlsplit(url)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"Expected an absolute HTTP(S) URL: {url}")
    if parts.username or parts.password:
        raise ValueError(f"Credentials are not allowed in redirect URLs: {url}")
    if parts.hostname.lower() == "localhost":
        raise ValueError(f"Non-public redirect URL: {url}")

    try:
        addresses = [ipaddress.ip_address(parts.hostname)]
    except ValueError:
        addresses = {
            ipaddress.ip_address(result[4][0])
            for result in socket.getaddrinfo(
                parts.hostname, parts.port or 443, type=socket.SOCK_STREAM
            )
        }
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError(f"Non-public redirect URL: {url}")


class PublicRedirectHandler(HTTPRedirectHandler):
    """Validate every redirect hop before urllib follows it."""

    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        assert_public_url(new_url)
        return super().redirect_request(
            request, file_pointer, code, message, headers, new_url
        )


PUBLIC_URL_OPENER = build_opener(PublicRedirectHandler)


def normalize_url(url: str) -> str:
    """Return a stable HTTP(S) URL suitable for comparison and JSON output."""
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError(f"Expected an absolute HTTP(S) URL: {url}")
    if parts.username or parts.password:
        raise ValueError(f"Credentials are not allowed in redirect URLs: {url}")

    hostname = parts.hostname.lower()
    port = parts.port
    default_port = (parts.scheme.lower() == "http" and port == 80) or (
        parts.scheme.lower() == "https" and port == 443
    )
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parts.path.rstrip("/")
    query = urlencode([
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in TRACKING_QUERY_KEYS
    ])
    return urlunsplit((parts.scheme.lower(), netloc, path, query, ""))


def resolve_redirect(url: str, timeout: float = 15.0) -> str:
    """Follow redirects and return the final response URL."""
    assert_public_url(url)
    request = Request(
        url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"}
    )
    with PUBLIC_URL_OPENER.open(request, timeout=timeout) as response:
        return response.geturl()


def fetch_wiki(url: str = DEFAULT_WIKI_URL, timeout: float = 30.0) -> str:
    """Download FMHY's single-page Markdown export."""
    assert_public_url(url)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with PUBLIC_URL_OPENER.open(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def extract_wiki_urls(markdown: str) -> list[str]:
    """Extract links from FMHY resource-list lines, excluding wiki navigation."""
    urls = {}
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("*") or "**" not in stripped:
            continue
        for match in MARKDOWN_LINK.finditer(line):
            value = match.group(1).replace("\\)", ")")
            normalized = normalize_url(value)
            hostname = urlsplit(normalized).hostname or ""
            if hostname.removeprefix("www.") in INTERNAL_WIKI_HOSTS:
                continue
            urls.setdefault(normalized, value)
    return [urls[key] for key in sorted(urls)]


def read_sources(path: Path) -> list[str]:
    """Read non-empty, non-comment URL lines and reject duplicates."""
    sources = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = line.strip()
        if not value or value.startswith("!") or value.startswith("#"):
            continue
        normalized = normalize_url(value)
        if normalized in seen:
            raise ValueError(f"Duplicate URL on line {line_number}: {normalized}")
        seen.add(normalized)
        sources.append(value)
    return sources


def site_key(hostname: str) -> str:
    """Return a dependency-free registrable-site approximation."""
    labels = hostname.removeprefix("www.").split(".")
    if len(labels) <= 2:
        return ".".join(labels)
    last_two = ".".join(labels[-2:])
    return ".".join(labels[-3:]) if last_two in TWO_PART_PUBLIC_SUFFIXES else last_two


def hosts_are_equivalent(source_host: str, target_host: str) -> bool:
    source_host = source_host.removeprefix("www.")
    target_host = target_host.removeprefix("www.")
    if site_key(source_host) == site_key(target_host):
        return True
    return any(
        source_host in group and target_host in group
        for group in EQUIVALENT_SERVICE_HOSTS
    )


def is_candidate_redirect(source_url: str, target_url: str) -> bool:
    """Exclude unsafe downgrades and standardized service handoffs."""
    source = urlsplit(source_url)
    target = urlsplit(target_url)
    hostname = (target.hostname or "").removeprefix("www.")
    return not (
        source.scheme == "https" and target.scheme == "http"
    ) and hostname not in EXCLUDED_TARGET_HOSTS


def generate_candidates(
    sources: Iterable[str], resolver: Callable[[str], str] | None = None
) -> list[dict[str, str]]:
    """Resolve sources into stable, sorted source-to-target alias records."""
    resolver = resolver or resolve_redirect
    candidates = []
    for source in sources:
        normalized_source = normalize_url(source)
        normalized_target = normalize_url(resolver(source))
        source_host = urlsplit(normalized_source).hostname or ""
        target_host = urlsplit(normalized_target).hostname or ""
        if (
            normalized_source != normalized_target
            and not hosts_are_equivalent(source_host, target_host)
            and is_candidate_redirect(normalized_source, normalized_target)
        ):
            candidates.append(
                {"source": normalized_source, "target": normalized_target}
            )
    return sorted(
        candidates, key=lambda candidate: (candidate["source"], candidate["target"])
    )


def scan_candidates(
    sources: Iterable[str], resolver: Callable[[str], str], workers: int
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Resolve URLs concurrently and return successful aliases and failures."""
    candidates = []
    failures = []
    normalized_sources = {}
    for source in sources:
        normalized_sources.setdefault(normalize_url(source), source)
    unique_sources = [normalized_sources[key] for key in sorted(normalized_sources)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(resolver, source): source for source in unique_sources}
        for future in concurrent.futures.as_completed(futures):
            source = futures[future]
            try:
                candidates.extend(
                    generate_candidates([source], resolver=lambda _: future.result())
                )
            except (OSError, ValueError) as error:
                failures.append({"source": normalize_url(source), "error": str(error)})
    candidates.sort(
        key=lambda candidate: (candidate["source"], candidate["target"])
    )
    failures.sort(key=lambda failure: failure["source"])
    return candidates, failures


def load_approved_aliases(path: Path) -> list[dict[str, str]]:
    """Load the manually reviewed alias file, if present."""
    if not path.exists():
        return []
    aliases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(aliases, list):
        raise ValueError(f"Approved alias file must contain a JSON array: {path}")
    for alias in aliases:
        if (
            not isinstance(alias, dict)
            or set(alias) != {"source", "target"}
            or not all(isinstance(alias[key], str) for key in ("source", "target"))
        ):
            raise ValueError(f"Invalid approved alias record in {path}")
    return aliases


def remove_approved_candidates(
    candidates: list[dict[str, str]], approved: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Hide only exact approved pairs so changed destinations are reviewed."""
    approved_pairs = {
        (normalize_url(alias["source"]), normalize_url(alias["target"]))
        for alias in approved
    }
    return [
        candidate
        for candidate in candidates
        if (candidate["source"], candidate["target"]) not in approved_pairs
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan FMHY wiki links and generate redirect candidates."
    )
    parser.add_argument("--wiki-url", default=DEFAULT_WIKI_URL)
    parser.add_argument("--extra-sources", default="redirect-sources.txt")
    parser.add_argument("--approved-file", default="filterlist-redirects.json")
    parser.add_argument(
        "--output",
        default="filterlist-redirect-candidates.json",
        help="generated candidate JSON output path",
    )
    parser.add_argument(
        "--errors-output",
        default="filterlist-redirect-errors.json",
        help="JSON report for URLs that could not be checked",
    )
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=15.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_path = Path(args.output)
    errors_path = Path(args.errors_output)
    approved_path = Path(args.approved_file)
    if args.workers < 1:
        raise ValueError("--workers must be at least 1")
    sources = extract_wiki_urls(fetch_wiki(args.wiki_url))
    extra_path = Path(args.extra_sources)
    if extra_path.exists():
        sources.extend(read_sources(extra_path))
    candidates, failures = scan_candidates(
        sources,
        resolver=lambda source: resolve_redirect(source, timeout=args.timeout),
        workers=args.workers,
    )
    candidates = remove_approved_candidates(
        candidates, load_approved_aliases(approved_path)
    )
    output_path.write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    errors_path.write_text(
        json.dumps(failures, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Checked {len(set(sources))} wiki URLs; generated {len(candidates)} "
        f"cross-host candidates and reported {len(failures)} failures."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
