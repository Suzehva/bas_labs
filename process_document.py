from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from typing import List, Dict, Set
import glob
import pandas as pd
import re
import os
import numpy as np
import json
import requests
import tempfile
from tqdm import tqdm
from urllib.parse import unquote
import io

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.base_directory = os.path.abspath(".")
        self.csv_directory = os.path.join(self.base_directory, "spreadsheet")
        self.pdf_cache_dir = os.path.join(self.base_directory, "pdf_cache")
        os.makedirs(self.pdf_cache_dir, exist_ok=True)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", "? ", "! "],
            chunk_size=2000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def download_pdf(self, url: str) -> str:
        try:
            safe_filename = re.sub(r'[^a-zA-Z0-9]', '_', url) + '.pdf'
            cache_path = os.path.join(self.pdf_cache_dir, safe_filename)
            if os.path.exists(cache_path):
                return cache_path
            
            # Download first
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Cache it
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return cache_path
        except Exception as e:
            print(f"Error downloading PDF from {url}: {str(e)}")
            return None

    def process_pdf_url(self, url: str) -> List[Dict]:
        pdf_path = self.download_pdf(url)
        if not pdf_path:
            return []
        
        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            chunks = []
            
            for page in pages:
                text = page.page_content
                if not text.strip():
                    continue
                
                chunks.append({
                    "content": self.clean_text(text),
                    "metadata": {
                        "source_url": url,
                        "source_type": "pdf",
                        "page": page.metadata.get("page", 0)
                    }
                })
            
            return chunks
        except Exception as e:
            print(f"Error processing PDF {url}: {str(e)}")
            return []

    def process_csv(self, file_path: str) -> List[Dict]:
        df = pd.read_csv(file_path)
        chunks = []
        pdf_urls = set()
        
        for idx, row in df.iterrows():
            row_text = []
            for col, val in row.items():
                if pd.notna(val):
                    row_text.append(f"{col}: {val}")
                    if isinstance(val, str) and val.lower().endswith('.pdf'):
                        pdf_urls.add(val)
            
            content = " | ".join(row_text)
            chunks.append({
                "content": content,
                "metadata": {
                    "source_file": os.path.basename(file_path),
                    "source_type": "csv",
                    "row_index": idx,
                    "columns": list(df.columns)
                }
            })

        print(f"\nProcessing {len(pdf_urls)} PDFs from {os.path.basename(file_path)}...")
        for url in tqdm(pdf_urls):
            pdf_chunks = self.process_pdf_url(url)
            chunks.extend(pdf_chunks)
            if pdf_chunks:
                print(f"Added {len(pdf_chunks)} chunks from {url}")
        
        return chunks

    def load_csvs(self) -> List[Dict]:
        all_chunks = []
        csv_files = glob.glob(os.path.join(self.csv_directory, "*.csv"))
        
        for csv_path in csv_files:
            try:
                chunks = self.process_csv(csv_path)
                all_chunks.extend(chunks)
                print(f"Processed {os.path.basename(csv_path)}: {len(chunks)} total chunks")
            except Exception as e:
                print(f"Error processing {csv_path}: {str(e)}")
        
        return all_chunks

    def create_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        embeddings_list = []
        total = len(chunks)
        
        texts = [chunk["content"] if isinstance(chunk, dict) else chunk.page_content for chunk in chunks]
        
        print(f"Creating embeddings for {total} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            content = chunk["content"] if isinstance(chunk, dict) else chunk.page_content
            metadata = chunk["metadata"] if isinstance(chunk, dict) else chunk.metadata
            
            embeddings_list.append({
                "content": content,
                "embedding": embedding.tolist(), 
                "metadata": metadata
            })
            
        return embeddings_list

    def save_embeddings(self, embeddings_data: List[Dict], output_dir: str = "embeddings"):
        os.makedirs(output_dir, exist_ok=True)
        embeddings_by_source = {}
    
        for item in embeddings_data:
            source = item["metadata"].get("source_url", item["metadata"].get("source_file"))
            if source not in embeddings_by_source:
                embeddings_by_source[source] = []
            embeddings_by_source[source].append(item)
        
        for source, items in embeddings_by_source.items():
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', source)
            output_file = os.path.join(output_dir, f"{safe_name}_embeddings.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            print(f"Saved embeddings for {source} to {output_file}")

def main():
    processor = DocumentProcessor()
    print("Starting document processing...")
    all_chunks = processor.load_csvs()
    print(f"\nCreated {len(all_chunks)} total chunks")
    print("1) Created chunks. Now creating embeddings...")
    embeddings_data = processor.create_embeddings(all_chunks)
    print(f"2) Embeddings created for {len(embeddings_data)} total chunks")
    processor.save_embeddings(embeddings_data)
    print("3) Embeddings saved to ./embeddings directory")
    return embeddings_data

if __name__ == "__main__":
    main()