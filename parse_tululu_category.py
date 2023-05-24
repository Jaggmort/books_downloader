import argparse
import json
import os
import pathlib
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

from download_books import create_directory, check_for_redirect
from download_books import download_txt, download_image
from download_books import parse_book_page


def main():
    parser = argparse.ArgumentParser(
        description='Скачивает книги по научной фантастике с заданных страниц'
        'с сайта tululu.org'
    )
    parser.add_argument(
        '--start_page',
        type=int,
        help='Номер первой страницы для скачивания',
        default=1,
    )
    parser.add_argument(
        '--end_page',
        type=int,
        help='Номер последней страницы для скачивания',
        default=2,
    )
    parser.add_argument(
        '--dest_folder',
        help='Путь для хранения файлов',
        default=pathlib.Path().resolve(),
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
        help='Игнорировать изображения?',
    )
    parser.add_argument(
        '--skip_txt',
        action='store_true',
        help='Игнорировать txt-файлы',
    )
    parser.add_argument(
        '--json_path',
        help='Путь к json-файлу с описанием книг',
    )
    args = parser.parse_args()

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[400, 404, 500, 502, 503, 504],
    )
    folder = Path(args.dest_folder).resolve()
    session.mount('https://', HTTPAdapter(max_retries=retries))
    books = []
    for page_id in range(args.start_page, args.end_page):
        try:
            genre_url = f'https://tululu.org/l55/{page_id}'
            response = session.get(genre_url)
            response.raise_for_status()
            check_for_redirect(response.history)
        except requests.HTTPError:
            print('Page does not exists', file=sys.stderr)
            continue
        except requests.ConnectionError:
            print(f'Can not connect to {genre_url}')
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        tululu_books = soup.select_one('#content').select('div.bookimage')
        for tululu_book in tululu_books:
            try:
                book_id = tululu_book.a["href"][2:-1]
                params = {'id': f'{book_id}'}
                txt_url = 'https://tululu.org/txt.php'
                response = session.get(txt_url, params=params)
                response.raise_for_status()
                check_for_redirect(response.history)

                book_page_url = urljoin(genre_url, tululu_book.a['href'])
                book_page_response = session.get(book_page_url)
                book_page_response.raise_for_status()
                check_for_redirect(book_page_response.history)

                book_page_parsed = parse_book_page(
                    book_page_response.text, txt_url
                )
                title, author, image_url, comments, genres = book_page_parsed
                if not args.skip_txt:
                    download_txt(
                        txt_url,
                        params,
                        f'{book_id}. {title}.txt',
                        os.path.join(folder, 'media/books')
                    )
                if not args.skip_imgs:
                    download_image(image_url, os.path.join(folder,
                                                           'media/images'))

                book = {
                    'title': title,
                    'author': author,
                    'img_src': f'media/images/{book_id}.jpg',
                    'book_path': f'media/books/{book_id}. {title}.txt',
                    'comments': [comments],
                    'genres': [genres]
                }
                books.append(book)

            except requests.HTTPError:
                print('Txt file is absent', file=sys.stderr)
            except requests.ConnectionError:
                print("Connection error", file=sys.stderr)

    json_path = folder
    if args.json_path:
        json_path = os.path.join(args.json_path)
    json_path = os.path.join(folder, 'media/')
    create_directory(json_path)
    with open(f'{json_path}/books.json', 'w', encoding='utf8') as file:
        json.dump(books, file, ensure_ascii=False)


if __name__ == '__main__':
    main()
