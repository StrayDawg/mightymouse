"""MightyMouse - MyAnonamouse Torrent Auto-Seeding Bot v1.0

    Mister Trouble never hangs around
    When he hears this Mighty sound.
    "Here I come to save the day"
    That means that Mighty Mouse is on the way.

    Yes sir, when there is a wrong to right
    Mighty Mouse will join the fight.
    On the sea or on the land,
    He gets the situation well in hand

    So though we are in danger, we never despair
    Cause we know that where there's danger he is there!
    (He is there, on the land, on the sea, in the air!)

    We're not worrying at all
    We're just listening for his call
    “Here I come, to save the day!”
    That means that Mighty Mouse
    Is on the way!

    We're not worrying at all
    We're just listening for his call
    “Here I come, to save the day!”
    That means that Mighty Mouse
    Is on the way!

source: https://www.lyricsondemand.com/tvthemes/mightymouselyrics.html

This module automates interactions with MyAnonamouse (MAM) to fetch torrents,
manage seedbox categories, and handle bonus point automation.

Key Features:
  - User detail and torrent list fetching from MAM
  - Unsaturated torrent searching and downloading
  - Bonus point management (VIP, Upload, Donations)
  - qBittorrent integration for category management
  - Automated donation to Millionaire's Vault

Dependencies:
  - requests: HTTP library for API calls
  - selenium: Web automation for complex interactions
  - qbittorrentapi: qBittorrent WebUI client
  - config: Local configuration module with API credentials
"""

import sys
import os
import shutil

# if config.py doesn't exist, create it using a copy of config-example.py
if not os.path.exists("config.py"):
    shutil.copy("config-example.py", "config.py")
    print(
        "config.py created from config-example.py, please edit config.py with your settings and run the script again."
    )
    sys.exit(0)

import zipfile
import requests
import json
from datetime import datetime, time, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

import time
import schedule
import config

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

# Handle Unicode output on Windows - ensures UTF-8 characters display correctly
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Create storage directory for JSON data files if it doesn't exist
if not os.path.exists(data_dir := "storage"):
    os.mkdir(data_dir)

# Read configuration from config.py with safe defaults
DEBUG = config.DEBUG if hasattr(config, "DEBUG") else False

# Validate MAM_ID is set in config - required for API authentication
MAM_ID = config.MAM_ID if hasattr(config, "MAM_ID") else ""
if MAM_ID == "":
    print(
        "MAM_ID not set in config.py, please create a session ID and set it in config.py"
    )
    sys.exit(1)

# Global session and authentication objects
session = requests.Session()  # Persistent HTTP session for API requests
headers = {}  # HTTP headers with authentication cookie
userinfo = {}  # Cached user information from MAM
freshLoad = True  # Flag for tracking first load
base_url = "https://www.myanonamouse.net"  # MAM base URL
data = {}  # General data storage

