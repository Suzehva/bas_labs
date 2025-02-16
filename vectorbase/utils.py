import requests
import base64
from pathlib import Path
import tempfile
from typing import Union, Optional
import logging

def get_prompt(prompt_name, placeholders):
    with open(f"{prompt_name}") as f:
        prompt = f.read()

    for ph in placeholders:
        prompt = prompt.replace(ph[0], ph[1])

    return prompt

def clean_company_name(company_name):
    return ''.join(e for e in company_name.lower().replace(" ", "_") if e.isalnum())

def download_and_process_pdf(company_name, report: dict) -> Optional[str]:
    """
    Download a PDF from a URL and convert it to base64 for Gemini API
    
    Args:
        pdf_url (str): URL of the PDF file
        
    Returns:
        Optional[str]: Base64 encoded PDF content or None if failed
    """
    try:
        # Download the PDF
        try:
            response = requests.get(report["pdf_link"], stream=True, timeout=5)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            logging.error(f"Timed out downloading PDF for {company_name}")
            return None
        
        report_name = ''.join(e for e in company_name.lower().replace(" ", "_") if e.isalnum())
        
        pdf_path = Path(f"pipeline/data/reports/{report_name}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download the PDF
        with open(pdf_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print("Saved report to", pdf_path)
        return str(pdf_path)
    except:
        return None