from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import json


# url https://nzdpu.com/companies?sicsSector=Consumer%20Goods


sics_sector_urls = {
    "Consumer Goods": "https://nzdpu.com/companies?sicsSector=Consumer%20Goods",
    "Extractives & Minerals Processing": "https://nzdpu.com/companies?sicsSector=Extractives%20%26%20Minerals%20Processing",
    "Financials": "https://nzdpu.com/companies?sicsSector=Financials",
    "Food & Beverage": "https://nzdpu.com/companies?sicsSector=Food%20%26%20Beverage",
    "Health Care": "https://nzdpu.com/companies?sicsSector=Health%20Care",
    "Infrastructure": "https://nzdpu.com/companies?sicsSector=Infrastructure",
    "Renewable Resources & Alternative Energy": "https://nzdpu.com/companies?sicsSector=Renewable%20Resources%20%26%20Alternative%20Energy",
    "Resource Transformation": "https://nzdpu.com/companies?sicsSector=Resource%20Transformation",
    "Services": "https://nzdpu.com/companies?sicsSector=Services",
    "Technology & Communications": "https://nzdpu.com/companies?sicsSector=Technology%20%26%20Communications",
    "Transportation": "https://nzdpu.com/companies?sicsSector=Transportation",
    "Not Classified by SICS": "https://nzdpu.com/companies?sicsSector=Not%20Classified%20by%20SICS",
}


def scrape_nzdpu(sector: str, country: str) -> list[str]:
    """ """
    if sector not in sics_sector_urls:
        return []

    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "profile.default_content_settings.popups": 0,
        },
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    country = country.capitalize()
    nzdpu_url = sics_sector_urls[sector]
    nzdpu_url += f"&jurisdiction={country}"

    try:
        driver.get(nzdpu_url)
        time.sleep(2)

        wait = WebDriverWait(driver, 10)
        table = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//tbody[@class='MuiTableBody-root']")
            )
        )

        # MuiTableBody-root
    except:
        # return ["Amazon", "Delta Airlines", "DAIN"]
        return []


if __name__ == "__main__":
    # Get company name from command line arguments
    if len(sys.argv) > 2:
        sector = sys.argv[1]
        country = sys.argv[2]
        try:
            content = scrape_nzdpu(sector, country)
            print(json.dumps(content))
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Not enough arguments provided", file=sys.stderr)
        sys.exit(1)
