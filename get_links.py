import pandas as pd
import re
import os
import glob
from typing import Set
from urllib.parse import unquote

class LinkExtractor:
    def __init__(self):
        self.base_directory = os.path.abspath(".")
        self.csv_directory = os.path.join(self.base_directory, "spreadsheet")
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )

    def is_pdf_link(self, url: str) -> bool:
        decoded_url = unquote(url)
        return decoded_url.lower().endswith('.pdf')

    def extract_links_from_csv(self, file_path: str) -> Set[str]:
        df = pd.read_csv(file_path)
        links = set()
        for column in df.columns:
            df[column] = df[column].astype(str)
        
        for column in df.columns:
            cell_links = df[column].str.findall(self.url_pattern)
            for cell_link_list in cell_links:
                pdf_links = {link for link in cell_link_list if self.is_pdf_link(link)}
                links.update(pdf_links)
        
        return links

    def extract_all_links(self) -> Set[str]:
        all_links = set()
        csv_files = glob.glob(os.path.join(self.csv_directory, "*.csv"))
        
        for csv_path in csv_files:
            try:
                file_links = self.extract_links_from_csv(csv_path)
                all_links.update(file_links)
            except Exception as e:
                print(f"Error processing {csv_path}: {str(e)}")
        
        output_file = os.path.join(self.csv_directory, "pdf_links.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            for link in sorted(all_links):
                f.write(f"{link}\n")
        
        print(f"Found {len(all_links)} unique PDF links")
        print(f"Links saved to {output_file}")
        return all_links

def main():
    extractor = LinkExtractor()
    extractor.extract_all_links()

if __name__ == "__main__":
    main()