# Contributing

## Adding a website:

Fork the project, add a website in sitelist.txt (or in sitelist-plus.txt if the domain fits in the Plus category) and run build.py then submit a pull request. 

## Adding a redirect alias

Run the full-wiki redirect scan:

```sh
python build_redirects.py
python -m unittest discover -s tests -v
```

The generator scans resource links from FMHY's single-page export, follows HTTP
redirects concurrently, preserves paths and query strings, and writes possible
cross-host changes to `filterlist-redirect-candidates.json`. It writes URLs that
could not be checked to the ignored
`filterlist-redirect-errors.json` review file.

Same-site changes, HTTPS downgrades, and known authentication, invite,
short-link and tracking redirects are excluded from the candidate file.

Verify that a candidate is the same resource under continued ownership before
copying its exact `source` and `target` pair into the manually maintained
`filterlist-redirects.json`. A redirect alone is not approval: expired, parked,
sold or compromised domains can redirect to unrelated sites.

The next scan removes exact approved pairs from the candidate report. If an
approved source begins redirecting somewhere else, the changed pair appears as
a new candidate and must be reviewed again.

Commit the candidate file when it helps reviewers audit a scan. Consumers must
use only `filterlist-redirects.json`.

`redirect-sources.txt` is only for additional FMHY-listed URLs that are not
discoverable in the wiki export.
