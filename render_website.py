import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html'])
)
template = env.get_template('template.html')


with open('downloaded_books.json', encoding='utf_8') as file:
    books = json.load(file)

rendered_page = template.render(books=books)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
