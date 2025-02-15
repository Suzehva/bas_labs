from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
from typing import List, Dict
import glob
import pandas as pd
import re

load_dotenv()

class DocumentProcessor:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.pdf_directory = os.path.join(base_directory, "pdfs")
        self.csv_directory = os.path.join(base_directory, "spreadsheet")
        
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

    def load_pdfs(self) -> List[Dict]:
        all_chunks = []
        if os.path.exists(self.pdf_directory):
            for pdf_path in glob.glob(f"{self.pdf_directory}/*.pdf"):
                loader = PyPDFLoader(pdf_path)
                pages = loader.load()
                
                for page in pages:
                    text = page.page_content
                    paragraphs = self.text_splitter.split_text(text)
                    
                    for para in paragraphs:
                        if len(self.clean_text(para)) < 50:  # Skip very short paragraphs
                            continue
                            
                        all_chunks.append({
                            "content": self.clean_text(para),
                            "metadata": {
                                "source_file": os.path.basename(pdf_path),
                                "source_type": "pdf",
                                "page": page.metadata.get("page", 0)
                            }
                        })
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
    base_dir = "c:/Users/Bubble/Desktop/Treehacks2025/bas_labs"
    processor = DocumentProcessor(base_dir)
    
    print("Starting document processing...")
    # case: pdfs
    pdf_chunks = processor.load_pdfs()
    print(f"Created {len(pdf_chunks)} chunks from PDFs")

    # default: csvs
    csv_chunks = processor.load_csvs()
    print(f"Created {len(csv_chunks)} chunks from CSVs")
    
    all_chunks = pdf_chunks + csv_chunks
    print("1) Created chunks. Now creating embeddings...")
    embeddings_data = processor.create_embeddings(all_chunks)
    print(f"2) Embeddings created for {len(embeddings_data)} total chunks")
    return embeddings_data

if __name__ == "__main__":
    main()