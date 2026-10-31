import sqlite3
import os
import pandas as pd

oscars_df = pd.read_csv('list.csv')

if os.path.exists("oscars.db"):
    os.remove("oscars.db")

# utworzenie połączenia z bazą danych
conn = sqlite3.connect("oscars.db")
cursor = conn.cursor()

oscars_df['year'] = pd.to_numeric(oscars_df['year'], errors='coerce')

# tworzenie tabel słownikowych oraz wypełnienie ich danymi
def create_table(table_name, new_column_name, conn, df, column_name,column_type):

    cursor = conn.cursor()

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {new_column_name} {column_type} NOT NULL
    )
    ''')

    unique_values = df[[column_name]].dropna().drop_duplicates()

    for _, row in unique_values.iterrows():
        value = row[column_name]
        if column_type.upper() == "INTEGER":
            try:
                value = int(value)
            except:
                continue

        cursor.execute(f'''
            INSERT INTO {table_name} ({new_column_name})
            VALUES (?)
        ''', (value,))

    conn.commit()

create_table("year", "rok", conn, oscars_df, "year", "INTEGER")
create_table("page_id", "identyfikator_strony", conn, oscars_df, "page_id", "TEXT")
create_table("category", "kategoria", conn, oscars_df, "category","TEXT")
create_table("author", "autor", conn, oscars_df, "author", "TEXT")
create_table("movie", "film", conn, oscars_df, "movie","TEXT")
create_table("link", "nazwa_strony_internetowej", conn, oscars_df, "link","TEXT")
create_table("raw_winner_text", "nagrody_specjalne", conn, oscars_df, "raw_winner_text","TEXT")
create_table("winner", "czy_zwyciężył", conn, oscars_df, "winner","INTEGER")

cursor.execute('''
CREATE TABLE data_oscars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    link_id INTEGER,
    year_id INTEGER,
    category_id INTEGER,
    author_id INTEGER,
    movie_id INTEGER,
    raw_winner_text_id INTEGER,
    winner_id INTEGER,
    page_id_id INTEGER,
    FOREIGN KEY(link_id) REFERENCES link(id),
    FOREIGN KEY(year_id) REFERENCES year(id),
    FOREIGN KEY(category_id) REFERENCES category(id),
    FOREIGN KEY(author_id) REFERENCES author(id),
    FOREIGN KEY(movie_id) REFERENCES movie(id),
    FOREIGN KEY(raw_winner_text_id) REFERENCES raw_winner_text(id),
    FOREIGN KEY(winner_id) REFERENCES winner(id),
    FOREIGN KEY(page_id_id) REFERENCES page_id(id)
)
''')

conn.commit()


# wydobycie id z tabel
def get_id(cursor, table_name, column_name, value):

    if pd.isna(value):
        return None
    cursor.execute(
        f"SELECT id FROM {table_name} WHERE {column_name} = ?",
        (value,)
    )

    result = cursor.fetchone()

    return result[0] if result else None

# tworzenie tabeli ze wszystkimi danymi dot. Oscarów
for _, row in oscars_df.iterrows():
    year_id = get_id(cursor, "year", "rok", row["year"])
    page_id_id = get_id(cursor, "page_id", "identyfikator_strony", row["page_id"])
    category_id = get_id(cursor, "category", "kategoria", row["category"])
    author_id = get_id(cursor, "author", "autor", row["author"])
    movie_id = get_id(cursor, "movie", "film", row["movie"])
    link_id = get_id(cursor, "link", "nazwa_strony_internetowej", row["link"])
    raw_winner_text_id = get_id(cursor, "raw_winner_text", "nagrody_specjalne", row["raw_winner_text"])
    winner_id = get_id(cursor, "winner", "czy_zwyciężył", row["winner"])

    cursor.execute('''
        INSERT INTO data_oscars (
            year_id, page_id_id, category_id, author_id,
            movie_id, link_id, raw_winner_text_id, winner_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        year_id, page_id_id, category_id, author_id,
        movie_id, link_id, raw_winner_text_id, winner_id
    ))

conn.commit()


query4 = '''
SELECT *
FROM author
'''

top_cities = pd.read_sql_query(query4, conn)
print(top_cities)




