import json
import glob
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathlib import Path
from constants import BOOKS_COUNT_PER_PAGE, COLUMNS_COUNT, HTML_PAGES_DIRNAME


def render_pages_from_template(books_count_per_page=BOOKS_COUNT_PER_PAGE,
                               columns_count=COLUMNS_COUNT):
    template = env.get_template('template.html')

    with open('downloaded_books.json', encoding='utf_8') as file_with_books:
        books = json.load(file_with_books)

    books_divided_into_pages = list(chunked(books, books_count_per_page))
    pages_count = len(books_divided_into_pages)
    actual_files = []
    for page_num, books_for_one_page in enumerate(books_divided_into_pages, 1):
        books_divided_into_rows = chunked(books_for_one_page, columns_count)
        rendered_page = template.render(books=books_divided_into_rows,
                                        pages_count=pages_count,
                                        current_page=page_num)
        filepath = os.path.join('pages', f'index{page_num}.html')

        with open(filepath, 'w', encoding="utf8") as page_file:
            page_file.write(rendered_page)

        actual_files.append(filepath)
    remove_redundant_files(actual_files, target_directory)


def remove_redundant_files(actual_files, directory, extension='html'):
    files_in_directory = glob.glob(f'{directory}/*.{extension}')
    for file in files_in_directory:
        if file not in actual_files:
            os.remove(file)


if __name__ == '__main__':
    os.makedirs(HTML_PAGES_DIRNAME, exist_ok=True)
    remove_files_from_directory()

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIRNAME),
                      autoescape=select_autoescape(['html']))
    render_pages_from_template()

    server = Server()
    server.watch('templates/template.html', render_pages_from_template)
    server.serve(root='.')
