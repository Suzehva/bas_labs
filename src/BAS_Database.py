import iris
import time
import os
import pandas as pd
from sqlalchemy import create_engine

from sentence_transformers import SentenceTransformer
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv


class BAS_Database:
    def __init__(self):
        ### Vector Database Setup
        username = "demo"
        password = "demo"
        hostname = os.getenv("IRIS_HOSTNAME", "localhost")
        port = "1972"
        namespace = "USER"
        CONNECTION_STRING = f"{hostname}:{port}/{namespace}"

        self.conn = iris.connect(CONNECTION_STRING, username, password)
        self.cursor = self.conn.cursor()

        # Tables
        self.un_table = "BASLABS.UNClimateAction"
        self.report_table = "BASLABS.ClimateReportsEmbed"

        # Embeddings
        self.embed_minilm = SentenceTransformer("all-MiniLM-L6-v2")

        load_dotenv()
        NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
        self.embed_nvidia = NVIDIAEmbeddings(
            model="nvidia/llama-3.2-nv-embedqa-1b-v2",
            api_key=NVIDIA_API_KEY,
            truncate="NONE",
        )

    def get_un_initative(self, search_query, n=5):
        """
        Retrieve the top N initiatives from the database based on the search query.
        This method connects to the database if not already connected, encodes the search query
        into a search vector using the MiniLM model, and retrieves the top N initiatives from the
        database ordered by the similarity of their description vectors to the search vector.
        Args:
            search_query (str): The search query to find relevant initiatives.
            n (int, optional): The number of top initiatives to retrieve. Defaults to 5.
        Returns:
            list: A list of dictionaries, each containing the title, summary, and description
                  of an initiative.
        """

        if not self.conn:
            self.connect()
        search_vector = self.embed_minilm.encode(
            search_query, normalize_embeddings=True
        ).tolist()
        sql = f"""
            SELECT TOP ? title, summary, description
            FROM {self.un_table}
            ORDER BY VECTOR_DOT_PRODUCT(description_vector, TO_VECTOR(?)) DESC
        """
        self.cursor.execute(sql, [n, str(search_vector)])
        results = self.cursor.fetchall()
        return [
            dict(title=row[0], summary=row[1], description=row[2]) for row in results
        ]

    def get_report_section(self, search_query, n=5):
        if not self.conn:
            self.connect()
        search_vector = self.embed_nvidia.embed_query(search_query)
        sql = f"""
            SELECT TOP ? company_name, source_url, year, page, content
            FROM {self.report_table}
            ORDER BY VECTOR_DOT_PRODUCT(content_embedding, TO_VECTOR(?)) DESC
        """
        self.cursor.execute(sql, [n, str(search_vector)])
        results = self.cursor.fetchall()
        return [
            dict(
                company_name=row[0],
                source_url=row[1],
                year=str(row[2]),
                page=str(row[3]),
                content=row[4],
            )
            for row in results
        ]


# Hi! I'm a tech company in united states looking to reduce our emissions. We specialize in software development and run quite big data centers
