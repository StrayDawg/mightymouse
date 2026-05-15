# MightyMouse

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
- Dependencies: `requests`, `selenium`, `qbittorrent-api`, `schedule`

## Setup And Run

1. Clone the repository and open it in your terminal.
2. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

If you are on PowerShell and use a full Python path with spaces, use this form:

```powershell
& "C:/Program Files/Python314/python.exe" -m pip install -r requirements.txt
```

3. Create your local config:
  - If `config.py` is missing, the program will auto-create it from `config-example.py` on first run.
4. Edit `config.py` and set at minimum:
  - `MAM_ID`
  - `MAM_USER_EMAIL`
  - `MAM_USER_PASS`
  - `QBITTORRENT_URL`, `QBITTORRENT_PORT`, `QBITTORRENT_USERNAME`, `QBITTORRENT_PASSWORD`
5. Make sure qBittorrent WebUI is enabled and reachable at the URL/port in `config.py`.
6. Run the bot:

```powershell
python .\mightymouse.py
```

Or with a full interpreter path:

```powershell
& "C:/Program Files/Python314/python.exe" .\mightymouse.py
```

The script starts immediately, performs a full pass, then enters its scheduler loop.

## Configuration

See `config.py` for all available settings including:

- `MAM_ID`: Your MAM session ID
- `MAM_USER_EMAIL`, `MAM_USER_PASS`: Credentials used for donation automation
- `RUN_INTERVAL`: Time between automation runs
- `MAM_OPEN_SLOTS`: Number of free unsaturated slots to keep open
- `MAM_DOWNLOAD_ENABLED`: Enable/disable torrent downloads while still running checks
- `SEARCH`: Torrent search parameters posted to MAM search API
- `BUY_VIP`, `BUY_UPLOAD`, `DONATE_TO_POT`: Enable/disable automation features
- `POT_INTERVAL`: Donation cadence (for example, `CYCLE`)
- `QBITTORRENT_URL`, `QBITTORRENT_PORT`, `QBITTORRENT_USERNAME`, `QBITTORRENT_PASSWORD`: qBittorrent WebUI connection details
- `CAT_UNSAT`, `CAT_SAT`: qBittorrent category names used for organization
- `AUTO_EXTRACT_DIR`, `AUTO_DEL_BATCH`: Control torrent ZIP extraction and cleanup
- `DEBUG`: Enable verbose logging

## Sample Output

```text
PS O:\source\repos\mightymouse> python .\mightymouse.py
User: ****** - Class: VIP - Bonus Points: 14340
***** Checking Torrent Status *****
You are seeding 145 unsaturated torrents. (Limit: 150 for VIP)
You are seeding 4163 saturated torrents
You are leeching 0 torrents
Unsaturated limit reached! Cannot download new torrents until you have fewer than 145 unsaturated torrents.
User is VIP, searching for free+VIP torrents
***** Fixing categories in qBittorrent *****
***** Checking VIP Status *****
VIP expires at: 2026-08-11 20:40:44 UTC
VIP time remaining (weeks): 12.57 Purchasable (weeks): 0.287 cost (points): 358.75
Minimum VIP purchase is 1 week, skipping...
***** Checking Millionaire's Vault Donation Status *****
Not a new cycle: skipping donation attempt
***** Checking Buy Upload Status *****
You have 14340 seedbonus points, you need 25000 for 50GB (MAM Minimum for automation)
Torrent closest to finishing saturation: The Stolen Princess - STG: 1:39:39 - STG_seconds: 5979
Next saturation completes in 5979 seconds.
Adding extra 5 minute buffer to next run time to allow MAM to update torrent status before next check.
Next run scheduled in 6279 seconds
Next run in 6123s [#-----------------------------------------------------------]
```

## IMPORTANT NOTE: The first time you run this with MAM_DOWNLOAD_ENABLED = True, it's going to download torrents, quite a few of them very quickly :) Be prepared.

```text
Total torrent IDs fetched: 120
Torrent IDs: ['1242307', '1242274', '1242326', '1242260', '1242354', '1242282', '1242361', '1242300', '1242254', '1242264', '1242228', '1242251', '1242338', '1242325', '1242331', '1242348', '1242311', '1242272', '1242236', '1242336', '1242301', '1242316', '1242234', '1242352', '1242372', '1242357', '1242294', '1242327', '1242363', '1242315', '1242287', '1242342', '1242232', '1242275', '1242375', '1242344', '1242280', '1242263', '1242297', '1242353', '1242360', '1242252', '1242320', '1242364', '1242243', '1242328', '1242289', '1242266', '1242323', '1242267', '1242250', '1242374', '1242249', '1242225', '1242329', '1242238', '1242371', '1242302', '1242241', '1242242', '1242283', '1242226', '1242319', '1242365', '1242227', '1242257', '1242370', '1242362', '1242268', '1242330', '1242253', '1242341', '1242310', '1242270', '1242295', '1242255', '1242240', '1242312', '1242235', '1242237', '1242244', '1242314', '1242304', '1242247', '1242340', '1242273', '1242256', '1242259', '1242293', '1242245', '1242229', '1242318', '1242231', '1242296', '1242239', '1242366', '1242281', '1242292', '1242324', '1242261', '1242346', '1242246', '1242343', '1242333', '1242291', '1242269', '1242233', '1242349', '1242230', '1242355', '1242339', '1242258', '1242265', '1242248', '1242298', '1242306', '1242290', '1242308', '1242332', '1242262']
Downloaded: storage\batch_1778862678.3646579.zip
Downloaded: storage\batch_1778862683.8422112.zip
***** Fixing categories in qBittorrent *****
```
