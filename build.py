import datetime

def combine_files(header_file, sitelist_file, combined_file):
  """
  Combines content of two files into a new file, 
  replacing placeholders and counting entries.
  """
  # Get current time in desired format with timezone-aware object
  current_time = datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y %H:%M UTC")

  # Count entries in filtered file, ignoring lines starting with "!"
  num_entries = 0
  with open(sitelist_file, 'r') as f_filtered:
    for line in f_filtered:
      if not line.startswith('!'):
        num_entries += 1

  # Open header and combined files
  with open(header_file, 'r') as f_header, open(combined_file, 'w') as f_combined:
    header_lines = f_header.readlines()

    # Replace placeholders in header lines
    for i, line in enumerate(header_lines):
      if line.startswith('! Last modified:'):
        header_lines[i] = line.replace('ReplaceString1', current_time)
      elif line.startswith('! Entries:'):
        header_lines[i] = line.replace('ReplaceString2', str(num_entries))

    # Write modified header and filtered content
    f_combined.writelines(header_lines)
    f_combined.writelines(open(sitelist_file, 'r'))

  print("Generated filterlist!")

# Generate Header to make filterlist
print("Generating filterlist.")
combine_files("header.txt", "sitelist.txt", "filterlist.txt")
print("Build Finished")