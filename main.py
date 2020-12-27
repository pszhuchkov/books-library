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
IMAGES_FOLDER = 'images'


def download_txt(response, filename, books_folder=BOOKS_FOLDER):
    Path(books_folder).mkdir(exist_ok=True)
    filepath = os.path.join(
        books_folder, f"{filename}.txt"
    )
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def download_image(url, images_folder=IMAGES_FOLDER):
    Path(images_folder).mkdir(exist_ok=True)
    response = requests.get(url, verify=False)
    response.raise_for_status()
    filename = url.split('/')[-1]
    filepath = os.path.join(images_folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_books(url, start, end):
    for book_id in range(start, end + 1):
        book_txt_url = url.format(book_id)
        try:
            response = requests.get(book_txt_url, verify=False)
            response.raise_for_status()
            check_for_redirect(response)
        except HTTPError:
            pass
        else:
            filename, image_url = get_bookinfo(book_id)
            print(filename, image_url)
            # download_txt(response, filename)
            download_image(image_url)


def get_bookinfo(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    response = requests.get(book_url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_name = soup.find('h1').text.split('::')[0].strip()
    filename = f"{book_id}. {sanitize_filename(book_name)}"
    image_url = soup.find(class_='bookimage').find('img')['src']
    image_url_full = urljoin(url, image_url)
    return filename, image_url_full


def check_for_redirect(response):
    if response.history:
        raise HTTPError


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    download_books(DOWNLOAD_TXT_URL, 1, 10)
