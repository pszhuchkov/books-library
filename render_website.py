import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


BOOKS_COUNT_PER_PAGE = 20
COLUMNS_COUNT = 2


def on_reload(books_count_per_page=BOOKS_COUNT_PER_PAGE,
              columns_count=COLUMNS_COUNT):
    template = env.get_template('template.html')

    with open('downloaded_books.json', encoding='utf_8') as file_with_books:
        books = json.load(file_with_books)

    books_divided_into_pages = chunked(books, books_count_per_page)

    for page_num, books_for_one_page in enumerate(books_divided_into_pages, 1):
        books_divided_into_rows = chunked(books_for_one_page, columns_count)
        rendered_page = template.render(books=books_divided_into_rows)
        filepath = os.path.join('pages', f'index{page_num}.html')

        with open(filepath, 'w', encoding="utf8") as page_file:
            page_file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('templates/template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    os.makedirs('pages', exist_ok=True)
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )
    main()
