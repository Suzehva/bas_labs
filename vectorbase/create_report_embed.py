#### PACKAGES

import pandas as pd
import numpy as np
import iris
import time
import os

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv

from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_iris import IRISVector
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyMuPDFLoader

import requests
from io import BytesIO
import time
import multiprocessing


# This function will be executed in the subprocess
def create_loader(url):
    return PyPDFLoader(url)  # PyPDFLoader instantiation inside timeout


def run_with_timeout(func, timeout, *args, **kwargs):
    # Start a new process for the function
    process = multiprocessing.Process(target=func, args=args, kwargs=kwargs)
    process.start()
    process.join(timeout)  # Wait for the process to finish within the timeout

    if process.is_alive():
        process.terminate()  # Forcefully terminate if still running after timeout
        print(f"Timeout occurred for {func.__name__}")
        return None
    return func(*args, **kwargs)  # Return the result if no timeout


# The main logic of your program
def get_docs(url):
    try:
        start = time.time()
        loader = run_with_timeout(
            create_loader, TIMEOUT, url
        )  # Timeout on PyPDFLoader instantiation
        if loader is None:
            return None  # Stop if timeout occurs
        end = time.time()
        print(f"Loading PDF took {(end - start):.2f} s")

        documents = loader.load()
        docs = text_splitter.split_documents(documents)
        return docs
    except Exception as e:
        print(f"Error loading PDF: {e}")
        return None


def get_df(docs, company_name, year, pdf_url):
    data = [
        {
            "page": doc.metadata["page"],
            "total_pages": doc.metadata["total_pages"],
            "content": doc.page_content,
        }
        for doc in docs
    ]

    doc_df = pd.DataFrame(data)
    doc_df["company_name"] = company_name
    doc_df["year"] = year
    doc_df["source_url"] = pdf_url
    doc_embeddings = client.embed_documents(doc_df["content"].tolist())
    doc_df["content_embedding"] = doc_embeddings
    return doc_df


def insert_df(doc_df):
    sql = f"""
    INSERT INTO {embedTableName}
    (company_name, source_url, year, page, total_pages, content, content_embedding) 
    VALUES (?, ?, ?, ?, ?, ?, TO_VECTOR(?))
    """

    data = [
        (
            row["company_name"],
            row["source_url"],
            row["year"],
            row["page"],
            row["total_pages"],
            row["content"],
            str(row["content_embedding"]),
        )
        for index, row in doc_df.iterrows()
    ]
    results = cursor.executemany(sql, data)


# Ensure the multiprocessing code runs only when executed directly
if __name__ == "__main__":

    ##### PARAMETERS
    CREATE_TABLE = True
    TIMEOUT = 5

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", "? ", "! "],
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )

    # Load environment variables from .env file
    load_dotenv()

    # Access variables
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

    client = NVIDIAEmbeddings(
        model="nvidia/llama-3.2-nv-embedqa-1b-v2",
        api_key=NVIDIA_API_KEY,
        truncate="NONE",
    )

    ### Vector Database Setup
    username = "demo"
    password = "demo"
    hostname = os.getenv("IRIS_HOSTNAME", "localhost")
    port = "1972"
    namespace = "USER"
    CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
    print(CONNECTION_STRING)

    conn = iris.connect(CONNECTION_STRING, username, password)
    cursor = conn.cursor()

    embedTableName = "BASLABS.ClimateReportsEmbed"
    tableDefinition = """
    (
    company_name VARCHAR(255), 
    source_url VARCHAR(1000),
    year INT,
    page INT,
    total_pages INT,
    content VARCHAR(5000), 
    content_embedding VECTOR(DOUBLE, 2048)
    )
    """

    if CREATE_TABLE:
        try:
            cursor.execute(f"DROP TABLE {embedTableName}")
        except:
            pass
        cursor.execute(f"CREATE TABLE {embedTableName} {tableDefinition}")

    # OPEN
    link_df = pd.read_csv("data/tech_reports.csv")

    i = 0
    for index, row in link_df.iterrows():

        company_name = row["company_name"]
        year = row["year"]
        source_url = row["report_url"]
        print("Processing", company_name)

        docs = get_docs(source_url)
        if docs == None:
            continue
        print(f"Found {len(docs)} docs")
        doc_df = get_df(docs, company_name, year, source_url)
        insert_df(doc_df)

        i += 1
        if i == 10:
            break
