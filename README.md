justseeditdl - Autonomous downloader
====================================
Script used to autonomously download and delete files fully downloaded at http://justseed.it/

The script is intended to run via crontab fetching files which are 100% complete. After a successful download file are deleted remotely.

Installation & configuration
============================
Update KEY, PATH and LOG_FILENAME inline with your system

The KEY can be retrieved from the justseedit options sub-menu http://justseed.it/options/index.csp the API key would be a 40 character hash.

Add to crontab.

