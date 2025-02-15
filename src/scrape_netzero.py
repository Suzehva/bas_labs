from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

def scrape_netzero_data(company_name: str) -> str:
    """
    Scrapes Net Zero data for a given company and returns the content.
    
    Args:
        company_name (str): Name of the company to search for
        
    Returns:
        str: Content of the downloaded JSON file
    """
    
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    download_dir = os.path.join(os.getcwd(), "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    chrome_options.add_experimental_option(
        "prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "profile.default_content_settings.popups": 0
        }
    )

    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()

    try:
        driver.get("https://zerotracker.net/")
        time.sleep(2)

        search_box = driver.find_element(By.CLASS_NAME, "table-header-search-input")
        search_box.send_keys(company_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        wait = WebDriverWait(driver, 10)
        first_link = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//tbody[@class='main-tbody']/tr[@class='table-border-tr']//td/a")
        ))
        
        driver.execute_script("arguments[0].scrollIntoView(true);", first_link)
        time.sleep(1)
        
        driver.execute_script("arguments[0].click();", first_link)
        time.sleep(3)
        
        # Download data
        download_buttons = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//button[contains(text(), 'Download Data')]")
        ))
        
        if len(download_buttons) >= 2:
            download_button = download_buttons[1]
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
            time.sleep(2)
            
            driver.execute_script("arguments[0].click();", download_button)
            time.sleep(5)  # Wait for download
            
            # Get most recently downloaded file
            downloaded_files = [f for f in os.listdir(download_dir) if f.endswith('.txt')]
            if downloaded_files:
                downloaded_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
                latest_file = downloaded_files[0]
                
                # Read and return file contents
                with open(os.path.join(download_dir, latest_file), 'r') as f:
                    return f.read()
                    
        else:
            raise Exception(f"Found only {len(download_buttons)} download buttons")
    except:
        print('was unable to process request')
        return None
            
    finally:
        driver.quit()
        
    return None

if __name__ == "__main__":
    # Get company name from command line arguments
    if len(sys.argv) > 1:
        company_name = sys.argv[1]
        try:
            content = scrape_netzero_data(company_name)
            #print(content)  # This will be returned to JavaScript
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: No company name provided", file=sys.stderr)
        sys.exit(1)