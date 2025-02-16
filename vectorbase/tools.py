import iris
import time
import os
import pandas as pd
from sqlalchemy import create_engine


class BAS_DATABASE:
    def __init__(self):
        ### Vector Database Setup
        username = "demo"
        password = "demo"
        hostname = os.getenv("IRIS_HOSTNAME", "localhost")
        port = "1972"
        namespace = "USER"
        CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
        print(CONNECTION_STRING)

        conn = iris.connect(CONNECTION_STRING, username, password)
        self.cursor = conn.cursor()

    def download_table(table_name, output_path):
        pass


# src_engine = create_engine("iris://_SYSTEM:SYS@localhost:1972/USER")


# def RAG_report(query_text):

#     embedTableName = "BASLABS.ClimateReportsEmbed"


# def export_table():

# searchVector = self.model.encode(
#             searchPhrase, normalize_embeddings=True
#         ).tolist()
#         sql = f"""
#             SELECT TOP ? title, summary, description
#             FROM {self.tableName}
#             ORDER BY VECTOR_DOT_PRODUCT(description_vector, TO_VECTOR(?)) DESC
#         """
#         self.cursor.execute(sql, [numberOfResults, str(searchVector)])
#         results = self.cursor.fetchall()
#         return [
#             dict(title=row[0], summary=row[1], description=row[2]) for row in results
#         ]
