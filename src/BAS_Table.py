from BAS_Database import BAS_Database
import pandas as pd


class BAS_Table:
    def __init__(self):
        self.db = BAS_Database()

    def create_UN(self):
        tableName = "BASLABS.UNClimateAction"
        tableDefinition = "(title VARCHAR(255), summary VARCHAR(1000), description VARCHAR(4000), description_vector VECTOR(DOUBLE, 384))"

        try:
            self.db.cursor.execute(f"DROP TABLE {tableName}")
        except:
            pass
        self.db.cursor.execute(f"CREATE TABLE {tableName} {tableDefinition}")

        df = pd.read_csv("../vectorbase/data/unfccc_initiatives.csv")
        df.fillna("", inplace=True)

        # Get embeddings
        embeddings = self.db.embed_minilm.encode(
            df["description"].tolist(), normalize_embeddings=True
        )
        df["description_vector"] = embeddings.tolist()

        # add data
        sql = f"""
            INSERT INTO {tableName}
            (title, summary, description, description_vector) 
            VALUES (?, ?, ?, TO_VECTOR(?))
        """
        data = [
            (
                row["title"],
                row["summary"],
                row["description"],
                str(row["description_vector"]),
            )
            for index, row in df.iterrows()
        ]
        results = self.db.cursor.executemany(sql, data)
        return results
