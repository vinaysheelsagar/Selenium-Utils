"""This module contains general utility functions for selenium"""

import os
import re
import shutil
import platform
from enum import Enum
from zipfile import ZipFile
from pathlib import Path
import requests
from selenium import webdriver


class Browser(Enum):
    "browser names for selenium"
    FIREFOX="firefox"
    CHROME="chrome"
    EDGE="edge"


def _driver_name_regex(browser: Browser):
    "returns the regex pattern for the driver name"
    match browser:
        case Browser.FIREFOX:
            return r"geckodriver(.*).exe"
        case Browser.CHROME:
            return r"chromedriver(.*).exe"
        case Browser.EDGE:
            return r"msedgedriver(.*).exe"
        case _:
            raise ValueError("Unsupported browser")


def _is_driver_present(driver_download_dir, browser: Browser):

    dir_files = os.listdir(driver_download_dir)

    for file in dir_files:
        if re.search(_driver_name_regex(browser), file):
            return True
    return False


def _fix_architecture_info(info: tuple):
    platform_info = list(info)
    if "windows" in platform_info[1].lower():
        platform_info[1] = "windows"
        platform_info = tuple(platform_info)
    return tuple(platform_info)


def _download_driver(
    driver_download_dir: str | os.PathLike,
    browser: Browser,
):

    driver_urls = None

    match browser:
        case Browser.FIREFOX:
            driver_urls = {
                ("32bit", "windows"): {
                    "url": "https://github.com/mozilla/geckodriver/releases/download"
                        "/v0.34.0/geckodriver-v0.34.0-win32.zip",
                    "is_zip": True
                },
                ("64bit", "windows"): {
                    "url": "https://github.com/mozilla/geckodriver/releases/download"
                        "/v0.34.0/geckodriver-v0.34.0-win64.zip",
                    "is_zip": True
                },
            }
        case Browser.CHROME:
            _32bit_url = None
            _64bit_url = None

            response = requests.get("https://googlechromelabs.github.io/"
            "chrome-for-testing/last-known-good-versions-with-downloads.json", timeout=60)
            data = response.json()

            platform_urls = data["channels"]["Stable"]["downloads"]["chromedriver"]
            for info in platform_urls:
                if info["platform"] == "win32":
                    _32bit_url = info["url"]
                elif info["platform"] == "win64":
                    _64bit_url = info["url"]

            driver_urls = {
                ("32bit", "windows"):{
                    "url": _32bit_url,
                    "is_zip": True
                },
                ("64bit", "windows"): {
                    "url": _64bit_url,
                    "is_zip": True
                },
            }

    platform_info = _fix_architecture_info(platform.architecture())

    driver_url = driver_urls[platform_info]["url"]
    response = requests.get(driver_url, timeout=60)

    filename = os.path.basename(driver_url)

    if driver_urls[platform_info]["is_zip"]:
        # Download the zip file
        zip_path = os.path.join(driver_download_dir, filename)
        with open(zip_path, 'wb') as file:
            file.write(response.content)

        # Extract the driver from the zip file
        driver_path = None

        with ZipFile(filename, 'r') as zip_ref:
            files = zip_ref.namelist()
            for file in files:
                if re.search(_driver_name_regex(browser), file):
                    driver_path = os.path.join(driver_download_dir, file)
                    zip_ref.extract(member=file, path=driver_download_dir)

                    extracted_filename = os.path.basename(file)

                    if file != extracted_filename:
                        src_path = os.path.join(driver_download_dir, file)
                        dst_path = os.path.join(driver_download_dir, extracted_filename)
                        os.rename(src_path, dst_path)

                        first_dir = Path(file).parts[0]
                        shutil.rmtree(os.path.join(driver_download_dir, first_dir))
                    break

        assert driver_path is not None, "no matching .exe file found in downloaded zip file"

        # Remove the downloaded zip file
        try:
            os.remove(zip_path)
        except FileNotFoundError:
            print("Warning: Something might be wrong with availability"
            " of the driver. Please check.")


def _verify_driver(driver_download_dir: str | os.PathLike, browser: Browser):

    if not _is_driver_present(driver_download_dir, browser):
        print('Driver not present. Downloading...')
        _download_driver(driver_download_dir, browser)


