import pandas as pd
import numpy as np
import iris
import time
import os

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Vector Database Setup
username = "demo"
password = "demo"
hostname = os.getenv("IRIS_HOSTNAME", "localhost")
port = "1972"
namespace = "USER"
CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
print(CONNECTION_STRING)

conn = iris.connect(CONNECTION_STRING, username, password)
cursor = conn.cursor()

# Create table
tableName = "BASLABS.UNClimateAction"
tableDefinition = "(title VARCHAR(255), summary VARCHAR(1000), description VARCHAR(4000), description_vector VECTOR(DOUBLE, 384))"

try:
    cursor.execute(f"DROP TABLE {tableName}")
except:
    pass
cursor.execute(f"CREATE TABLE {tableName} {tableDefinition}")

# Load data
df = pd.read_csv("data/unfccc_initiatives.csv")
df.fillna("", inplace=True)

# Get embeddings
embeddings = model.encode(df["description"].tolist(), normalize_embeddings=True)
df["description_vector"] = embeddings.tolist()

# add data
sql = f"""
    INSERT INTO {tableName}
    (title, summary, description, description_vector) 
    VALUES (?, ?, ?, TO_VECTOR(?))
"""
data = [
    (row["title"], row["summary"], row["description"], str(row["description_vector"]))
    for index, row in df.iterrows()
]
results = cursor.executemany(sql, data)