def save_json(filename: str, data: dict):
    """Save data to JSON file in storage directory.

    Persists API response data for caching and debugging purposes.
    Uses UTF-8 encoding and pretty-print formatting for readability.

    Args:
        filename (str): Target filename in the storage directory
        data (dict): Dictionary data to serialize as JSON

    Returns:
        None
    """
    filepath = os.path.join("storage", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if DEBUG:
        print(f"Saved to {filepath}")


def convert_timestamps(
    obj, timestamp_fields=["created", "create", "updated", "update", "latest"]
):
    """Recursively convert Unix timestamp fields to human-readable dates.

    Transforms API responses containing Unix timestamps into formatted date strings
    for better readability in JSON output files. Works recursively on nested dicts/lists.

    Args:
        obj: Input object (dict, list, or primitive) to process
        timestamp_fields (list): Field names to treat as timestamps

    Returns:
        Transformed object with timestamps converted to "YYYY-MM-DD HH:MM:SS UTC" format

    Example:
        >>> data = {"created": 1234567890, "name": "test"}
        >>> convert_timestamps(data)
        {"created": "2009-02-13 23:31:30 UTC", "name": "test"}
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            if key in timestamp_fields and isinstance(value, (int, float)):
                result[key] = datetime.fromtimestamp(value, tz=timezone.utc).strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )
            elif isinstance(value, (dict, list)):
                result[key] = convert_timestamps(value, timestamp_fields)
            else:
                result[key] = value
        return result
    elif isinstance(obj, list):
        return [convert_timestamps(item, timestamp_fields) for item in obj]
    else:
        return obj


def fetch_and_save_torrents(uid: int, torrent_type: str, filename: str):
    """Fetch torrents from MAM and save to JSON file for caching.

    Retrieves a list of torrents from MAM API based on torrent type and saves
    the response to a JSON file in the storage directory. Prints torrent details
    to console if DEBUG mode is enabled.

    Args:
        uid (int): MyAnonamouse user ID
        torrent_type (str): Type of torrents to fetch:
            - "unsat" (unsaturated)
            - "sSat" (saturated)
            - "leeching" (currently leeching)
        filename (str): Output filename for JSON storage (e.g., "unsat_torrents.json")

    Returns:
        dict: Parsed JSON response from MAM API containing torrent list,
              or None if the request fails

    API Response Format:
        {"rows": [{"id": "123", "title": "...", "free": "1", "vip": "1"}, ...]}
    """
    iteration = 0  # For pagination    
    looper = True
    tottorrents = {"rows": []}
    while looper:    
        url = f"https://myanonamouse.net/json/loadUserDetailsTorrents.php?uid={uid}&iteration={iteration}&type={torrent_type}"
        response = session.get(url, headers=headers)
        if response.status_code != 200:
            if DEBUG:
                print("Failed to fetch torrent details")
            return        
        torrents = response.json().get("rows", [])
        tottorrents["rows"] = tottorrents["rows"] + torrents        
        tlen = len(torrents)
        if DEBUG:
            print(f"Fetched {tlen} torrents for type {torrent_type}, iteration {iteration}")
            print(f"Total fetched so far: {len(tottorrents['rows'])} torrents")
        if tlen < 250:  # MAM API returns 250 torrents per page, if less than 250 we are on the last page
            looper = False
        iteration += 1
    counter = 1
    for torrent in tottorrents["rows"]:
        if DEBUG:
            print(
                f"{counter}: {torrent['id']} - {torrent['title']} - {torrent['free']} - {torrent['vip']}"
            )
            counter += 1
    save_json(filename, tottorrents)        
    return tottorrents


def getUserDetails() -> dict:
    """Fetch user profile and statistics from MyAnonamouse.

    Retrieves both basic user info and advanced statistics (seed bonus,
    unsaturated limit, VIP status, etc.) from MAM API and caches results.
    Combines responses into a single userinfo dictionary with "simple" and
    "advanced" keys containing profile and stats respectively.

    Args:
        None

    Returns:
        dict: User information with keys:
            - "simple": Basic user profile data
            - "advanced": Advanced stats (seedbonus, VIP status, community class, etc.)
            Returns empty dict {} if API request fails

    Side Effects:
        - Updates global userinfo dict
        - Saves formatted user data to storage/userinfo.json
        - Sets authentication cookie in global headers dict
    """
    headers["cookie"] = f"mam_id={MAM_ID}"
    # Get basic user info
    response = session.get(f"{base_url}/jsonLoad.php", headers=headers)
    if response.status_code != 200:
        return {}
    userinfo["simple"] = response.json()
    # Get advanced user stats
    response = session.get(f"{base_url}/jsonLoad.php?snatch_summary", headers=headers)
    if response.status_code != 200:
        return {}
    userinfo["advanced"] = response.json()
    # Convert timestamps and save
    user_formatted = convert_timestamps(userinfo)
    if DEBUG:
        print("Fetched user details:")
        print(json.dumps(user_formatted, indent=2))
    save_json("userinfo.json", user_formatted)
    print(
        f"User: {userinfo['simple']['username']} - Class: {userinfo['advanced']['classname']} - Bonus Points: {userinfo['advanced']['seedbonus']}"
    )
    return userinfo


def downloadBatch(ids: list):
    """Download torrents from MAM in batches and extract if configured.

    Fetches torrent files in batches of 100 (MAM API limit) as ZIP archives,
    saves to disk with timestamp, optionally extracts to a configured directory,
    and optionally deletes the ZIP file after extraction. Implements 5-second
    delay between batch requests to avoid rate limiting.

    Args:
        ids (list): List of torrent IDs (strings) to download

    Returns:
        None

    Config Requirements:
        - AUTO_EXTRACT_DIR: Directory to extract torrents to (if enabled)
        - AUTO_DEL_BATCH: Whether to delete ZIP file after extraction (bool)
        - DEBUG: Whether to print extraction messages (bool)

    Batch Processing:
        - Processes in chunks of 100 torrents (MAM API limit)
        - Waits 5 seconds between batch downloads for rate limiting
        - Saves each batch with unique timestamp in filename
    """
    # Download in batches - MAM API limit is 100 torrents per request
    for i in range(0, len(ids), 100):
        batch = ids[i : i + 100]
        # Build query string with torrent IDs
        tids = "&".join([f"tids[]={id}" for id in batch])

        # Request torrent batch as ZIP file from MAM
        response = session.get(
            f"{base_url}/DownloadZips.php?type=batch&{tids}",
            headers={**headers, "Content-Type": "application/x-zip"},
            timeout=30,
        )

        # Save ZIP file with timestamp to storage directory
        path = os.path.join(data_dir, f"batch_{time.time()}.zip")
        with open(path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded: {path}")

        # Extract to configured directory if AUTO_EXTRACT_DIR is set
        if config.AUTO_EXTRACT_DIR:
            if config.DEBUG:
                print(f"Extracting {path} to {config.AUTO_EXTRACT_DIR}")
            with zipfile.ZipFile(path, "r") as f:
                f.extractall(config.AUTO_EXTRACT_DIR)
            # Optionally delete ZIP after extraction
            if config.AUTO_DEL_BATCH:
                os.remove(path)

        # Wait 5 seconds before next batch to avoid rate limiting
        time.sleep(5)


def check_and_buy_vip(userinfo: dict):
    """Check VIP status and automatically purchase additional time if configured.

    Monitors VIP expiration time and calculates how much VIP time can be purchased
    with current seed bonus points. Automatically purchases VIP time to the maximum
    allowed duration (3 months) if BUY_VIP config is enabled and user has sufficient
    seed bonus points.

    Args:
        userinfo (dict): User information dict from getUserDetails()

    Returns:
        None

    Config Requirements:
        - BUY_VIP: Whether to automatically purchase VIP time (bool)

    Account Requirements:
        - User must be VIP or Power User class

    Notes:
        - Maximum purchasable: 3 months (12.857 weeks) at 1250 points/week
        - Skips purchase if insufficient seed bonus points
        - Displays VIP expiration time and purchasable duration
    """
    if (
        userinfo["advanced"]["classname"] == "VIP"
        or userinfo["advanced"]["classname"] == "Power User"
    ):
        print("***** Checking VIP Status *****")
        if userinfo["advanced"]["classname"] == "VIP":
            vip_until_raw = userinfo["advanced"]["vip_until"]
            vip_until_timestamp = datetime.strptime(vip_until_raw, "%Y-%m-%d %H:%M:%S")
            vip_until_utc = vip_until_timestamp.replace(tzinfo=timezone.utc)
            current_utc = datetime.now(tz=timezone.utc)
            time_remaining = max(0, (vip_until_utc - current_utc).total_seconds())
            time_remaining_weeks = round(time_remaining / (7 * 24 * 3600), 3)
            max_vip_weeks = 12.857  # 3 months max VIP purchase allowed by MAM
            purchasable_weeks = round(max_vip_weeks - time_remaining_weeks, 3)
            vip_cost_points_perweek = 1250
            purchasable_cost = round(vip_cost_points_perweek * purchasable_weeks, 3)
            if purchasable_cost < 0:
                purchasable_cost = 0
            if purchasable_weeks < 0:
                purchasable_weeks = 0

            print(f"VIP expires at: {vip_until_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(
                f"VIP time remaining (weeks): {time_remaining_weeks}",
                f"Purchasable (weeks): {purchasable_weeks}",
                f"cost (points): {purchasable_cost}",
            )

        if config.BUY_VIP:
            if (
                userinfo["advanced"]["seedbonus"] < purchasable_cost
                or purchasable_weeks <= 1
            ):
                if (
                    purchasable_weeks <= 1  # Min purchase is a week's worth of VIP, which is 1 week
                ):
                    print("Minimum VIP purchase is 1 week, skipping...")
                else:
                    print(
                        f"You have {userinfo['advanced']['seedbonus']} seedbonus points, you need {purchasable_cost} for {round(purchasable_weeks, 3)} weeks of VIP (MAM Minimum for automation)"
                    )
                return
            else:
                r = session.get(
                    f"{base_url}/json/bonusBuy.php?spendtype=VIP&duration=max&_",
                    headers=headers,
                ).json()
                if r["success"]:
                    print(f"{r['amount']} VIP time purchased.")
                else:
                    print("Failed to purchase VIP time: " + r["error"])
    else:
        print("User is not eligible for VIP, skipping VIP purchase")


def check_and_buy_upload(userinfo: dict):
    """Check upload bonus and automatically purchase credits if configured.

    Checks if user has sufficient seed bonus points (25000 = 50GB upload credit)
    and automatically purchases maximum affordable upload credits if BUY_UPLOAD
    is enabled in config.

    Args:
        userinfo (dict): User information dict from getUserDetails()

    Returns:
        None

    Config Requirements:
        - BUY_UPLOAD: Whether to automatically purchase upload credits (bool)

    Notes:
        - Minimum 25000 seed bonus points required for 50GB
        - Purchases maximum affordable amount if points are available
        - Downloads can be started before reaching this limit via downloadBatch()
    """
    if config.BUY_UPLOAD:
        print("***** Checking Buy Upload Status *****")
        if userinfo["advanced"]["seedbonus"] < 25000:
            print(
                f"You have {userinfo['advanced']['seedbonus']} seedbonus points, you need 25000 for 50GB (MAM Minimum for automation)"
            )
        else:
            r = session.get(
                f"{base_url}/json/bonusBuy.php/?spendtype=upload&amount=Max Affordable ",
                headers=headers,
            ).json()
            if r["success"]:
                print(f"{r['amount']} Upload credit purchased.")
            else:
                print("Failed to purchase Upload credit. " + r["error"])


def donate_to_pot():
    """Automatically donate seed bonus to Millionaire's Vault if configured.

    Uses Selenium WebDriver to interact with MAM's Millionaire's Vault donation page.
    Automatically logs in using Selenium, verifies eligibility, and donates 2000 seed
    bonus points once per day. Tracks donation history in storage/millionaires_vault.json
    to avoid duplicate donations in the same cycle.

    Args:
        None (uses global userinfo and config values)

    Returns:
        None

    Config Requirements:
        - DONATE_TO_POT: Whether to auto-donate (bool)
        - USER_EMAIL: MAM account email
        - USER_PASS: MAM account password

    Account Requirements:
        - Minimum 2000 seed bonus points available
        - Must not have already donated today per MAM rules

    Implementation Details:
        - Uses headless Chrome WebDriver for automation
        - Tracks vault total to detect new donation cycles
        - Stores state in storage/millionaires_vault.json
        - Handles Selenium exceptions gracefully
    """
    if config.DONATE_TO_POT:
        if not config.MAM_USER_EMAIL or not config.MAM_USER_PASS:
            print("MAM_USER_EMAIL and MAM_USER_PASS must be set in config.py to donate to the pot.")
            return
        
        print("***** Checking Millionaire's Vault Donation Status *****")
        if userinfo["advanced"]["seedbonus"] < 2000:
            print(
                f"You have {userinfo['advanced']['seedbonus']} seedbonus points, you need 2000 for donation (MAM Minimum for automation)"
            )
            return
        
        try:
            # Selenium Manager automatically handles the driver
            chrome_options = Options()
            if not config.DEBUG:
                chrome_options.add_argument("--headless")                
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://www.myanonamouse.net/millionaires/donate.php?")
            
            username_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "email"))
            )
            password_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            # Enter credentials
            username_field.send_keys(config.MAM_USER_EMAIL)
            password_field.send_keys(config.MAM_USER_PASS)
            
            # Submit the form
            password_field.submit()
            # Wait for login to complete (adjust the selector as needed)
            time.sleep(11)  # Wait for login to complete and page to load

            # check if millionaires json file exists, if not create it with amount_available set to 0
            if not os.path.exists(os.path.join("storage", "millionaires_vault.json")):
                with open(
                    os.path.join("storage", "millionaires_vault.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump({"amount_available": 0}, f, indent=2, ensure_ascii=False)
            # read previous donation total from json file if it exists
            with open(
                os.path.join("storage", "millionaires_vault.json"),
                "r",
                encoding="utf-8",
            ) as f:
                previous_donation_total = json.load(f).get("amount_available", 1)
            
            # find "<A href=> element with id "millionInfo" and add the title and text to variables
            million_info_element = driver.find_element(By.ID, "millionInfo")
            million_info_title = million_info_element.get_attribute("title")
            million_info_text = million_info_element.text
            donation_total = int(
                million_info_text.split(":")[1].strip().split(" ")[0].replace(",", "")
            )
            
            with open(
                os.path.join("storage", "millionaires_vault.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    {"amount_available": donation_total},
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
            
            if config.POT_INTERVAL == "CYCLE":
                if (
                    previous_donation_total > 0
                    and donation_total >= previous_donation_total
                ):
                    if config.DEBUG:
                        print(
                        f"Donation total is {donation_total}, change: {donation_total - previous_donation_total}"
                        )
                    print("Not a new cycle: skipping donation attempt")
                    driver.quit()
                    return
            
            # Check if already donated today by looking for "have already" in million_info_title
            if "have already" in million_info_title:
                print("Already donated today, skipping donation attempt")
                driver.quit()
                return
            else:
                try:
                    select_element = driver.find_element(By.NAME, "Donation")
                    select_object = Select(select_element)
                    select_object.select_by_visible_text("2000")
                    check_input = driver.find_element(By.NAME, "submit")
                    check_input.click()
                    time.sleep(10)
                    million_info_element = driver.find_element(By.ID, "millionInfo")
                    million_info_title = million_info_element.get_attribute("title")
                    if "have already" in million_info_title:
                        print("Donation successful!")
                    else:
                        print(
                            r"Donation may have failed, please check 'https://www.myanonamouse.net/millionaires/donate.php?' manually."
                        )
                except Exception as e:
                    print(f"Error during donation process: {e}")
                    
            driver.quit()            
        except Exception as e:
            print(f"Selenium error: {e}")


def fetch_and_download_torrents(userinfo: dict):
    """Fetch all torrent lists and download new unsaturated torrents.

    Main torrent management function that:
    1. Fetches user's unsaturated/saturated/leeching torrent lists from MAM
    2. Calculates how many new torrents can be downloaded (based on unsaturated limit)
    3. Searches MAM for free or free+VIP torrents matching config search criteria
    4. Downloads torrents in batches when quota allows
    5. Returns torrent IDs for qBittorrent category management

    Args:
        userinfo (dict): User information from getUserDetails()

    Returns:
        tuple: (unSatTorrents, sSatTorrents, leechingTorrents, didDownload)
            - unSatTorrents (list): IDs of unsaturated torrents user is seeding
            - sSatTorrents (list): IDs of saturated torrents user is seeding
            - leechingTorrents (list): IDs of torrents user is leeching
            - didDownload (bool): Whether torrents were downloaded this run

    Config Requirements:
        - SEARCH: Search parameters dict including:
            - "perpage": Results per page (default: 20)
            - "tor": Seed/leech ratio filters, sorting, category, start number, etc.

    Behavior Notes:
        - Sets SEARCH["tor"]["searchType"] to "fl-VIP" for VIP users, otherwise "fl"
        - Updates SEARCH["tor"]["startNumber"] as it paginates results

    Algorithm:
        - Searches are performed in sequence with pagination
        - Downloads stop when unsaturated limit is reached
        - Torrents are consolidated and deduplicated
        - Only free/VIP torrents that user isn't already seeding are considered
    """
    print("***** Checking Torrent Status *****")
    # Fetch and save unsaturated torrents
    unSat = fetch_and_save_torrents(
        userinfo["simple"]["uid"], "unsat", "unsat_torrents.json"
    )
    if not unSat or not isinstance(unSat, dict) or "rows" not in unSat:
        print("ERROR: Failed to fetch unsaturated torrents or invalid response format")
        return [], [], [], False
    
    print(
        f"You are seeding {len(unSat['rows'])} unsaturated torrents. (Limit: {userinfo['advanced']['unsat']['limit']} for {userinfo['advanced']['classname']})"
    )
    unSatTorrents = []
    for torrent in unSat["rows"]:
        unSatTorrents.append(torrent["id"])
    unSatCount = len(unSat["rows"])
    # Fetch and save saturated torrents   
    sSat = fetch_and_save_torrents(
        userinfo["simple"]["uid"], "sSat", "sat_torrents.json"
    )
    if not sSat or not isinstance(sSat, dict) or "rows" not in sSat:
        print("ERROR: Failed to fetch saturated torrents or invalid response format")
        return [], [], [], False
    
    print(f"You are seeding {userinfo['advanced']['sSat']['count']} saturated torrents")
    sSatTorrents = []
    for torrent in sSat["rows"]:
        sSatTorrents.append(torrent["id"])
    sSatCount = len(sSat["rows"])
    leeching = fetch_and_save_torrents(
        userinfo["simple"]["uid"], "leeching", "leeching_torrents.json"
    )
    if not leeching or not isinstance(leeching, dict) or "rows" not in leeching:
        print("ERROR: Failed to fetch leeching torrents or invalid response format")
        return [], [], [], False
    
    print(f"You are leeching {len(leeching['rows'])} torrents")
    leechingTorrents = []
    for torrent in leeching["rows"]:
        leechingTorrents.append(torrent["id"])
    leechingCount = len(leeching["rows"])
    unsatLimit = userinfo["advanced"]["unsat"]["limit"]
    if unsatLimit and unSatCount >= unsatLimit:
        print("Unsaturated limit reached!")
        canDownload = 0
    elif unsatLimit:
        print(
            f"Unsaturated limit not reached: Can get {unsatLimit - unSatCount} more torrents"
        )
        canDownload = unsatLimit - unSatCount
    didDownload = False
    torrentids = []
    search = config.SEARCH
    if userinfo["advanced"]["classname"] == "VIP":
        print("User is VIP, searching for free+VIP torrents")
        search["tor"]["searchType"] = "fl-VIP"
    else:
        print("User is not VIP, searching for free torrents")
        search["tor"]["searchType"] = "fl"
    startNumber = 0
    torCounter = 0
    keepDownloading = True
    downloadsNeeded = canDownload
    while canDownload > 0:
        if keepDownloading == True:
            print(
                f"getting torrents... {startNumber} - {startNumber + config.SEARCH['perpage']  - 1}"
            )
            response = session.post(
                f"{base_url}/tor/js/loadSearchJSONbasic.php",
                headers=headers,
                json=config.SEARCH,
            )
            if response.status_code == 200:
                torrents = response.json()
                for torrent in torrents["data"]:
                    if str(torrent["id"]) in unSatTorrents:
                        canDownload += 1
                        continue
                    if str(torrent["id"]) in sSatTorrents:
                        canDownload += 1
                        continue
                    if str(torrent["id"]) in leechingTorrents:
                        canDownload += 1
                        continue
                    if torrent["free"] == "0" or torrent["vip"] == "0":
                        canDownload += 1
                        continue

                    print(
                        f"{torrent['id']} - {torrent['title']} - {torrent['size']} - {torrent['free']} - {torrent['vip']} - Adding torrent ID"
                    )
                    torrentids.append(str(torrent["id"]))
                    torrentids = list(set(torrentids))
                    torCounter = len(torrentids)
                    canDownload -= 1
                    if torCounter == downloadsNeeded:
                        keepDownloading = False
                        break

            config.SEARCH["tor"]["startNumber"] = startNumber
            startNumber += 20
        else:
            break
    if unSatCount >= unsatLimit:
        pass
    else:
        print(f"Total torrent IDs fetched: {len(list(set(torrentids)))}")
        print(f"Torrent IDs: {list(set(torrentids))}")
        downloadBatch(list(set(torrentids)))
        didDownload = True
    return unSatTorrents, sSatTorrents, leechingTorrents, didDownload


def manage_qbittorrent_categories(
    unSatTorrents: list, sSatTorrents: list, leechingTorrents: list
):
    """Manage qBittorrent torrent categories based on MAM saturation status.

    Connects to qBittorrent WebUI via qbittorrentapi, creates configured categories
    if they don't exist, and updates torrent categories based on their current
    saturation status in MAM. Reads torrent comments for MAM ID (MID=xxxxx format)
    to match qBittorrent torrents with MAM data.

    Args:
        unSatTorrents (list): IDs of unsaturated torrents (category: CAT_UNSAT)
        sSatTorrents (list): IDs of saturated torrents (category: CAT_SAT)
        leechingTorrents (list): IDs of leeching torrents (no category change)

    Returns:
        None

    Config Requirements:
        - QBITTORRENT_URL: Hostname/IP of qBittorrent WebUI
        - QBITTORRENT_PORT: Port for qBittorrent WebUI (typically 8080)
        - QBITTORRENT_USERNAME: WebUI authentication username
        - QBITTORRENT_PASSWORD: WebUI authentication password
        - CAT_UNSAT: Category name for unsaturated torrents
        - CAT_SAT: Category name for saturated torrents

    Created Categories:
        - CAT_UNSAT: Unsaturated torrents (actively downloading)
        - CAT_SAT: Saturated torrents (seed-only mode)

    Torrent Metadata:
        - Reads torrent "comment" field for MAM ID extraction
        - Expected format: "MID=<torrent_id>,<other_data>"
        - Uses qBittorrent API to modify category per torrent

    Error Handling:
        - Gracefully handles missing qBittorrent credentials
        - Catches and logs API connection errors
        - Continues processing on category creation failures
    """
    if not (
        config.QBITTORRENT_URL
        and config.QBITTORRENT_USERNAME
        and config.QBITTORRENT_PASSWORD
    ):
        print(
            "qBittorrent credentials not fully provided, skipping qBittorrent category management"
        )
        return
    print("***** Fixing categories in qBittorrent *****")
    try:
        import qbittorrentapi

        conn_info = dict(
            host=config.QBITTORRENT_URL,
            port=config.QBITTORRENT_PORT,
            username=config.QBITTORRENT_USERNAME,
            password=config.QBITTORRENT_PASSWORD,
        )
        qb = qbittorrentapi.Client(**conn_info)
        try:
            qb.auth_log_in()
        except qbittorrentapi.LoginFailed as e:
            print(e)
        # check for MAM categories, if they don't exist create them
        categories = qb.torrent_categories.categories.keys()
        if DEBUG:
            print(f"Existing qBittorrent categories: {categories}")
        try:
            if config.CAT_UNSAT not in categories:
                qb.torrent_categories.createCategory(category=config.CAT_UNSAT)
            if config.CAT_SAT not in categories:
                qb.torrent_categories.createCategory(category=config.CAT_SAT)
        except Exception as e:
            print(f"Error creating categories in qBittorrent: {e}")

        # Get list of seeding torrents in qBittorrent with category "MAM"
        torrents = qb.torrents_info(category=config.CAT_UNSAT)
        torrents += qb.torrents_info(category=config.CAT_SAT)

        for torrent in torrents:
            # get the torrent comments, if it contains "MID={torrent_id}" extract that to a variable
            if torrent["comment"] and "MID=" in torrent["comment"]:
                mid = torrent["comment"].split(",")[0].split("MID=")[1]
                if mid in unSatTorrents:
                    if DEBUG:
                        print(
                            f"Torrent ID {mid} Unsaturated, moving to MAM_UNSAT category"
                        )
                    torrent.set_category(category=config.CAT_UNSAT)

                if mid in sSatTorrents:
                    if DEBUG:
                        print(f"Torrent ID {mid} Saturated, moving to MAM_SAT category")
                    torrent.set_category(category=config.CAT_SAT)

                if mid in leechingTorrents:
                    if DEBUG:
                        print(f"Torrent ID {mid} Leeching, skipping category change")
                    pass
    except Exception as e:
        print(f"Error in qBittorrent: {e}")


def warn_on_unsat_stg_threshold(
    unsat_torrents_path: str, threshold_seconds: int = 1 * 3600
):
    """Warn when unsaturated torrents are close to saturation.

    Reads unsaturated torrents JSON and checks the STG time for each torrent.
    If the remaining time is below the threshold, a warning is printed.

    Args:
        unsat_torrents_path (str): Path to unsat_torrents.json
        threshold_seconds (int): Threshold in seconds for warning

    Returns:
        None
    """
    with open(unsat_torrents_path, "r", encoding="utf-8") as f:
        unsat_torrents = json.load(f)

    for torrent in unsat_torrents.get("rows", []):
        if "STG" in torrent:
            # Convert "2d 04:12:00" to seconds
            stg_str = torrent["STG"]
            stg_seconds = 0
            if "d" in stg_str:
                days, stg_str = stg_str.split("d ")
                stg_seconds += int(days.strip()) * 24 * 3600
            if ":" in stg_str:
                # count occurrences of ":" to determine if it's in HH:MM:SS or MM:SS format
                colon_count = stg_str.count(":")
                if colon_count == 2:
                    hours, minutes, seconds = stg_str.split(":")
                    stg_seconds += int(hours.strip()) * 3600
                    stg_seconds += int(minutes.strip()) * 60
                    stg_seconds += int(seconds.strip())
                elif colon_count == 1:
                    minutes, seconds = stg_str.split(":")
                    stg_seconds += int(minutes.strip()) * 60
                    stg_seconds += int(seconds.strip())
            if stg_seconds < 3600:
                if config.DEBUG:
                    print(
                        f"INFO: Torrent '{torrent['title']}' (ID: {torrent['id']}) is close to saturation with STG of {torrent['STG']} ({stg_seconds} seconds remaining)"
                    )
            
            torrent["STG_seconds"] = stg_seconds
    # sort unsat torrents by STG_seconds ascending
    unsat_torrents["rows"] = sorted(
        unsat_torrents.get("rows", []), key=lambda x: x.get("STG_seconds", float("inf"))
    )   
    
    for torrent in unsat_torrents.get("rows", [])[:1]:  # print torrent closest to saturation
        print("Torrent closest to finishing saturation: " + f"{torrent['title']} - STG: {torrent['STG']} - STG_seconds: {torrent.get('STG_seconds', 'N/A')}")
    return torrent["STG_seconds"] if unsat_torrents.get("rows", []) else 0


def main():
    """Main orchestration function for the entire mightymouse automation workflow.

    Executes the complete sequence of automation tasks in order:
    1. Fetch user profile and statistics
    2. Fetch torrent lists and download new torrents if needed
    3. Synchronize qBittorrent categories (initial pass)
    4. Check and auto-purchase VIP time (if configured)
    5. Process Millionaire's Vault donations (if configured)
    6. Check and auto-purchase upload credits (if configured)
    7. Synchronize qBittorrent categories again if downloads were triggered

    Args:
        None (uses global configuration and session state)

    Returns:
        None

    Side Effects:
        - Modifies global userinfo dict
        - Saves JSON files to storage/ directory
        - Downloads torrents and ZIP files to storage/ directory
        - Modifies qBittorrent categories (may run twice per invocation)
        - May purchase VIP/upload credits depending on config and budget
        - Logs all operations to console (more detail if DEBUG=True)

    Configuration:
        - All behavior controlled by config.py settings
        - See individual function docstrings for per-function config requirements

    Typical Execution Flow:
        $ python mightymouse.py
        ***** Checking Torrent Status *****
        ***** Checking VIP Status *****
        ***** Checking Millionaire's Vault Donation Status *****
        ***** Checking Buy Upload Status *****
        ***** Fixing categories in qBittorrent *****
    """
    nextrun = None
    try:
        # Fetch and save user data
        userinfo = getUserDetails()
        
        # Validate userinfo was fetched successfully
        if not userinfo or "simple" not in userinfo or "advanced" not in userinfo:
            print("ERROR: Failed to fetch user details from MAM. Check MAM_ID in config.py and your internet connection.")
            sys.exit(1)
        
        # Fetch and download torrents
        unSatTorrents, sSatTorrents, leechingTorrents, didDownload = (
            fetch_and_download_torrents(userinfo)
        )
        # Manage qBittorrent categories (initial sync)
        manage_qbittorrent_categories(unSatTorrents, sSatTorrents, leechingTorrents)
        # Spend free bonus points (reorder as desired to prioritize one action)
        check_and_buy_vip(userinfo)
        donate_to_pot()  # once per cycle of the Millionaire's Vault, tracks donation history in storage/millionaires_vault.json
        check_and_buy_upload(userinfo)

        # Warn if unsaturated torrents are close to saturation
        nextrun = warn_on_unsat_stg_threshold(
            os.path.join("storage", "unsat_torrents.json")
        )
        print(f"Next saturation completes in {nextrun} seconds.")
        if nextrun < config.RUN_INTERVAL:
            print("Adding extra 5 minute buffer to next run time to allow MAM to update torrent status before next check.")

        # Manage qBittorrent categories again if downloads were triggered
        if didDownload:
            manage_qbittorrent_categories(unSatTorrents, sSatTorrents, leechingTorrents)
    except Exception as e:
        print(f"Error in main workflow: {e}")
        import traceback
        traceback.print_exc()
    return nextrun
    # Bye!


def run_scheduler():
    """Run main() on a repeating schedule.

    Uses config.RUN_INTERVAL by default, but if main() returns a positive
    number of seconds, the lowest of the two values is used for the next delay.
    """

    default_interval = config.RUN_INTERVAL if hasattr(config, "RUN_INTERVAL") else 3600
    
    while True:
        nextrun = main()
        if nextrun is None:
            nextrun = default_interval
        nextrun = nextrun + int(
            5 * 60
        )  # add 5 minutes to the nextrun time to give a buffer for completed torrents to register in MAM adjust if needed

        if isinstance(nextrun, (int, float)) and nextrun > 0:
            sleep_seconds = min(nextrun, default_interval)
        else:
            sleep_seconds = default_interval

        print(f"Next run scheduled in {sleep_seconds} seconds")
        if sleep_seconds <= 0:
            continue
        remaining = int(sleep_seconds)
        total = remaining
        while remaining > 0:
            filled = int((total - remaining) / total * 60) if total else 60
            bar = "#" * filled + "-" * (60 - filled)
            print(f"\rNext run in {remaining:>4}s [{bar}]", end="", flush=True)
            time.sleep(1)
            remaining -= 1
        print()
        freshLoad = False  # placeholder for any state reset needed before next run


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Schedule main() using config.RUN_INTERVAL or the nextrun value returned
    run_scheduler()
