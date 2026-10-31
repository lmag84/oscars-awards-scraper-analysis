# Skrypt do ekstrakcji danych o nominacjach i zwycięzcach Oscarów
# z lokalnych plików HTML i normalizacji danych do postaci tabelarycznej

import json
import pandas as pd
from bs4 import BeautifulSoup as bs

prefix_path = "oscars/output"
index_path = f'{prefix_path}/index.html'
separator=" and "

# Funkcja wczytująca plik HTML i zwracająca obiekt BeautifulSoup
def parse_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return bs(file, "html.parser")


# Funkcja rozdzielająca osoby nominowane zwycięskie od tytułu filmu
def parse_movie_author(text):
    movie = None
    if '"' in text:
        before, movie, _ = text.rsplit('"', 2)
        authors_part = before.rstrip(" -").strip()

    else:
        authors_part = text.strip()

    # zastąpienie ciągu znaków ", Jr.", aby nie zostały błędnie rozdzielone jako separator autorów
    authors_part = authors_part.replace(", Jr.", " Jr.")

    # rozdzielenie conajmniej 2 autorów nominowanych lub grupy zwycięzców za jeden film w jednej kategorii połączonych średnikiem
    authors = [a.strip() for a in authors_part.split(";")]

    # zastąpienie różnych łączników między autorami oraz nominowanymi jedym łącznikiem
    # rozdzielenie grupy autorów jednego filmu w jednej kategorii tym łącznikiem
    cleaned_authors = []
    for author in authors:
        author = author.replace(", ", separator).replace(" & ", separator)
        cleaned_authors.append(author)

    return cleaned_authors, movie


# funkcja ujednolicniająca nazwy kategorii Oscarowych pomiędzy różnymi latami
def standardize_ceremony_data(data_frame):

    name_mapping = {
        'MUSIC (Original Song Score and Its Adaptation or Adaptation Score)': 'MUSIC (Original Song Score and Its Adaptation or Adaptation Score)',
        'MUSIC (Scoring: Adaptation and Original Song Score)':'MUSIC (Scoring: Original Song Score and Adaptation -or- Scoring: Adaptation)',
        'ACTOR IN A LEADING ROLE':'ACTOR',
        'ACTRESS IN A LEADING ROLE':'ACTRESS',
        'OUTSTANDING PICTURE':'BEST PICTURE',
        'OUTSTANDING MOTION PICTURE':'BEST MOTION PICTURE',
        'MUSIC (Song--Original for the Picture)':'MUSIC (Song)',
        'MUSIC (Score of a Musical Picture--original or adaptation)':'MUSIC (Scoring of a Musical Picture)',
        'MUSIC (Original Music Score)':'MUSIC (Original Score)',
        'MUSIC (Music Score--substantially original)':'MUSIC (Original Score)'

    }

    df['category'] = df['category'].map(lambda x: name_mapping.get(x, x) if pd.notna(x) else x)

    return df


# funkcja wydobywająca dodatkowe informacje o roli autora (np. written by)                                                                       ńb
def additional_information(text):
    keywords = [
        'Written for the screen by ', 'Adaptation Score by ',
        'Set Decoration: ', 'Interior Decoration: ',
        'Art Direction: ', 'Production Design: ',
        'Sound Effects by ', 'Music by ',
        'Written by ', 'Story by ', 'Lyrics by ',
        'Screenplay by ', 'Visual Effects by ',
        'Musical Settings :','Lyric by '
            ]

    for key in keywords:
        if key in text:
            clean_text=text.replace(key,"").strip()
            clean_key=key.replace(": ","")

            return clean_text, clean_key

    return text.strip(), None


# funkcja wydobywająca unikalne page id strony roku z sekcji meta-info
def extract_page_id(soup):
    meta = soup.find("p", class_="meta-info")
    if not meta:
        return None

    text = meta.text.strip()

    if ":" in text:
        return text.split(":", 1)[1].strip()

    return text


# funkcja tworząca rekordy danych dla pojedyńczej kategorii
# każdy rekord reprezentuje jednego autora przypisanego do filmu
def build_records(cat, winner_nominate_text):
    records = []
    authors, movie = parse_movie_author(winner_nominate_text)

    for author_group in authors:
        clean_author, info = additional_information(author_group)
        split_authors = clean_author.split(separator)

        for author in split_authors:
            records.append({
                "category": cat,
                "additional_information": info,
                "author": author.strip(),
                "movie": movie,
                "winner": None

            })

    return records


