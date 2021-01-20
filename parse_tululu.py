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
from urllib.parse import urljoin, urlsplit, unquote
from constants import BOOK_URL, DOWNLOAD_TXT_URL
from helpers import get_parsed_arguments


def save_txt_file(response, filename, books_dir):
    filepath = os.path.join(books_dir, f"{sanitize_filename(filename)}.txt")
    with open(filepath, 'w', encoding='utf8') as file:
        file.write(response.text)
    return filepath


def download_image(url, images_dir):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    unquoted_url = unquote(url)
    unquoted_url_path = urlsplit(unquoted_url).path
    filename, extension = os.path.splitext(unquoted_url_path.split('/')[-1])
    timestamp_now = get_timestamp_now()
    new_filename = filename
    if filename != 'nopic':
        new_filename = f'{filename}_{timestamp_now}'
    filepath = os.path.join(images_dir, f'{new_filename}{extension}')
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def get_timestamp_now():
    now = datetime.now()
    timestamp_now = round(datetime.timestamp(now))
    return timestamp_now


def check_for_redirect(response):
    if response.history:
        raise HTTPError('Redirected')


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
    raw_comments = soup.select('.texts')
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


def download_book(
        book_id, books_dir, images_dir, skip_txt,
        skip_img, url=DOWNLOAD_TXT_URL):
    book_txt_url = url.format(book_id)
    response = requests.get(book_txt_url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_properties = get_book_properties(book_id)
    if not skip_txt:
        filename = f"{book_id}. {book_properties['title']}"
        book_properties['book_path'] = save_txt_file(response, filename,
                                                     books_dir)
    if not skip_img:
        image_url = urljoin(url, book_properties['img_src'])
        book_properties['img_src'] = download_image(image_url, images_dir)
    else:
        del book_properties['img_src']
    return book_properties


def create_books_and_images_dirs(args):
    target_books_dir = os.path.join(args.dest_dir, args.books_dirname)
    target_images_dir = os.path.join(args.dest_dir, args.images_dirname)
    Path(target_books_dir).mkdir(exist_ok=True)
    Path(target_images_dir).mkdir(exist_ok=True)
    return target_books_dir, target_images_dir


def main():
    args = get_parsed_arguments()
    target_books_dir, target_images_dir = create_books_and_images_dirs(args)
    downloaded_books = []
    for book_id in range(args.start_id, args.end_id + 1):
        try:
            downloaded_book = download_book(
                book_id, target_books_dir, target_images_dir,
                args.skip_txt, args.skip_img)
            downloaded_books.append(downloaded_book)
            print(f'Сохранена книга: {BOOK_URL.format(book_id)}')
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)

    result_filepath = args.json_path or os.path.join(args.dest_dir,
                                                     'downloaded_books.json')
    with open(result_filepath, 'w', encoding='utf_8') as file:
        json.dump(downloaded_books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
