import requests
import urllib3
from pathlib import Path
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


BOOKS_FOLDER = 'books'
BOOK_URL = 'https://tululu.org/b{}'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'


def download_txt_book(url, filename, books_folder):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        check_for_redirect(response)
    except HTTPError:
        pass
    else:
        with open(f"{books_folder}/{filename}.txt", 'w') as file:
            file.write(response.text)


def download_books(url, count, books_folder=BOOKS_FOLDER):
    for book_id in range(1, count + 1):
        filename = get_filename(book_id)
        download_url = url.format(book_id)
        download_txt_book(download_url, filename, books_folder)


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_filename(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    response = requests.get(book_url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_name = soup.find('h1').text.split('::')[0].strip()
    filename = f"{book_id}. {sanitize_filename(book_name)}"
    return filename


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    download_books(DOWNLOAD_TXT_URL, 10)
