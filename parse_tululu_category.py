import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from download_books import create_directory, check_for_redirect
from download_books import download_txt, download_image
from download_books import parse_book_page
import sys
import json
import argparse
from pathlib import Path
import pathlib
import os


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
        type=bool,
        help='Игнорировать изображения?',
        default=False,
    )
    parser.add_argument(
        '--skip_txt',
        type=bool,
        help='Игнорировать txt-файлы',
        default=False,
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
        status_forcelist=[400, 500, 502, 503, 504],
    )
    folder = Path(args.dest_folder).resolve()
    session.mount('https://', HTTPAdapter(max_retries=retries))
    for i in range(args.start_page, args.end_page):
        genre_url = f'https://tululu.org/l55/{i}'
        response = session.get(genre_url)
        response.raise_for_status()
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
                    download_txt(txt_url,
                                 params,
                                 f'{book_id}. {title}.txt',
                                 os.path.join(folder, 'Books')
                                 )
                if not args.skip_imgs:
                    download_image(image_url, os.path.join(folder, 'Images'))

                books = {
                    'title': title,
                    'author': author,
                    'img_src': f'images/{book_id}.jpg',
                    'book_path': f'books/{title.strip()}.txt',
                    'comments': [comments],
                    'geners': [genres]
                }
                json_path = folder
                if args.json_path:
                    json_path = os.path.join(args.json_path)
                create_directory(json_path)
                with open(f'{json_path}/books.json',
                          'a',
                          encoding='utf8'
                          ) as my_file:
                    json.dump(books, my_file, ensure_ascii=False)

            except requests.HTTPError:
                print('Txt file is absent', file=sys.stderr)
            except requests.ConnectionError:
                print("Connection error", file=sys.stderr)


if __name__ == '__main__':
    main()
