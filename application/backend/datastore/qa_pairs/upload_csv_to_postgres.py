import psycopg2
from psycopg2 import sql
import os
import csv
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

host = "som-postgres.postgres.database.azure.com"
dbname = "questions_answers"
user = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")

# Connection String
conn_string = "host={0} user={1} dbname={2} password={3}".format(
    host, user, dbname, password
)

csv_file_path='cleaned_questions_answers.csv'

class PostgresCSVLoader:
    """Class to load CSV data into a Postgres database."""

    def __init__(self, csv_file_path: str, table_name: str = "qa_pairs"):
        self.csv_file_path = csv_file_path
        self.table_name = table_name
        self.connection = self.connect_to_db()

        if self.connection:
            self.cursor = self.connection.cursor()
            self._create_table_if_not_exists()
        
    def connect_to_db(self):
        try:
            connection = psycopg2.connect(conn_string)
            return connection
        except psycopg2.OperationalError as error:
            print(f"Database connection failed due to {error}")
            return None

    def _create_table_if_not_exists(self) -> None:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            program VARCHAR(255),
            language VARCHAR(255),
            question TEXT,
            answer TEXT
        );"""
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def load_csv_data(self) -> None:
        with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                insert_query = sql.SQL("INSERT INTO {} (program, language, question, answer) VALUES (%s, %s, %s, %s)").format(sql.Identifier(self.table_name))
                self.cursor.execute(insert_query, (row['program'], row['language'], row['question'], row['answer']))
            self.connection.commit()

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

if __name__ == "__main__":
    loader = PostgresCSVLoader(csv_file_path='cleaned_questions_answers.csv')
    loader.load_csv_data()
    loader.close_connection()
    print("CSV data has been loaded successfully.")