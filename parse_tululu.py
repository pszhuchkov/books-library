import argparse
import json
import os
import sys
import time

import requests
import urllib3

from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError, ConnectionError
from tqdm import tqdm
from urllib.parse import urljoin, urlsplit, unquote


BOOK_URL = 'https://tululu.org/b{}/'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'
BOOKS_FOLDER = 'books'
IMAGES_FOLDER = 'images'


def save_txt_file(response, filename, books_folder):
    filepath = os.path.join(
        books_folder, f"{sanitize_filename(filename)}.txt"
    )
    with open(filepath, 'w', encoding='utf8') as file:
        file.write(response.text)
    return filepath


def download_image(url, images_folder):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    unquoted_url = unquote(url)
    unquoted_url_path = urlsplit(unquoted_url).path
    filename, extension = os.path.splitext(unquoted_url_path.split('/')[-1])
    timestamp_now = get_timestamp_now()
    new_filename = filename
    if filename != 'nopic':
        new_filename = f'{filename}_{timestamp_now}'
    filepath = os.path.join(
        images_folder, f'{new_filename}{extension}'
    )
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def get_timestamp_now():
    now = datetime.now()
    timestamp_now = round(datetime.timestamp(now))
    return timestamp_now


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_properties(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    response = requests.get(book_url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_page = response.text
    return parse_book_page(book_page)


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')
    title, author, *_ = soup.find('h1').text.split('::')
    title, author = title.strip(), author.strip()
    img_src = soup.select_one(".bookimage img")['src']
    raw_comments = soup.find_all(class_='texts')
    comments = [comment.find('span').text for comment in raw_comments]
    raw_genres = soup.select("span.d_book a")
    genres = [genre.text for genre in raw_genres]
    return {
        'title': title,
        'author': author,
        'img_src': img_src,
        'comments': comments,
        'genres': genres
    }


def get_parsed_arguments():
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги с сайта tululu.org. В качестве '
                    'аргументов принимаются начальный и конечный id книг, а '
                    'также пути до директорий с книгами и изображениями. По'
                    'умолчанию (без указания параметров) скачиваются книги с'
                    'id с 1 до 10 включительно.'
    )
    parser.add_argument('--start_id', type=int, default=1)
    parser.add_argument('--end_id', type=int, default=10)
    parser.add_argument('--books_folder', type=str, default=BOOKS_FOLDER)
    parser.add_argument('--images_folder', type=str, default=IMAGES_FOLDER)
    return parser.parse_args()


def download_book(
        book_id, books_folder, images_folder, url=DOWNLOAD_TXT_URL
):
    book_txt_url = url.format(book_id)
    response = requests.get(book_txt_url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_properties = get_book_properties(book_id)
    filename = f"{book_id}. {book_properties['title']}"
    image_url = urljoin(url, book_properties['img_src'])
    book_properties['book_path'] = \
        save_txt_file(response, filename, books_folder)
    book_properties['img_src'] = download_image(image_url, images_folder)
    return book_properties


def main():
    args = get_parsed_arguments()
    Path(args.books_folder).mkdir(exist_ok=True)
    Path(args.images_folder).mkdir(exist_ok=True)
    downloaded_books = []
    for book_id in tqdm(range(args.start_id, args.end_id + 1)):
        try:
            downloaded_book = download_book(
                book_id, args.books_folder, args.images_folder
            )
            downloaded_books.append(downloaded_book)
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)
    with open('downloaded_books.json', 'w', encoding='utf_8') as file:
        json.dump(downloaded_books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
