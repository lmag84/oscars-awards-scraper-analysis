import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Wczytanie pliku csv
df = pd.read_csv("list.csv")


# Analiza nr 1: średnia roczna liczba nominowanych osób w jednej kategorii

# wyfiltrowanie danych dotyczących nominowanych (bez zwycięzców)
df_nominees = df[df["winner"]==0]

# pogrupowanie danych po roku i kategorii
nominee_counts = (
    df_nominees
    .groupby(["year", "category"])
    .size()
    .reset_index(name="nominee_count")
)

# obliczenie średniej ilości nominowanych w danym roku
mean_per_year = (
    nominee_counts
    .groupby("year")["nominee_count"]
    .mean()
    .reset_index(name="mean_nominees")
)

# znalezienie największej oraz najmniejszej średniej liczby osób nominowanych w badanym okresie
max_row = mean_per_year.loc[mean_per_year["mean_nominees"].idxmax()]
min_row = mean_per_year.loc[mean_per_year["mean_nominees"].idxmin()]

max_year = int(max_row["year"])
min_year = int(min_row["year"])
max_mean = max_row["mean_nominees"]
min_mean = min_row["mean_nominees"]
highest_diffrence=max_mean-min_mean

print(f'''
Największa średnia roczna ilość osób nominowanych do Oscara ({round(max_mean, 2)}) w jednej kategorii była w roku {max_year}.
Najmniejszą średnią ilość osób nominowanych do Oscara ({round(min_mean, 2)}) w jednej kategorii odnotowano w roku {min_year}.
Różnica pomiędzy największą, a najmniejszą roczną średnią ilością nominowanych do Oscara osób wynosi {round(highest_diffrence, 2)}.
''')


# Analiza nr 2: Najczęściej wygrywający autor oraz najczęciej wygrywający film wśród wszystkich zwycięzców

# wyfiltrowanie danych dotyczących zwycięzców
df_winners=df[df['winner']==1]

# obliczenie ilości zwycięskich autorów, znalezienie autora który wygrał najwięcej razy
winner_author_counts = df_winners['author'].value_counts()

winner_author_counts = winner_author_counts.reset_index()
winner_author_counts.columns=["author", "wins"]
max_winner = winner_author_counts.loc[winner_author_counts["wins"].idxmax()]
max_author=max_winner["author"]
max_number_winners=max_winner["wins"]
winner_movie_counts = df_winners["movie"].value_counts()

# obliczenie ilości zwycięskich filmów, znalezienie filmu który wygrał najwięcej razy
winner_movie_counts = winner_movie_counts.reset_index()
winner_movie_counts.columns=["movie", "wins"]

max_winner_movie = winner_movie_counts.loc[winner_movie_counts["wins"].idxmax()]
max_movie=max_winner_movie["movie"]
max_number_movie_winners=max_winner_movie["wins"]

disney_lst=[a for a in df['raw_winner_text'] if "Walt Disney" in str(a)]
Disney_special_awards=len(disney_lst)

print(f'''
{max_author} zdobył Oscara {max_number_winners} razy w różnych kategoriach. 
Jest to najwyższa liczba zwcięstw odnotowana w analizowanym zbiorze danych.
Dodatkowo został uhonorowany specjalnymi nagrodami {Disney_special_awards} razy.

"{max_movie}" uzyskał {max_number_movie_winners} nagórd, co stanowi rekordową liczbę zwycięstw wśród analizowanych produkcji. 
''')


# Analiza nr 3: Unikalne kategorie dobecne w całym analizowanym okresie

# Stworzenie tabelki z unikalnymiparami  rok - kategoria
df_unique = df[["year","category"]].drop_duplicates()

number_of_categories = (
    df_unique["category"]
    .value_counts()
    .reset_index(name="category_count")
)
# liczba lat poddana analizie
number_of_years = len(df_unique[["year"]].drop_duplicates())

# znalezienie kategorii, które występowały we wszystkich latach
max_cat = number_of_categories[number_of_categories["category_count"] == number_of_years]
max_category_list = max_category_list = max_cat["category"].tolist()

if len(max_category_list)>0:
    print(f"""
W analizowanym okresie obejmującym {number_of_years} lat, 
{len(max_category_list)} kategorie występowały w każdym roku przyznawania nagród,
są to następujące kategorie:
{", ".join(max_category_list)}.
    """)
else:
    print("Żadna kategoria nie występowała nieprzerwanie przez cały analizowany okres.")


# Anomalia nr 1: kategorie, które wystąpiły tylko raz we wszystkich latach dot. Oscarów:

# lista kategorii, która wystąpiła tylko raz (na podstawie obliczeń z analizy nr 3)
categories_appreared_once = number_of_categories[number_of_categories["category_count"] ==1]
number_of_once_categories = len(categories_appreared_once)
categories_appreared_once_list = categories_appreared_once["category"].tolist()
print(f'''
{number_of_once_categories} kategorii pojawiło się w historii Oscarów tylko jeden raz.
Oto ich lista:
{", ".join(categories_appreared_once_list)}.
''')


# Anomalia nr 2: rozbieżności w nazewnictwie autorów - 1 autor pod kilkoma nazwami

#stworzenie listy z unikalnymi autorami
# sprawdzenie ilości występowania 2 przykładowych autorów
unique_authors = df["author"].drop_duplicates()
unique_disney = [a for a in unique_authors if "Walt Disney" in str(a)]
unique_warner_bros = [b for b in unique_authors if "Warner Bros" in str(b)]

