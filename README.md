![picture 0](images/c2578cdc2ca5c1ccd8d12ace71e881cd47e47ab97f05ae45bbc0dff0434e6ea7.jpg)  

## Overview

**MightyMouse** is a Python-based automation bot for MyAnonamouse (MAM) that handles torrent management, bonus point optimization, and qBittorrent category organization.

## Key Features

### Torrent Management

- **Unsaturated Torrent Tracking**: Monitors torrents approaching saturation limit and provides warnings with estimated time to completion
- **Automatic Downloads**: Searches for and downloads free/VIP torrents to fill your unsaturated torrent quota
- **Smart Pagination**: Handles large search results across multiple pages to find optimal torrents

### Bonus Point Automation

- **VIP Auto-Purchase**: Automatically buys VIP time when you have sufficient seed bonus points (configurable)
- **Upload Credit Management**: Purchases upload credits as configured
- **Millionaire's Vault Donations**: Auto-donates seed bonus to the vault once per cycle (when eligible)

### qBittorrent Integration

- **Category Management**: Automatically organizes torrents into categories based on saturation status:
  - `MAM_UNSAT`: Unsaturated torrents (actively seeding to saturation)
  - `MAM_SAT`: Saturated torrents (maintenance seeding)
- **Real-time Sync**: Maintains category consistency between MAM data and qBittorrent

### Scheduler

- **Configurable Intervals**: Runs automation at intervals specified in `config.py` (default: 1 hour)
- **Dynamic Scheduling**: Can use STG (Seed To Gain) times to schedule next run based on torrent saturation progress
- **Progress Tracking**: Visual countdown with ETA using `tqdm` progress bar

## Workflow

1. Fetch user profile and statistics from MAM
2. Retrieve unsaturated, saturated, and leeching torrent lists
3. Search for new free/VIP torrents matching your criteria
4. Download torrents in batches (auto-extract if configured)
5. Sync qBittorrent categories with MAM data
6. Auto-purchase VIP/upload credits if configured
7. Auto-donate to Millionaire's Vault if eligible
8. Monitor torrents close to saturation and alert user
9. Schedule next run with countdown timer

## Requirements

- Python 3.8+
- MAM account with valid session ID 
- qBittorrent 
- Dependencies: `requests`, `selenium`, `qbittorrent-api`, `schedule`, `tqdm`

## Configuration

See `config.py` for all available settings including:

- `MAM_ID`: Your MAM session ID
- `RUN_INTERVAL`: Time between automation runs
- `SEARCH`: Torrent search parameters
- `BUY_VIP`, `BUY_UPLOAD`, `DONATE_TO_POT`: Enable/disable automation features
- `QBITTORRENT_*`: Connection details for qBittorrent WebUI

- Sample Output

```
PS O:\> python .\mightymouse.py
User: ************ - Class: VIP - Bonus Points: 766
***** Checking Torrent Status *****
You are seeding 150 unsaturated torrents. (Limit: 150 for VIP)
You are seeding 864 saturated torrents
You are leeching 0 torrents
Unsaturated limit reached!
User is VIP, searching for free+VIP torrents
***** Fixing categories in qBittorrent *****
***** Checking VIP Status *****
VIP expires at: 2026-06-02 12:50:54 UTC
VIP time remaining (weeks): 12.85 Purchasable (weeks): 0.007 cost (points): 8.75
Minimum VIP purchase is 1 week, skipping...
***** Checking Millionaire's Vault Donation Status *****
You have 766 seedbonus points, you need 2000 for donation (MAM Minimum for automation)
Torrent closest to finishing saturation: Fallschirmjager: Elite German Paratroops In World War II - STG: 6:06:09 - STG_seconds: 21969
Next saturation completes in 21969 seconds.
Next run scheduled in 3600 seconds
Next run in 2622s [################--------------------------------------------]
```
