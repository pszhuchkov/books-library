import requests
import urllib3
import os
from pathlib import Path
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin


BOOKS_FOLDER = 'books'
BOOK_URL = 'https://tululu.org/b{}'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'


def download_txt(url, filename, books_folder):
    Path(books_folder).mkdir(exist_ok=True)
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        check_for_redirect(response)
    except HTTPError:
        pass
    else:
        filepath = os.path.join(
            books_folder, f"{sanitize_filename(filename)}.txt"
        )
        with open(filepath, 'w') as file:
            file.write(response.text)
        return filepath


def download_image(url, filename, books_folder):
    pass


def download_books(url, start, end, books_folder=BOOKS_FOLDER):
    for book_id in range(start, end + 1):
        book_txt_url = url.format(book_id)
        filename = get_filename(book_id) or str(book_id)
        download_txt(book_txt_url, filename, books_folder)


def get_filename(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    try:
        response = requests.get(book_url, verify=False)
        response.raise_for_status()
    except HTTPError:
        pass
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        book_name = soup.find('h1').text.split('::')[0].strip()
        filename = f"{book_id}. {book_name}"
        return filename


def check_for_redirect(response):
    if response.history:
        raise HTTPError


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    download_books(DOWNLOAD_TXT_URL, 1, 10)
