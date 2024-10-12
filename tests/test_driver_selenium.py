import os
import time
import uuid
# TODO: Fix import path
import shutil
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def test_is_driver_present_firefox():
    print(os.getcwd())
    assert _is_driver_present(os.getcwd(), Browser.FIREFOX), "Could not detect geckodriver"


def test_is_driver_present_chrome():
    print(os.getcwd())
    assert _is_driver_present(os.getcwd(), Browser.CHROME), "Could not detect chromedriver"


# def init_driver(
#     browser: Browser = Browser.FIREFOX,
#     driver_download_dir: str = None,
#     user_data_dir: str = None,
#     download_dir: str = None,
#     headless: bool = False,
# ) -> webdriver:
def test_init_driver_firefox():
    driver = init_driver(browser=Browser.FIREFOX)
    assert driver is not None, "No webdriver generated."
    driver.quit()


def test_driver_download_dir_firefox():
    download_dir = os.path.join(os.getcwd(), "download_test", str(uuid.uuid4()))
    os.makedirs(download_dir, exist_ok=True)

    driver = init_driver(
        browser=Browser.FIREFOX,
        download_dir=download_dir)

    try:
        url = "https://imarcservices-my.sharepoint.com/:t:/g/personal/vinay_sagar_imarc_in/EacNp-kyR6hIhiXAbN9CC5IBj0tHaFMLmUPWC1E1JHGbVg?e=I9XfLU"
        driver.get(url)
        driver.find_element(By.XPATH, '//*[@id="downloadCommand"]').click()

        wait_limit = 60
        while len(os.listdir(download_dir)) == 0:
            time.sleep(1)
            wait_limit = wait_limit - 1
            if wait_limit <= 0:
                break
    except Exception:
        pass
    finally:
        driver.quit()

    files = os.listdir(download_dir)
    shutil.rmtree(download_dir)

    assert len(files) > 0, "Download directory does not exist."


def test_download_dir_chrome():
    download_dir = os.path.join(os.getcwd(), "download_test", str(uuid.uuid4()))
    os.makedirs(download_dir, exist_ok=True)

    driver = init_driver(
        browser=Browser.CHROME,
        download_dir=download_dir)
    try:
        url = "https://imarcservices-my.sharepoint.com/:t:/g/personal/vinay_sagar_imarc_in/EacNp-kyR6hIhiXAbN9CC5IBj0tHaFMLmUPWC1E1JHGbVg?e=I9XfLU"
        driver.get(url)
        driver.find_element(By.XPATH, '//*[@id="downloadCommand"]').click()

        wait_limit = 60
        while len(os.listdir(download_dir)) == 0:
            time.sleep(1)
            wait_limit = wait_limit - 1
            if wait_limit <= 0:
                break

    except Exception:
        pass
    finally:
        driver.quit()

    files = os.listdir(download_dir)
    shutil.rmtree(download_dir)

    assert len(files) > 0, "Download directory does not exist."


# def test_driver_download_dir_firefox():
    # assert download_dir in driver.capabilities["moz:profile"], "Download directory not set correctly."


def test_user_dir_firefox():
    user_dir = get_profile_path(Browser.FIREFOX)
    driver = init_driver(Browser.FIREFOX, user_data_dir=user_dir)
    print(driver.capabilities)
    assert driver.capabilities["moz:profile"] == user_dir, "profile path not set"
    driver.quit()


def test_init_driver_chrome():
    driver = init_driver(browser=Browser.CHROME)
    assert driver is not None, "No webdriver generated."
    driver.quit()


def test_init_driver_edge():
    try:
        driver = init_driver(browser=Browser.EDGE)
        driver.quit()
    except Exception as e:
        assert isinstance(e, NotImplementedError), "No driver generated for Edge browser."


# # TODO: to be completed
# def get_profile_path(browser: Browser) -> str:
#     "returns the path to the profile"
#     profile_path = None
#     return profile_path


def get_profile_firefox():
    path = None
    path = get_profile_path(Browser.FIREFOX)
    assert path is not None, "profile_firefox not found."
    print(path)


def get_profile_chrome():
    path = None
    path = get_profile_path(Browser.CHROME)
    assert path is not None, "profile_firefox not found."
    print(path)


def profile_path_working_firefox():
    url = "https://books.zoho.com/app/653945843#/timesheet/projects/957216000012513009"
    profile_path = get_profile_path(Browser.FIREFOX)
    driver = init_driver(
        browser=Browser.FIREFOX,
        user_data_dir=profile_path,
    )
    driver.get(url)
    title = driver.title
    driver.quit()
    assert "Timesheet" in title, "Page title does not match expected."


def profile_path_working_chrome():
    url = "https://books.zoho.com/app/653945843#/timesheet/projects/957216000012513009"
    profile_path = get_profile_path(Browser.CHROME)
    driver = init_driver(
        browser=Browser.CHROME,
        user_data_dir=profile_path,
    )
    driver.get(url)
    title = driver.title
    driver.quit()
    assert "Timesheet" in title, "Page title does not match expected."
