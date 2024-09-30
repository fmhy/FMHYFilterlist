import datetime

def generate_blocklist(output_file, format, is_sitelist_plus: bool = False, filterlist_file_ublock_only:str = ''):
  """
  Combines and modifies content of two files into a new file, 
  replacing placeholders, counting entries and adding text characters for proper format support.
  """
  header_file = "header.txt"
  sitelist_file = "sitelist.txt"
  sitelist_file_plus = "sitelist-plus.txt"
  # Get current time in desired format with timezone-aware object
  current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y %H:%M UTC")

  # Count entries in filtered file, ignoring lines starting with "!"
  num_entries = 0
  with open(sitelist_file, 'r') as f_filtered:
        num_entries += countUncommentedLines(sitelist_file)
  if (is_sitelist_plus):
          num_entries += countUncommentedLines(sitelist_file_plus)
  if format == 'ublock':
          num_entries += countUncommentedLines(filterlist_file_ublock_only)

  # Open header and combined files
  with open(header_file, 'r') as f_header, open(output_file, 'w') as f_combined:
    header_lines = f_header.readlines()

    # Replace placeholders in header lines
    for i, line in enumerate(header_lines):
      if line.startswith('Title:'):
          header_lines[i] = line.replace('${filterlist_edition}', 'Plus' if is_sitelist_plus else 'Basic')
      elif line.startswith('Description:'):
          header_lines[i] = line.replace('${sites_blocked}', 'malicious and not recommended' if is_sitelist_plus else 'malicious')
      elif line.startswith('Last modified:'):
        header_lines[i] = line.replace('${current_time}', current_time)
      elif line.startswith('Entries:'):
        header_lines[i] = line.replace('${num_entries}', str(num_entries))
      elif line.startswith('Format:'):
        header_lines[i] = line.replace('${format}', format)

      # Add comment symbols before every header line
      if format == 'ublock' or format == 'abp':
        header_lines[i] = ('! ' + header_lines[i])
      if format == 'hosts' or format == 'domains' or format == 'wildcard_domains' or format == 'wildcard_urls':
        header_lines[i] = ('# ' + header_lines[i])

    # Add proper filterlist formatting
    domains_lines = formatFile(sitelist_file, format)
    if (is_sitelist_plus):
     domains_lines_plus = formatFile(sitelist_file_plus, format)

    # Write modified header and filtered content
    if format == 'abp':
      f_combined.writelines("[Adblock Plus]\n")
    f_combined.writelines(header_lines)
    f_combined.writelines("\n")
    f_combined.writelines(domains_lines)
    if (is_sitelist_plus):
      if format == 'domains' or format == 'hosts' or format == 'wildcard_domains':
        f_combined.writelines("\n")
      f_combined.writelines(domains_lines_plus)
    if format == 'ublock':
      f_combined.writelines(open(filterlist_file_ublock_only, 'r'))

  print("Generated filterlist with " + format + " format as " + output_file + "!")

# Add proper filterlist formatting to the domains
def formatFile(filename: str, format: str):
  with open(filename, 'r') as f:
    file = f.readlines()
    for i, line in enumerate(file):
      if not line.startswith('!'):
        if format == 'ublock' or format == 'abp':
          file[i] = line.replace("\n", '')
          file[i] = ('||' + file[i] + '^' + "\n")
        elif format == 'hosts':
          file[i] = ('0.0.0.0 ' + file[i])
        elif format == 'wildcard_domains':
          file[i] = ('*.' + file[i])
        elif format == 'wildcard_urls':
          file[i] = line.replace("\n", '')
          file[i] = ('*://*.' + file[i] + '/*' + "\n")
      else:
        if format == 'hosts' or format == 'domains' or format == 'wildcard_domains' or format == 'wildcard_urls':
          file[i] = line.replace('!', '#')
      line.format()
  return file

def countUncommentedLines(filename: str) -> int:
  count = 0
  with open(filename, 'r') as file:
   for line in file:
      if not line.startswith('!'):
        count += 1
  return count  

# Generate Header to make filterlist
print("Generating filterlist.")
# Generate Plus version filterlist files
generate_blocklist("filterlist.txt", "ublock", True, "filters-ublock-only.txt")
generate_blocklist("filterlist-abp.txt", "abp", True)
generate_blocklist("filterlist-domains.txt", "domains", True)
generate_blocklist("filterlist-wildcard-domains.txt", "wildcard_domains", True)
generate_blocklist("filterlist-wildcard-urls.txt", "wildcard_urls", True)
generate_blocklist("filterlist-hosts.txt", "hosts", True)
# Generate Basic version filterlist files
generate_blocklist("filterlist-basic.txt", "ublock", False, "filters-ublock-only.txt")
generate_blocklist("filterlist-basic-abp.txt", "abp")
generate_blocklist("filterlist-basic-domains.txt", "domains")
generate_blocklist("filterlist-basic-wildcard-domains.txt", "wildcard_domains")
generate_blocklist("filterlist-basic-wildcard-urls.txt", "wildcard_urls")
generate_blocklist("filterlist-basic-hosts.txt", "hosts")
print("Build Finished")
