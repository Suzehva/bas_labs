from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from typing import List, Dict
import glob
import pandas as pd
import re
import os

load_dotenv()

class DocumentProcessor:
    def __init__(self):
        self.base_directory = os.path.abspath(".")
        self.csv_directory = os.path.join(self.base_directory, "spreadsheet")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", "? ", "! "],
            chunk_size=2000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False
        )
        self.embeddings = OpenAIEmbeddings()

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def process_csv(self, file_path: str) -> List[Dict]:
        df = pd.read_csv(file_path)
        chunks = []
        for idx, row in df.iterrows():
            content = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            
            chunks.append({
                "content": content,
                "metadata": {
                    "source_file": os.path.basename(file_path),
                    "source_type": "csv",
                    "row_index": idx,
                    "columns": list(df.columns)
                }
            })
        return chunks

    def load_csvs(self) -> List[Dict]:
        all_chunks = []
        csv_files = glob.glob(f"{self.csv_directory}/*.csv")
        
        for csv_path in csv_files:
            try:
                chunks = self.process_csv(csv_path)
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {csv_path}: {str(e)}")
        
        return all_chunks

    def create_embeddings(self, chunks: List[Dict]):
        embeddings_list = []
        for chunk in chunks:
            content = chunk["content"] if isinstance(chunk, dict) else chunk.page_content
            metadata = chunk["metadata"] if isinstance(chunk, dict) else chunk.metadata
            
            embedding = self.embeddings.embed_query(content)
            embeddings_list.append({
                "content": content,
                "embedding": embedding,
                "metadata": metadata
            })
        return embeddings_list

def main():
    processor = DocumentProcessor()
    print("Starting document processing...")
    # default: csvs
    all_chunks = processor.load_csvs()
    print(f"Created {len(all_chunks)} chunks from CSVs")
    print("1) Created chunks. Now creating embeddings...")
    embeddings_data = processor.create_embeddings(all_chunks)
    print(f"2) Embeddings created for {len(embeddings_data)} total chunks")
    return embeddings_data

if __name__ == "__main__":
    main()