# funkcja wstawiająca do słownika kolumnę z informacją czy dany film wraz z autorem są zwycięzcą, czy nominowanym
def build_records_with_flag(name_of_category, text, is_winner):
    records = build_records(name_of_category, text)
    for r in records:
        r["winner"] = is_winner
    return records


# funkcja wydzialająca nagrodzonych oraz nominowanych z danej strony roku
# uwzględnia kategorie specjalne, z których nie da się jednoznacznie wydobyc autora i filmu
def get_raw_category_data(link):
    raw_categories = ["HONORARY AWARD", "SPECIAL AWARD", "AWARD OF COMMENDATION","HONORARY FOREIGN LANGUAGE FILM AWARD"]
    category_data = []

    #zawartośc strony internetowej - w perspektywie roku, kategorii oraz użycie funkcji page id
    year_content = parse_html(link)
    categories = year_content.find_all("div", class_="category-section")
    page_id=extract_page_id(year_content)

    # pętla po kategoriach dająca nazwę kategorii, zwycięzców oraz nominowanych
    for category in categories:
        cat_name = category.find("h2").text.strip()

        winners = category.find_all("div", class_="winner")
        nominees = category.select(".nominee")

        # pętla po zwycięzcach
        for winner in winners:
            text = winner.text.strip()

            if cat_name in raw_categories:
                category_data.append({
                    "category": cat_name,
                    "additional_information": None,
                    "author": None,
                    "movie": None,
                    "winner": 1,
                    "raw_winner_text": text,
                    "page_id": page_id
                })
            else:
                records = build_records_with_flag(cat_name, text, 1)
                for one_record in records:
                    one_record["page_id"]=page_id
                category_data.extend(records)

        # dodanie nominowanych do słownika
        for nominee in nominees:
            text = nominee.text.strip()
            records=build_records_with_flag(cat_name, text, 0)
            for possition in records:
                possition["page_id"] = page_id
            category_data.extend(records)

    return category_data


# uzuełnianie słownika danymi
def get_year_data(index_file_path, prefix_file_path):
    content = parse_html(index_file_path)
    div_section = content.find_all("div", class_="year-card")

    all_ceremony_data = []

    for element in div_section:
        year = int(element.find("h2").text.strip())
        link = f'{prefix_file_path}/{element.find("a").get("href")}'

        categories = get_raw_category_data(link)

        for category in categories:
            all_ceremony_data.append({
                "year": year,
                "link": link,
                "category": category["category"],
                "additional_information": category["additional_information"],
                "author": category["author"],
                "movie": category["movie"],
                "raw_winner_text": category.get("raw_winner_text"),
                "winner": category["winner"],
                "page_id": category['page_id']
            })

    return all_ceremony_data


#funkcja tworząca strukturę słownikową wg schematu:
# {rok: {kategoria: {zwycięzca: [...], nmoinowani: [...] oraz nominowanymi
def process_category(cat,year, new_dict):

    if year not in new_dict:
        new_dict[year]={}

    category_name = cat["category"]

    if category_name not in new_dict[year]:
        new_dict[year][category_name] = {
            "winners": [],
            "nominees": []
        }
    record = {
        "author": cat["author"],
        "movie": cat["movie"]
    }

    if cat["winner"] == 1:
        new_dict[year][category_name]["winners"].append(record)
    else:
        new_dict[year][category_name]["nominees"].append(record)
    return new_dict


# funkcja tworząca słownik z danymi dotyczącymi ceremonii Oscarowych
# przygotowane dane są strukturą hierarchiczną do jsona
def data_to_json(index_file_path, prefix_file_path):
    content = parse_html(index_file_path)
    div_section = content.find_all("div", class_="year-card")

    ceremony_data_json = {}

    for element in div_section:
        year = str(int(element.find("h2").text.strip()))
        link = f'{prefix_file_path}/{element.find("a").get("href")}'

        categories = get_raw_category_data(link)

        for category in categories:
            ceremony_data_json = process_category(category,year,ceremony_data_json)

    return ceremony_data_json


ceremony_data = get_year_data(index_path, prefix_path)
df = pd.DataFrame(ceremony_data)
df = standardize_ceremony_data(df)

# usunięcie fałszywych danych zawartych w autorze np. producer
invalid_authors = ["Producer", "Producers", "Sound Director","Music"]
df = df[~df["author"].isin(invalid_authors)]

# zapis danych do pliku CSV w kodowaniu UTF-8 (uwzględniającym polskie znaki)
df.to_csv("list.csv", index=False, encoding="utf-8-sig")

ceremony_data_to_json=data_to_json(index_path,prefix_path)

y=json.dumps(ceremony_data_to_json)
with open("out.json","w") as f:
    f.write(y)
