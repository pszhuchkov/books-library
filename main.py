import requests
import urllib3
from pathlib import Path
from requests.exceptions import HTTPError


BOOKS_FOLDER = 'books'
URL = 'https://tululu.org/txt.php'


def download_book(url, books_folder, params):
    try:
        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
        check_for_redirect(response)
    except HTTPError:
        print(f"{params['id']}: redirection")
    else:
        with open(f"{books_folder}/book_{params['id']}.txt", 'w') as file:
            file.write(response.text)


def download_books(url, books_folder, count):
    for book_id in range(1, count + 1):
        params = {'id': book_id}
        download_book(url, books_folder, params)


def check_for_redirect(response):
    if response.history:
        raise HTTPError


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    download_books(URL, BOOKS_FOLDER, 10)
