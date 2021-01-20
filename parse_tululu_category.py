import argparse
import json
import sys
import time

import requests
import urllib3

from pathlib import Path
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError, ConnectionError
from urllib.parse import urljoin
from parse_tululu import download_book, BOOKS_FOLDER, IMAGES_FOLDER, BOOK_URL,\
    check_for_redirect


COLLECTION_URL = 'https://tululu.org/l55/'


def get_parsed_arguments():
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги определенной коллекции '
                    'с сайта tululu.org. '
                    'В качестве аргументов принимаются начальная и конечная '
                    'страницы, а также пути до директорий с книгами и '
                    'изображениями.'
    )
    parser.add_argument('--start_page', type=int, default=1)
    parser.add_argument('--end_page', type=int)
    parser.add_argument('--books_folder', type=str, default=BOOKS_FOLDER)
    parser.add_argument('--images_folder', type=str, default=IMAGES_FOLDER)
    return parser.parse_args()


def get_amount_pages(url):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    page_numbers = soup.select('.npage')
    if page_numbers:
        last_page_number = int(page_numbers[-1].string)
        return last_page_number
    return 1


def download_books_on_page(url, books_folder, images_folder):
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
                book_id, books_folder, images_folder
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
    Path(args.books_folder).mkdir(exist_ok=True)
    Path(args.images_folder).mkdir(exist_ok=True)
    downloaded_books = []
    start_page = args.start_page
    end_page = args.end_page or get_amount_pages(COLLECTION_URL)
    for page_number in range(start_page, end_page + 1):
        url = urljoin(COLLECTION_URL, str(page_number))
        try:
            downloaded_books.extend(
                download_books_on_page(
                    url, args.books_folder, args.images_folder
                )
            )
            print(f'Обработка страницы {page_number} завершена')
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
