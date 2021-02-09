import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def on_reload():
    template = env.get_template('template.html')
    with open('downloaded_books.json', encoding='utf_8') as file_with_books:
        books = json.load(file_with_books)

    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding="utf8") as index_page:
        index_page.write(rendered_page)


def main():

    on_reload()

    server = Server()
    server.watch('templates/template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html'])
    )
    main()
