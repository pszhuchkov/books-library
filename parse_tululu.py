import requests
import urllib3
import os
import argparse
from pathlib import Path
from requests.exceptions import HTTPError
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, unquote
from tqdm import tqdm
from datetime import datetime


BOOK_URL = 'https://tululu.org/b{}/'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'
BOOKS_FOLDER = 'books'
IMAGES_FOLDER = 'images'


def save_txt_file(response, filename, books_folder=BOOKS_FOLDER):
    filepath = os.path.join(
        books_folder, f"{sanitize_filename(filename)}.txt"
    )
    with open(filepath, 'w', encoding='utf8') as file:
        file.write(response.text)
    return filepath


def download_image(url, images_folder=IMAGES_FOLDER):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    unquoted_url = unquote(url)
    unquoted_url_path = urlsplit(unquoted_url).path
    filename, extension = os.path.splitext(unquoted_url_path.split('/')[-1])
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
            save_txt_file(response, filename)
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
    book_name, author, *_ = soup.find('h1').text.split('::')
    book_name, author = book_name.strip(), author.strip()
    relative_image_url = soup.find(class_='bookimage').find('img')['src']
    absolute_image_url = urljoin(url, relative_image_url)
    raw_comments = soup.find_all(class_='texts')
    comments = [comment.find('span').text for comment in raw_comments]
    raw_genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in raw_genres]
    return {
        'name': book_name,
        'author': author,
        'image_url': absolute_image_url,
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


def download_book(book_id, url=DOWNLOAD_TXT_URL):
    book_txt_url = url.format(book_id)
    response = requests.get(book_txt_url, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    book_properties = get_book_properties(book_id)
    filename = f"{book_id}. {book_properties['name']}"
    save_txt_file(response, filename)
    download_image(book_properties['image_url'])


def main():
    Path(BOOKS_FOLDER).mkdir(exist_ok=True)
    Path(IMAGES_FOLDER).mkdir(exist_ok=True)
    args = get_parsed_arguments()
    for book_id in tqdm(range(args.start_id, args.end_id + 1)):
        try:
            download_book(book_id)
        except ConnectionError as conn_err:
            print(conn_err, file=sys.stderr)
            time.sleep(5)
        except HTTPError as http_err:
            print(http_err, file=sys.stderr)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
