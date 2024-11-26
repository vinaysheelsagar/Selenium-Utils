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


def _fix_architecture_info(info: tuple):
    platform_info = list(info)
    if "windows" in platform_info[1].lower():
        platform_info[1] = "windows"
        platform_info = tuple(platform_info)
    return tuple(platform_info)


def init_driver(
    browser: Browser = Browser.FIREFOX,
    user_data_dir: str = None,
    download_dir: str = None,
    headless: bool = False,
) -> webdriver:

    driver = None
    options = None
    service = None

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

            service = Service(log_output=os.devnull)

        case Browser.CHROME:
            from selenium.webdriver.chrome.service import Service

            service = Service(log_output=os.devnull)

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


def get_profile_path(browser: Browser) -> str:
    "returns the path to the profile"

    if browser == Browser.EDGE:
        raise ValueError("support for profile path hasn't been added yet...")

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
