import json
import os
import sys
import time

import requests
import urllib3

from pathlib import Path
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError
from urllib.parse import urljoin
from parse_tululu import download_book, check_for_redirect
from helpers import get_parsed_arguments, BOOK_URL


def get_amount_pages(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    page_numbers = soup.select('.npage')
    if page_numbers:
        last_page_number = int(page_numbers[-1].string)
        return last_page_number
    return 1


def download_books_on_page(url, books_folder, images_folder,
                           skip_txt, skip_img):
    downloaded_books_on_page = []
    response = requests.get(url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    books_cards = soup.select("table.d_book")
    for book_card in books_cards:
        book_url = book_card.find('a')['href']
        book_id = book_url[2:-1]
        try:
            downloaded_book = download_book(
                book_id, books_folder, images_folder, skip_txt, skip_img
            )
            downloaded_books_on_page.append(downloaded_book)
            print(f'Сохранена книга: {BOOK_URL.format(book_id)}')
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)
    return downloaded_books_on_page


def main():
    args = get_parsed_arguments()
    target_books_dir = os.path.join(args.dest_dir, args.books_dirname)
    target_images_dir = os.path.join(args.dest_dir, args.images_dirname)
    Path(target_books_dir).mkdir(exist_ok=True)
    Path(target_images_dir).mkdir(exist_ok=True)
    downloaded_books = []
    start_page = args.start_page
    end_page = args.end_page or get_amount_pages(args.collection_url)
    for page_number in range(start_page, end_page + 1):
        url = urljoin(args.collection_url, str(page_number))
        try:
            downloaded_books.extend(
                download_books_on_page(
                    url, target_books_dir, target_images_dir, args.skip_txt,
                    args.skip_img
                )
            )
            print(f'Обработка страницы {page_number} завершена')
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)

    result_filepath = \
        args.json_path or os.path.join(args.dest_dir, 'downloaded_books.json')
    with open(result_filepath, 'w', encoding='utf_8') as file:
        json.dump(downloaded_books, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
