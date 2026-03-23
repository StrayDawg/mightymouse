
# MAM Information 
# Session ID - create one here: https://www.myanonamouse.net/preferences/index.php?view=security
# I actually have 2 MAM_IDs here because I run with a VPN and without and I switch between them depending on whether I'm connected to the VPN or not. 
# You only need one MAM_ID, but you can have multiple if you want to switch between accounts or use with/without a VPN like I do.
MAM_ID = "" # MyAnonaMouse session ID
#MAM_ID = "" # MyAnonaMouse session ID with VPN (if applicable)

# MAM login information
MAM_USER_EMAIL = "" # MyAnonaMouse email address or username
MAM_USER_PASS = "" # MyAnonaMouse password 
RUN_INTERVAL = 60 * 60 # Time in seconds the script should wait between runs (default is 1 hour)   

# QBittorrent Information
QBITTORRENT_URL = r"http://localhost" # qBittorrent URL (leave as http://localhost if running on the same machine)
QBITTORRENT_PORT = "8080" # qBittorrent port (leave as 8080 if running on the same machine)
QBITTORRENT_USERNAME = "admin" # qBittorrent username
QBITTORRENT_PASSWORD = "admin" # qBittorrent password

# Spend Bonus Points?
# DONATE_TO_POT can lock your account if you don't have your password correct, so make sure to set MAM_USER_PASS before setting DONATE_TO_POT to True
DONATE_TO_POT = False # Automatically donate to the pot once a cycle or day to get FL wedges (requires Selenium and ChromeDriver, leave False to disable) (BROKEN CURRENTLY, DO NOT ENABLE)
POT_INTERVAL = "CYCLE" # Donate to pot once per cycle.
#POT_INTERVAL = "DAILY" # Donate to pot once a day.

BUY_UPLOAD = False # Automatically buy upload (requires Selenium and ChromeDriver, leave False to disable)
BUY_VIP = False # Automatically try to keep VIP full (requires Selenium and ChromeDriver, leave False to disable)

# Webhook (Not used yet)
DISCORD_WEBHOOK = "" # Discord webhook link for notifications (leave blank to disable)
STATS_NOTIFICATION_INTERVAL = 60 * 15 # Time in seconds the script should wait until sending another statistics update (False to disable)

# QBT Automation Options
# AUTO_EXTRACT_DIR = "" # Automatically extract the downloaded torrents to specified directory (leave blank to disable)
# Add this as a watched folder in qBittorrent to automatically add torrents to qBittorrent once extracted
AUTO_EXTRACT_DIR = "C:\\downloads\\mam\\" 
# Automatically delete batch archive files once automatically added to qBittorrent
AUTO_DEL_BATCH = True 

# Debug flag - set to True to enable verbose print statements
DEBUG = False

#Torrent categories in qBittorrent
CAT_UNSAT = "MAM_UNSAT" # qBittorrent category for unsaturated torrents
CAT_SAT = "MAM_SAT" # qBittorrent category for saturated torrents

# MAM Torrent search criteria (shouldn't have to change these, but you can if you want to customize the search)
# More information: https://www.myanonamouse.net/api/endpoint.php/1/tor/js/loadSearchJSONbasic.php
SKIP = ['sSat', 'unsat', 'leeching'] # sSat, unsat, inactHnr, inactUnsat, upInact, inactSat, seedUnsat, seedHnr, leeching, upAct
SEARCH = { 
    "tor": {
        "searchType": "fl", # fl-VIP, fl, nVIP, VIP, nMeta, inactive, active, all
        "minSize": 0, # 0 to disable
        "maxSize": 0, # 0 to disable
        "startNumber": 0,
    },
    "perpage":20
}
