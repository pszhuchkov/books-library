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
        books_folder, f"{sanitize_filename(filename)}.txt"
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
            pass
            # filename, image_url = get_bookinfo(book_id)
            # download_txt(response, filename)
            # download_image(image_url)


def get_bookinfo(book_id, url=BOOK_URL):
    book_url = url.format(book_id)
    response = requests.get(book_url, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_name = soup.find('h1').text.split('::')[0].strip()
    filename = f"{book_id}. {book_name}"

    image_url = soup.find(class_='bookimage').find('img')['src']
    image_url_full = urljoin(url, image_url)

    comments = soup.find_all(class_='texts')
    comments_clean = [comment.find('span').text for comment in comments]

    genres = soup.find('span', class_='d_book')
    genres_a = genres.find_all('a')
    genres_lst = [genre.text for genre in genres_a]
    print(genres_lst)


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
    download_books(DOWNLOAD_TXT_URL, 1, 10)
