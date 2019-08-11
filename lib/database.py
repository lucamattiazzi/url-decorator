from bs4 import BeautifulSoup
import requests
import uuid

CREATE_TABLE_SQL = '''
  CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    shortened VARCHAR(12),
    url VARCHAR(255),
    image VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    name VARCHAR(255),
    created_at DATE DEFAULT (datetime('now','localtime'))
  )'''

WRITE_ROW_SQL = "INSERT INTO urls(shortened, url, image, title, description, name) VALUES (?, ?, ?, ?, ?, ?)"
READ_ROW_SQL = "SELECT url, image, title, description, name FROM urls WHERE shortened = ?"

URL_FALLBACK = "grokked.it"
IMAGE_FALLBACK = "https://www.ready.gov/sites/default/files/hazard-hero-images/nuclear_blast_v2.jpg"
TITLE_FALLBACK = "Roba superinteressante!"
DESCRIPTION_FALLBACK = "Descrizione di un'interessantezza incredibile"
NAME_FALLBACK = "Sito interessante"


def generate_uuid():
    return str(uuid.uuid4())[:8]


def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    connection.commit()
    connection.close()


def write_row(connection, shortened, url, image, title, description, name):
    cursor = connection.cursor()
    cursor.execute(WRITE_ROW_SQL, [shortened, url,
                                   image, title, description, name])
    connection.commit()
    connection.close()


def find_row(connection, shortened):
    cursor = connection.cursor()
    cursor.execute(READ_ROW_SQL, [shortened])
    results = cursor.fetchone()
    connection.commit()
    connection.close()
    return results


def get_og(soup, property, fallback, value):
    if value is not None:
        return value
    existant = soup.find("meta", property=f"og:{property}")
    if existant is None:
        return fallback
    return existant["content"]


def get_shortened_url(connection, url, image, title, description, name):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    url = get_og(soup, "url", URL_FALLBACK, url)
    image = get_og(soup, "image", IMAGE_FALLBACK, image)
    title = get_og(soup, "title", TITLE_FALLBACK, title)
    description = get_og(soup, "description",
                         DESCRIPTION_FALLBACK, description)
    name = get_og(soup, "site_name", NAME_FALLBACK, name)
    shortened = generate_uuid()
    write_row(connection, shortened, url, image, title, description, name)
    return shortened


def get_decorations(connection, shortened):
    return find_row(connection, shortened)
