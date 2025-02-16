import iris
from sentence_transformers import SentenceTransformer
import os


class BASDatabase:
    """
    Class to search the UN Climate Action database with a search phrase
    and return structured title, summary, description in list format.
    """

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.conn = None
        self.cursor = None
        self.tableName = "BASLABS.UNClimateAction"

    def connect(self):
        """
        Connect to the IRIS database and create a cursor.
        """
        username = "demo"
        password = "demo"
        hostname = os.getenv("IRIS_HOSTNAME", "localhost")
        port = "1972"
        namespace = "USER"
        CONNECTION_STRING = f"{hostname}:{port}/{namespace}"
        self.conn = iris.connect(CONNECTION_STRING, username, password)
        self.cursor = self.conn.cursor()

    def search_UN(self, searchPhrase, numberOfResults=5):
        """
        Search the UN Climate Action database with a search phrase
        and return structured title, summary, description in list format.
        """
        if not self.conn:
            self.connect()
        searchVector = self.model.encode(
            searchPhrase, normalize_embeddings=True
        ).tolist()
        sql = f"""
            SELECT TOP ? title, summary, description
            FROM {self.tableName}
            ORDER BY VECTOR_DOT_PRODUCT(description_vector, TO_VECTOR(?)) DESC
        """
        self.cursor.execute(sql, [numberOfResults, str(searchVector)])
        results = self.cursor.fetchall()
        return [
            dict(title=row[0], summary=row[1], description=row[2]) for row in results
        ]


if __name__ == "__main__":
    # TODO