def init_driver(
    browser: Browser = Browser.FIREFOX,
    driver_download_dir: str = None,
    user_data_dir: str = None,
    download_dir: str = None,
    headless: bool = False,
) -> webdriver:

    driver_path = None
    driver = None
    options = None
    service = None

    if driver_download_dir is None:
        driver_download_dir = os.getcwd()

    # safeguard
    match browser:
        case Browser.EDGE:
            raise NotImplementedError("Service for Edge browser is not implemented yet.")

    # download driver if not already downloaded
    _verify_driver(driver_download_dir, browser)

    # handling data_path
    files = os.listdir(driver_download_dir)
    for file in files:
        if re.search(_driver_name_regex(browser), file):
            driver_path = os.path.join(driver_download_dir, file)
            break

    assert driver_path is not None, "No driver executable found."

    # Setup Options
    match browser:
        case Browser.FIREFOX:
            from selenium.webdriver.firefox.options import Options

            options = Options()
            if headless:
                options.headless = True
            if user_data_dir:
                options.add_argument("-profile")
                options.add_argument(user_data_dir)
            if download_dir:
                options.set_preference("browser.download.folderList", 2)
                options.set_preference("browser.download.dir", download_dir)
                options.set_preference("browser.download.useDownloadDir", True)
                options.set_preference("browser.download.manager.showWhenStarting", False)
                options.set_preference(
                    "browser.helperApps.neverAsk.saveToDisk",
                    "application/pptx, "
                    "application/csv, "
                    "application/ris, "
                    "text/csv, "
                    "image/png, "
                    "application/pdf, "
                    "text/html, "
                    "text/plain, "
                    "application/zip, "
                    "application/x-zip, "
                    "application/x-zip-compressed, "
                    "application/download, "
                    "application/octet-stream",
                )

        case Browser.CHROME:
            from selenium.webdriver.chrome.options import Options

            options = Options()
            if headless:
                options.add_argument("--headless")
            if user_data_dir:
                if not os.path.exists(user_data_dir):
                    raise ValueError("Provided user_data_dir does not exist.")

                options.add_argument(f'--user-data-dir={user_data_dir}')
            if download_dir:
                prefs = {'download.default_directory' : download_dir}
                options.add_experimental_option('prefs', prefs)

    # Setup Service
    match browser:
        case Browser.FIREFOX:
            from selenium.webdriver.firefox.service import Service

            service = Service(executable_path=driver_path, log_output=os.devnull)

        case Browser.CHROME:
            from selenium.webdriver.chrome.service import Service

            service = Service(executable_path=driver_path, log_output=os.devnull)

    assert options is not None, "Options are not found."
    assert service is not None, "Service is not found."

    # Initialize Driver
    match browser:
        case Browser.FIREFOX:
            from selenium.webdriver import Firefox

            driver = Firefox(service=service, options=options)

        case Browser.CHROME:
            from selenium.webdriver import Chrome

            driver = Chrome(service=service, options=options)

    assert driver is not None, "No webdriver generated."

    driver.maximize_window()

    return driver

# TODO: to be completed
def get_profile_path(browser: Browser) -> str:
    "returns the path to the profile"

    profile_path = None

    platform_info = _fix_architecture_info(platform.architecture())

    match browser:
        case Browser.FIREFOX:
            if platform_info[1] == "windows":
                profiles_dir = os.path.join(
                    os.path.expanduser("~"),
                    "AppData",
                    "Roaming",
                    "Mozilla",
                    "Firefox",
                    "Profiles",
                )
                profile_name = None
                for folder in os.listdir(profiles_dir):
                    regex_pattern = r"(.*).default-release"
                    match = re.search(regex_pattern, folder)
                    if match is not None:
                        profile_name = folder
                        break
                assert profile_name is not None, "No profile found."
                profile_path = os.path.join(profiles_dir, profile_name)

        case Browser.CHROME:
            if platform_info[1] == "windows":
                profile_path = os.path.join(
                    os.path.expanduser("~"),
                    "AppData",
                    "Local",
                    "Google",
                    "Chrome",
                    "User Data",
                    "Default",
                )

                assert os.path.exists(profile_path), "No Chrome profile found."

    return profile_path
