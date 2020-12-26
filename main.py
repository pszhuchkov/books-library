import requests
import urllib3
from pathlib import Path


BOOKS_FOLDER = 'books'
URL_PATTERN = 'https://tululu.org/txt.php?id={}'


def download_book(url, book_id, books_folder):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    with open(f'{books_folder}/book_{book_id}.txt', 'w') as file:
        file.write(response.text)


def download_books(count):
    for book_id in range(1, count+1):
        url = URL_PATTERN.format(book_id)
        download_book(url, book_id, BOOKS_FOLDER)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    download_books(10)
