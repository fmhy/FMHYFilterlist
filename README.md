# FMHYFilterlist
FMHY Filterlist, Blocks unsafe sites listed in unsafe sites.

[Check out the website](https://windowsaurora.github.io/FMHYFilterlist/site/index.html)
## How to use
### Ublock origin (Easy):
1. [Go to the website](https://windowsaurora.github.io/FMHYFilterlist/site/index.html)
2. Click the "1 Click Install For Ublock Origin" button
3. Click the subscribe button
### Ublock origin ( Manual )
1. Open ublock origin and select the cog ( to go to the dashboard ).
2. Click filter lists 
3. Scroll down to "Import" click it and type this url: ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist.txt``` and click "Apply Changes"
### Brave Browser:
1. Open a new tab in brave and type ```brave://settings/```
2. Click Shields/Content Filtering/ Scroll down to add custom filter lists
3. Enter this url ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist.txt``` and click add.
### Other blockers:
Add blocklist url with right syntax/formatting according to documentation of your blocker.
Blocklist formats:
1. Adblock Plus syntax (example uses: Pi-hole) - ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist-abp.txt```
2. uBlock Origin syntax - ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist.txt```
3. List of domains - ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist-domains.txt```
4. Hosts file - ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist-hosts.txt```
5. List of domains with wildcards - ```https://raw.githubusercontent.com/WindowsAurora/FMHYFilterlist/main/filterlist-wildcard-domains.txt```

If your blocker doesn't support any of these formats, feel free to create an issue for adding support for your blocker.

## How to contribute.

Fork the project, add a website in sitelist.txt and run build.py then submit a pull request. 

## Want to be a collaborator?

Dm me in discord ( windowsaurora ) to request to be a collaborator this ensure the filterlist stays up to date if i can not update it. please note that you should have at least 1 pull request accepted to request being a collaborator.