import requests
import urllib3
import os
import argparse
from pathlib import Path
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from datetime import datetime


BOOKS_FOLDER = 'books'
BOOK_URL = 'https://tululu.org/b{}'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'
IMAGES_FOLDER = 'images'


def download_txt(response, filename, books_folder=BOOKS_FOLDER):
    filepath = os.path.join(
        books_folder, f"{sanitize_filename(filename)}.txt"
    )
    with open(filepath, 'w', encoding='utf8') as file:
        file.write(response.text)
    return filepath


def download_image(url, images_folder=IMAGES_FOLDER):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    filename, extension = os.path.splitext(url.split('/')[-1])
    filepath = os.path.join(
        images_folder, f'{filename}_{get_timestamp_now()}{extension}'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)


def get_timestamp_now():
    now = datetime.now()
    timestamp_now = round(datetime.timestamp(now))
    return timestamp_now


def download_books(url, start, end):
    for book_id in tqdm(range(start, end + 1)):
        book_txt_url = url.format(book_id)
        try:
            response = requests.get(book_txt_url, verify=False)
            response.raise_for_status()
            check_for_redirect(response)
        except HTTPError:
            pass
        else:
            book_properties = get_book_properties(book_id)
            filename = f"{book_id}. {book_properties['name']}"
            download_txt(response, filename)
            download_image(book_properties['image_url'])


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_properties(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    response = requests.get(book_url, verify=False)
    response.raise_for_status()
    book_page = response.text
    return parse_book_page(book_page, url)


def parse_book_page(html, url):
    soup = BeautifulSoup(html, 'lxml')
    book_name = soup.find('h1').text.split('::')[0].strip()
    author = soup.find('h1').text.split('::')[1].strip()
    image_url_relative = soup.find(class_='bookimage').find('img')['src']
    image_url_absolute = urljoin(url, image_url_relative)
    comments_raw = soup.find_all(class_='texts')
    comments = [comment.find('span').text for comment in comments_raw]
    genres_raw = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres_raw]
    return {
        'name': book_name,
        'author': author,
        'image_url': image_url_absolute,
        'comments': comments,
        'genres': genres
    }


def get_parsed_arguments():
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги с сайта tululu.org. В качестве '
                    'аргументов принимается начальный и конечный id книг.'
    )
    parser.add_argument('start_id', type=int)
    parser.add_argument('end_id', type=int)
    return parser.parse_args()


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    Path(IMAGES_FOLDER).mkdir(exist_ok=True)
    args = get_parsed_arguments()
    download_books(
        DOWNLOAD_TXT_URL, args.start_id, args.end_id
    )
