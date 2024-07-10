import datetime

def generate_blocklist(header_file, sitelist_file, output_file, format, filterlist_file_ublock_only=''):
  """
  Combines and modifies content of two files into a new file, 
  replacing placeholders, counting entries and adding text characters for proper format support.
  """
  # Get current time in desired format with timezone-aware object
  current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y %H:%M UTC")

  # Count entries in filtered file, ignoring lines starting with "!"
  num_entries = 0
  with open(sitelist_file, 'r') as f_filtered:
    for line in f_filtered:
      if not line.startswith('!'):
        num_entries += 1
  if format == 'ublock':
    with open(filterlist_file_ublock_only, 'r') as f_filtered_ublock:
      for line in f_filtered_ublock:
        if not line.startswith('!'):
          num_entries += 1

  # Open header and combined files
  with open(header_file, 'r') as f_header, open(sitelist_file, 'r') as f_domains, open(output_file, 'w') as f_combined:
    header_lines = f_header.readlines()

    # Replace placeholders in header lines
    for i, line in enumerate(header_lines):
      if line.startswith('Last modified:'):
        header_lines[i] = line.replace('${current_time}', current_time)
      elif line.startswith('Entries:'):
        header_lines[i] = line.replace('${num_entries}', str(num_entries))
      elif line.startswith('Format:'):
        header_lines[i] = line.replace('${format}', format)
      # Add comment symbols before every header line
      if format == 'ublock' or format == 'abp':
        header_lines[i] = ('! ' + header_lines[i])
      if format == 'hosts' or format == 'domains' or format == 'wildcard_domains':
        header_lines[i] = ('# ' + header_lines[i])

    # Add proper filterlist formatting to the domains
    domains_lines = f_domains.readlines()
    for i, line in enumerate(domains_lines):
      if not line.startswith('!'):
        if format == 'ublock' or format == 'abp':
          domains_lines[i] = line.replace("\n", '')
          domains_lines[i] = ('||' + domains_lines[i] + '^' + "\n")
        elif format == 'hosts':
          domains_lines[i] = ('0.0.0.0 ' + domains_lines[i])
        elif format == 'wildcard_domains':
          domains_lines[i] = ('*.' + domains_lines[i])
      if line.startswith('!'):
        if format == 'hosts' or format == 'domains' or format == 'wildcard_domains':
          domains_lines[i] = line.replace('!', '#')
      line.format()

    # Write modified header and filtered content
    if format == 'abp':
      f_combined.writelines("[Adblock Plus]\n")
    f_combined.writelines(header_lines)
    f_combined.writelines("\n")
    f_combined.writelines(domains_lines)
    if format == 'ublock':
      f_combined.writelines(open(filterlist_file_ublock_only, 'r'))

  print("Generated filterlist with " + format + " format as " + output_file + "!")

# Generate Header to make filterlist
print("Generating filterlist.")
generate_blocklist("header.txt", "sitelist.txt", "filterlist.txt", "ublock", "filters-ublock-only.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-abp.txt", "abp")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-domains.txt", "domains")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-wildcard-domains.txt", "wildcard_domains")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-hosts.txt", "hosts")
print("Build Finished")