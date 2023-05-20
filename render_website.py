from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
import warnings
import os
from dotenv import load_dotenv
import json


def on_reload():
    load_dotenv()
    warnings.filterwarnings("ignore")
    json_path = os.environ.get('JSON_PATH')
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    with open(json_path, 'r', encoding='utf8') as file:
        books = json.load(file)

    for book in books:
        if not os.path.isfile(book['img_src']):
            book['img_src'] = 'no_file'
    rendered_page = template.render(
        books=books,
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
