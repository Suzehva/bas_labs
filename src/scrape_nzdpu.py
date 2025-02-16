from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import json
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


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

AVAILABLE_SECTORS = [
    "Consumer Goods",
    "Extractives & Minerals Processing",
    "Financials",
    "Food & Beverage",
    "Health Care",
    "Infrastructure",
    "Renewable Resources & Alternative Energy",
    "Resource Transformation",
    "Services",
    "Technology & Communications",
    "Transportation",
    "Not Classified by SICS",
]


def match_sector_with_available(sector: str) -> str:
    prompt = f"""
    Classify the following sector into one of the following categories: {', '.join(AVAILABLE_SECTORS)}.
    If it doesn't match, return None.
    Input: {sector}
    Output: 
    """
    # Make the API call to Gemini (using the OpenAI wrapper as an example for now)
    model = genai.generativeModel(
        "gemini-2.0-flash-exp",
    )
    response = model.generate_content(prompt)
    print(response)
    return response.text.strip()


def match_sector_with_available_two(sector: str) -> str:
    match = difflib.get_close_matches(sector, AVAILABLE_SECTORS, n=0.8, cutoff=0.5)
    return match[0] if match else None


def scrape_nzdpu(sector: str, country: str) -> list[str]:
    """ """
    if sector not in AVAILABLE_SECTORS:
        sector = match_sector_with_available(sector)
        sector = match_sector_with_available_two(sector)
        if sector is None:
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
    # nzdpu_url += f"&jurisdiction={country}" # TODO: sort by country

    try:
        driver.get(nzdpu_url)
        time.sleep(2)

        wait = WebDriverWait(driver, 10)
        table = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//table[contains(@class, 'MuiTable-root')]//tbody[contains(@class, 'MuiTableBody-root')]",
                )
            )
        )

        # Get rows from the table we already found
        rows = table.find_elements(By.TAG_NAME, "tr")
        company_names = []

        # Get first 7 rows
        for row in rows[:7]:
            try:
                # Get first cell of each row (company name cell)
                name_cell = row.find_element(By.TAG_NAME, "td")
                name = name_cell.text.strip()
                if name:
                    company_names.append(name)
            except:
                continue

        return company_names[:7]

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


"""
hi! I am a software company based out of chicago; can you help me find how I can stop climate change?

"""
