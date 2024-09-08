# FMHYFilterlist
FMHY Filterlist, Blocks unsafe and optionally also not recommended sites listed in [FMHY unsafe sites](https://fmhy.net/unsafesites).

> [!TIP]
> [Check out the website](https://fmhy.github.io/FMHYFilterlist/site/index.html)

> [!NOTE]
> The "Basic" (recommended to use for inclusion in other blocklists or projects/browsers/etc.. as malicious sites filter, or for non-home network filtering) version blocks only the malicious sites, but the "Plus" (recommended to use for most users) version also blocks not recommended/potentially unsafe sites and apps
## How to use (Plus version) <a name="howtouse-plus"></a>
> [!NOTE]
> Plus version of the filterlist blocks apps and websites like Avast/AVG/Avira/Opera/Kik Messenger/McAfee/CNet/Softonic, if you don't want these services to be blocked for some reason, use the "[Basic](#howtouse-basic)" version of the filterlist instead
### uBlock Origin (Easy):
1. [Go to the website](https://fmhy.github.io/FMHYFilterlist/site/index.html)
2. Click the "1 Click Install For Ublock Origin" button
3. Click the subscribe button
### uBlock Origin (Manual)
1. Open ublock origin and select the cog ( to go to the dashboard ).
2. Click filter lists 
3. Scroll down to "Import" click it and type this url: ```https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist.txt``` and click "Apply Changes"
### Brave Browser:
1. Open a new tab in brave and type ```brave://settings/```
2. Click Shields/Content Filtering/ Scroll down to add custom filter lists
3. Enter this url ```https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist.txt``` and click add.
### Other blockers:
Add blocklist url with right syntax/formatting according to documentation of your blocker.
Blocklist formats:
| Format | Links |
|:--------|:----------------|
| Adblock Plus | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-abp.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-abp.txt`
| uBlock Origin | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist.txt`
| Domains | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-domains.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-domains.txt`
| Hosts | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-hosts.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-hosts.txt`
| Wildcard Domains | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-wildcard-domains.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-wildcard-domains.txt`
| Wildcard URLs<br>uBlacklist | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-wildcard-urls.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-wildcard-urls.txt`

If your blocker doesn't support any of these formats, feel free to create an issue for adding support for your blocker.

## How to use (Basic version) <a name="howtouse-basic"></a>
> [!NOTE]
> Basic version of the filterlist doesn't block apps and websites like Avast/AVG/Avira/Opera/Kik Messenger/McAfee/CNet/Softonic, if you do want services like this to be blocked, please use the "[Plus](#howtouse-plus)" version of the filterlist instead
### uBlock Origin (Manual)
1. Open ublock origin and select the cog ( to go to the dashboard ).
2. Click filter lists 
3. Scroll down to "Import" click it and type this url: ```https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic.txt``` and click "Apply Changes"
### Brave Browser:
1. Open a new tab in brave and type ```brave://settings/```
2. Click Shields/Content Filtering/ Scroll down to add custom filter lists
3. Enter this url ```https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic.txt``` and click add.
### Other blockers:
Add blocklist url with right syntax/formatting according to documentation of your blocker.
Blocklist formats:
| Format | Links |
|:--------|:-----------------|
| Adblock Plus | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic-abp.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic-abp.txt`
| uBlock Origin | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic.txt`
| Domains | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic-domains.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic-domains.txt`
| Hosts | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic-hosts.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic-hosts.txt`
| Wildcard Domains | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic-wildcard-domains.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic-wildcard-domains.txt`
| Wildcard URLs<br>uBlacklist | Main Link - `https://raw.githubusercontent.com/fmhy/FMHYFilterlist/main/filterlist-basic-wildcard-urls.txt`<br>Mirror - `https://fmhy.github.io/FMHYFilterlist/filterlist-basic-wildcard-urls.txt`

## How to contribute.

Fork the project, add a website in sitelist.txt (or in sitelist-plus.txt if the domain fits in the Plus category) and run build.py then submit a pull request. 

## Want to be a collaborator?

Dm me in discord ( windowsaurora ) to request to be a collaborator this ensure the filterlist stays up to date if i can not update it. please note that you should have at least 1 pull request accepted to request being a collaborator.