print(f'''
Walt Disney pojawiał się jako autor nominowanego lub zwycięskiego filmu pod różnymi postaciami {len(unique_disney)} razy.
W zbiorze danych Walt Disney występuje pod następującymi wariantami zapisu: {" ,".join(unique_disney)}.
Innym przykładem jest Warner Bros, który w analizowanym zbiorze danych występuje {len(unique_warner_bros)} razy, pod następującymi nazwami:
{" ,".join(unique_warner_bros)}
''')


# Anomalia nr 3: więcej niż jeden nagrodzony film w jednej kategorii w jednym roku

# tabelka z unikalnymi filmami występującymi w jednej kategorii w jednym roku
winner_movie_counts = (
    df_winners
    .groupby(["year", "category"])["movie"]
    .nunique()
    .reset_index(name="unique_winner_movies")
)

# kategorie w których jest więcej niż 1 nagrodzony film
many_movie_winners = winner_movie_counts[winner_movie_counts["unique_winner_movies"] > 1]
print(f"""
W analizowanym zbiorze danych zidentyfikowano {len(many_movie_winners)} przypadków,
w których w tej samej kategorii i roku nagrodzono więcej niż jeden film.

Poniżej przedstawiono listę takich sytuacji wraz z rokiem, kategorią oraz liczbą nagrodzonych filmów:

{many_movie_winners}
""")


#  Wykres nr 1: w ilu kategoriach i ile razy wygrał dany autor - top 10

# ujednolicenie nazwy autora Metro-Goldwyn-Mayer
df_winners["author"] = df_winners["author"].replace(
    {
        "Metro-Goldwyn-Mayer Studio Sound Department": "Metro-Goldwyn-Mayer"
    }
)

# stworzenie tabelki z top 10 zwycięzcami wśród autorów, którzy zdobyli największą ilością nagród
# w tabelce są zwarte również ilości zwycięstw oraz unikalne kategorie w których autor wygrał
top_authors = (
    df_winners
    .groupby("author")
    .agg(
        total_wins = ("author", "count"),
        unique_categories = ("category", "nunique")
    )
    .reset_index()
    .sort_values("total_wins", ascending = False)
    .head(10)
)

authors = top_authors["author"]

x = np.arange(len(authors))
width = 0.35

# utworzenie dwóch wykresów słupkowych
fig1, ax = plt.subplots(figsize = (12,6))

bar1 = ax.bar(x - width/2, top_authors["total_wins"], width, label = "liczba zwycięstw")
bar2 = ax.bar(x+  width/2, top_authors["unique_categories"], width, label = "liczba unikalnych kategorii")

# Ustawienie tytułów osi, tytułu wykresu
ax.set_xlabel("Autor")
ax.set_ylabel("Liczba")
ax.set_title("Top 10 autorów: liczba zwycięstw i liczba unikalnych kategorii")
ax.set_xticks(x)
ax.set_xticklabels(authors, rotation=45, ha="right")

ax.legend()

plt.tight_layout()
plt.show()


# wykres 2: stosunek ilości wygranych do nominacji

# stworzenie 2 tabelek - pierwszej z ilością autorów nominowanych, drugiej - z ilością zwycięskich autorów
number_of_nominees = (
    df["author"]
    .value_counts()
    .reset_index(name="author_nominee_count")
)

number_of_winners = (
    df_winners["author"]
    .value_counts()
    .reset_index(name = "author_winns_count")
)

# scalenie dwóch tabelek w jedną
summary = number_of_nominees.merge(
    number_of_winners,
    on ="author",
    how = "left"
)

# skuteczność nominacji - stosunek ilości zwycięstw do ilości nominacji
summary["win_%"] = summary["author_winns_count"]/summary["author_nominee_count"]*100

summary_filtered = summary[summary["author_nominee_count"]>=5]

plt.figure(figsize=(8,6))

plt.scatter(
    summary_filtered["author_nominee_count"],
    summary_filtered["win_%"],
    s=summary_filtered["author_winns_count"]*20
)

plt.xlabel("Liczba nominacji", fontsize=12)
plt.ylabel("Skuteczność (%)", fontsize=12)
plt.title("Nominacje vs skuteczność",fontsize=12)

plt.show()


# wykres nr 3: średnia liczba współzwycięzców w jednej kategorii w różnych latach

# stworzenie tabelki z liczbą unikalnych autorów, którzy zwyciężyli w jednej kategorii w jednym roku
multi_winners =(
    df_winners
    .groupby(["year","category"])["author"]
    .nunique()
    .reset_index(name="winner_count")
)

# średnia ilość współzwycięzców w jednej kategorii
avg_winners_per_year = (
    multi_winners
    .groupby("year")["winner_count"]
    .mean()
    .reset_index(name="avg_winner_count")
)

x = avg_winners_per_year["year"]
y = avg_winners_per_year["avg_winner_count"]

# stworzenie linii trendu
z = np.polyfit(x,y,1)
p = np.poly1d(z)

# stworzenie wykresu liniowego z linią trendu
plt.figure(figsize=(10,6))
plt.plot(x, y, marker="o",label = "Średnia liczby współzwycięzców")
plt.plot(x, p(x), linestyle = "--", label="linia trendu")

plt.xlabel("Rok")
plt.ylabel("Średnia liczby współzwycięzców")
plt.title("Zmiana liczby współnagrodzonych w czasie")
plt.legend()

plt.show()