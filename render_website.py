import json
import os
import pathlib
from pathlib import Path
import warnings

from dotenv import load_dotenv
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def create_directory(directory):
    current_directory = os.path.join(pathlib.Path().resolve(), directory)
    Path(current_directory).mkdir(parents=True, exist_ok=True)


def on_reload():
    load_dotenv()
    warnings.filterwarnings('ignore')
    json_path = os.environ.get('JSON_PATH')
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('static/template.html')
    create_directory('static/pages')
    json_path = os.path.join('media/', json_path)
    with open(json_path, 'r', encoding='utf8') as file:
        books = json.load(file)

    for book in books:
        if not os.path.isfile(book['img_src']):
            book['img_src'] = 'no_file'

    books_per_row = 2
    chunked_books = list(chunked(books, books_per_row))
    rows_per_page = 10
    books_on_pages = list(chunked(chunked_books, rows_per_page))
    number_of_pages = len(books_on_pages)
    for page_index, books_on_page in enumerate(books_on_pages, start=1):
        rendered_page = template.render(
            books=books_on_page,
            index=page_index,
            number_of_pages=number_of_pages
        )
        with open(
            f'./static/pages/index{page_index}.html',
            'w', encoding='utf8'
        ) as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
