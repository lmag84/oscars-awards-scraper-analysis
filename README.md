# Analiza danych Oscarowych

Projekt w języku **Python** służący do pobierania, czyszczenia oraz analizy historycznych danych dotyczących ceremonii wręczenia Oscarów.

---

## Spis treści

- [O projekcie](#o-projekcie)
- [Struktura danych](#struktura-danych)
- [Główne funkcjonalności](#główne-funkcjonalności)
- [Czyszczenie danych](#czyszczenie-danych)
- [Użyte technologie](#użyte-technologie)
- [Jak uruchomić projekt lokalnie?](#jak-uruchomić-projekt-lokalnie)
- [Baza danych i model relacyjny](#baza-danych-i-model-relacyjny)

---

## O projekcie

Głównym celem projektu jest automatyczny scraping lokalnych plików HTML, zachowanie pełnej struktury relacyjnej pomiędzy kategoriami, zwycięzcami, nominowanymi, twórcami i filmami, a także wygenerowanie raportu analitycznego oraz utworzenie spójnej bazy danych.

Aplikacja i skrypty dzielą się na trzy główne obszary:
1. **Scraping i parsowanie HTML:** Pobieranie danych z `index.html` oraz podstron `pages/*.html`.
2. **Przetwarzanie i export:** Czyszczenie danych, standaryzacja nazw kategorii, rozdzielanie twórców i filmów oraz zapis do ustrukturyzowanych formatów JSON i CSV.
3. **Persystencja i baza danych:** Zasilenie znormalizowanej bazy SQLite (`oscars.db`) ze spójnymi kluczami obcymi.

---

## Struktura danych

Dane wyjściowe pozyskiwane są z lokalnej strony w katalogu `output/` i przetwarzane do dwóch docelowych struktur:

### 1. Format JSON (Hierarchiczny)
Zachowuje pełne zagnieżdżenie relacji:
- `year` – rok przyznania nagrody / ceremonii
- `categories` – lista kategorii zawierająca:
  - `category_name` – ujednolicona nazwa kategorii
  - `winners` & `nominees` – listy obiektów przypisanych do danej kategorii wraz z powiązanymi twórcami i filmami

### 2. Format CSV (Spłaszczony)
Przygotowany do bezpośredniej analizy statystycznej w bibliotece Pandas lub importu do baz danych:
- `page_id` – unikalny identyfikator podstrony ceremonii
- `year` – rok ceremonii
- `category` – znormalizowana kategoria
- `winner` – flaga przyjmująca wartość `1` (zwycięzca) lub `0` (nominowany)
- `author` – autor lub twórca (z obsłużonymi separatorami `,`, `&`, `and`)
- `movie` – tytuł powiązanego filmu
- `raw_winner_text` – surowy tekst dla kategorii niestandardowych (np. nagrody honorowe)

---

## Główne funkcjonalności

- **Scraping HTML:** Parsowanie struktury za pomocą `BeautifulSoup4` z kodowaniem `UTF-8` i automatycznym wyciąganiem metadanych.
- **Rozdzielanie autorów i dzieł:**
  - Automatyczna separacja nazwy filmu od twórcy na podstawie analizy cudzysłowów od prawej strony.
  - Obsługa nietypowych nazwisk i przyrostków (np. zmiana `, Jr.` na `Jr.`).
  - Wyodrębnianie informacji dodatkowych (np. *Set Decoration:*, *Music by*).
- **Standaryzacja kategorii:** Mapowanie historycznych zmian nazw kategorii oznaczających to samo wyróżnienie (np. `ACTOR` oraz `ACTOR IN A LEADING ROLE`).
- **Obsługa błędów i wyjątków:**
  - Zabezpieczenie przed brakiem cudzysłowów w opisie warunkiem `if '"' in text:`.
  - Weryfikacja obecności metadanych `page_id` (`if not meta: return None`).
  - Bezpieczne pobieranie wartości ze słowników metodą `.get()` w celu ochrony przed błędem `KeyError`.
- **Analiza statystyczna i wykrywanie anomalii:**
  - Identyfikacja rekordzistów (np. Walt Disney z 23 nagrodami indywidualnymi i 4 specjalnymi, *The Lord of the Rings: The Return of the King* z 27 nagrodami).
  - Wykrywanie anomalii w danych (np. 17 kategorii występujących tylko raz w historii, duplikaty rekordów jak *The Lion King* z 1995 r. czy niespójności w nazewnictwie studium Warner Bros. występującym w 11 wariantach).

---

## Czyszczenie danych

Proces czyszczenia obejmuje m.in.:
- standaryzację nazw kategorii,
- ujednolicenie separatorów w nazwiskach i nazwach,
- obsługę nietypowych kategorii i nagród specjalnych,
- rozdzielenie informacji o osobach i filmach,
- obsługę brakujących wartości oraz wyjątków w danych.

---

## Użyte technologie

- **Python**
- **BeautifulSoup4** – web scraping i analiza HTML
- **Pandas** – przetwarzanie i analiza danych
- **JSON** – zapis danych w strukturze hierarchicznej
- **SQLite / sqlite3** – relacyjna baza danych

---

## Jak uruchomić projekt lokalnie?

### 1. Klonowanie repozytorium
```bash
git clone [https://github.com/lmag84/oscars-awards-scraper-analysis](https://github.com/lmag84/oscars-awards-scraper-analysis)
cd oscars-awards-scraper-analysis
```

### 2. Instalacja zależności

Zainstaluj wymagane pakiety za pomocą pip:
```bash
pip install -r requirements.txt
```

### 3. Uruchomienie

Projekt składa się z trzech modułów, które należy uruchamiać w następującej kolejności:

Pobieranie danych (Scraping):
```bash
python scraping.py
```

Analiza danych:
```bash
python analyst.py
```

Utworzenie bazy SQL:
```bash
python to_sql.py
```


W wyniku działania projektu generowane są pliki z danymi oraz baza oscars.db.

## Baza danych i model relacyjny

Dane są przechowywane w bazie SQLite.

Główna tabela data_oscars zawiera dane dotyczące nominacji i zwycięzców, natomiast dodatkowe tabele słownikowe przechowują unikalne wartości poszczególnych pól.

Relacje pomiędzy tabelami są realizowane za pomocą kluczy obcych, co ogranicza powtarzanie danych i umożliwia ich łączenie za pomocą JOIN.