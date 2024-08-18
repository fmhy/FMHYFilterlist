import datetime

def generate_blocklist(header_file, sitelist_file, output_file, format, plus_version: bool, sitelist_file_plus='', filterlist_file_ublock_only=''):
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
  if plus_version == True:
    with open(sitelist_file_plus, 'r') as f_filtered_plus:
      for line in f_filtered_plus:
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
      if line.startswith('Title:'):
        if plus_version == True:
          header_lines[i] = line.replace('${filterlist_edition}', 'Plus')
        elif plus_version == False:
          header_lines[i] = line.replace('${filterlist_edition}', 'Basic')
      if line.startswith('Description:'):
        if plus_version == True:
          header_lines[i] = line.replace('${sites_blocked}', 'malicious and not recommended')
        elif plus_version == False:
          header_lines[i] = line.replace('${sites_blocked}', 'malicious')
      if line.startswith('Last modified:'):
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
        elif format == 'wildcard_urls':
          domains_lines[i] = line.replace("\n", '')
          domains_lines[i] = ('*://*.' + domains_lines[i] + '/*' + "\n")
      if line.startswith('!'):
        if format == 'hosts' or format == 'domains' or format == 'wildcard_domains' or format == 'wildcard_urls':
          domains_lines[i] = line.replace('!', '#')
      line.format()

    # Add proper filterlist formatting to the plus version extra domains
    if plus_version == True:
      with open(sitelist_file_plus, 'r') as f_domains_plus:
        domains_lines_plus = f_domains_plus.readlines()
        for i, line in enumerate(domains_lines_plus):
          if not line.startswith('!'):
            if format == 'ublock' or format == 'abp':
              domains_lines_plus[i] = line.replace("\n", '')
              domains_lines_plus[i] = ('||' + domains_lines_plus[i] + '^' + "\n")
            elif format == 'hosts':
              domains_lines_plus[i] = ('0.0.0.0 ' + domains_lines_plus[i])
            elif format == 'wildcard_domains':
              domains_lines_plus[i] = ('*.' + domains_lines_plus[i])
            elif format == 'wildcard_urls':
              domains_lines_plus[i] = line.replace("\n", '')
              domains_lines_plus[i] = ('*://*.' + domains_lines_plus[i] + '/*' + "\n")
          if line.startswith('!'):
            if format == 'hosts' or format == 'domains' or format == 'wildcard_domains' or format == 'wildcard_urls':
             domains_lines_plus[i] = line.replace('!', '#')
          line.format()

    # Write modified header and filtered content
    if format == 'abp':
      f_combined.writelines("[Adblock Plus]\n")
    f_combined.writelines(header_lines)
    f_combined.writelines("\n")
    f_combined.writelines(domains_lines)
    if plus_version == True:
      if format == 'domains' or format == 'hosts' or format == 'wildcard_domains':
        f_combined.writelines("\n")
      f_combined.writelines(domains_lines_plus)
    if format == 'ublock':
      f_combined.writelines(open(filterlist_file_ublock_only, 'r'))

  print("Generated filterlist with " + format + " format as " + output_file + "!")

# Generate Header to make filterlist
print("Generating filterlist.")
# Generate Plus version filterlist files
generate_blocklist("header.txt", "sitelist.txt", "filterlist.txt", "ublock", True, "sitelist-plus.txt", "filters-ublock-only.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-abp.txt", "abp", True, "sitelist-plus.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-domains.txt", "domains", True, "sitelist-plus.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-wildcard-domains.txt", "wildcard_domains", True, "sitelist-plus.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-wildcard-urls.txt", "wildcard_urls", True, "sitelist-plus.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-hosts.txt", "hosts", True, "sitelist-plus.txt")
# Generate Basic version filterlist files
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic.txt", "ublock", False, filterlist_file_ublock_only="filters-ublock-only.txt")
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic-abp.txt", "abp", False)
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic-domains.txt", "domains", False)
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic-wildcard-domains.txt", "wildcard_domains", False)
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic-wildcard-urls.txt", "wildcard_urls", False)
generate_blocklist("header.txt", "sitelist.txt", "filterlist-basic-hosts.txt", "hosts", False)
print("Build Finished")