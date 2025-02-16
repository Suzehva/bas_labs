from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
import json


def scrape_nzdpu(sector: str, country: str) -> list[str]:
    """ """
    return ["Amazon", "Delta Airlines", "DAIN"]


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
