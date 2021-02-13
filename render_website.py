import json
import glob
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from functools import partial
from livereload import Server
from more_itertools import chunked
from constants import BOOKS_COUNT_PER_PAGE, COLUMNS_COUNT,\
    HTML_PAGES_DIRNAME, TEMPLATE_DIRNAME, TEMPLATE_FILENAME
from helpers import get_parsed_arguments


def render_pages_from_template(file_with_results,
                               template_filename,
                               books_count_per_page=BOOKS_COUNT_PER_PAGE,
                               columns_count=COLUMNS_COUNT,
                               target_directory=HTML_PAGES_DIRNAME):

    template = env.get_template(template_filename)

    with open(file_with_results, encoding='utf_8') as file_with_books:
        books = json.load(file_with_books)

    books_divided_into_pages = list(chunked(books, books_count_per_page))
    pages_count = len(books_divided_into_pages)
    actual_files = []
    for page_num, books_for_one_page in enumerate(books_divided_into_pages, 1):
        books_divided_into_rows = chunked(books_for_one_page, columns_count)
        rendered_page = template.render(books=books_divided_into_rows,
                                        pages_count=pages_count,
                                        current_page=page_num)
        filepath = os.path.join(target_directory, f'index{page_num}.html')

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

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIRNAME),
                      autoescape=select_autoescape(['html']))

    args = get_parsed_arguments()
    result_filepath = args.json_path or os.path.join(args.dest_dir,
                                                     'downloaded_books.json')

    render_pages_from_template = partial(render_pages_from_template,
                                         result_filepath, TEMPLATE_FILENAME)

    render_pages_from_template()

    server = Server()
    server.watch('templates/template.html', render_pages_from_template)
    server.serve(root='.')
