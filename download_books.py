import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
from requests.adapters import HTTPAdapter, Retry
import os
import sys


def create_directory(directory):
    current_directory = os.path.join(pathlib.Path().resolve(), directory)
    Path(current_directory).mkdir(parents=True, exist_ok=True)


def check_for_redirect(response_history):
    if response_history:
        raise requests.HTTPError


def download_txt(url, params, filename, folder='Books/'):
    create_directory(folder)
    correct_filename = sanitize_filename(filename)
    print(filename)
    response = requests.get(url, params=params)
    response.raise_for_status()
    filename = os.path.join(folder, correct_filename)
    with open(filename, 'wb') as file:
        file.write(response.content)
    return filename


def download_image(url, folder='Images/'):
    create_directory(folder)
    response = requests.get(url)
    response.raise_for_status()
    filename = url.split("/")[-1]
    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(html, url):
    soup = BeautifulSoup(html, 'lxml')
    content_text = soup.select_one('table #content h1').text
    book_header = content_text.split('::')
    title = book_header[0].rstrip(' ').lstrip(' ').strip('\xa0')
    author = book_header[1].rstrip(' ').lstrip(' ').strip('\xa0')

    image_soup = soup.select_one('div.bookimage a')
    image_url = urljoin(url, image_soup.img['src'])

    comments_soup = soup.select('div.texts')
    comments = []
    for comment_soup in comments_soup:
        comments.append(comment_soup.select_one('span.black').text)

    genres_soup = soup.select_one('span.d_book').select('a')
    genres = []
    for genre_soup in genres_soup:
        genres.append(genre_soup.text)
    return title, author, image_url, comments, genres


def main():
    parser = argparse.ArgumentParser(
        description='Скачивает книги из заданного промежутка'
        'с сайта tululu.org'
    )
    parser.add_argument(
        '--start_id',
        type=int,
        help='Номер начала выборки',
        default=1,
    )
    parser.add_argument(
        '--end_id',
        type=int,
        help='Номер конца выборки',
        default=2,
    )
    args = parser.parse_args()

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[400, 500, 502, 503, 504],
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for book_id in range(args.start_id, args.end_id):
        try:
            params = {'id': f'{book_id}'}
            url = 'https://tululu.org/txt.php'
            response = session.get(url, params=params)
            response.raise_for_status()
            check_for_redirect(response.history)

            book_page_url = f'https://tululu.org/b{book_id}/'
            book_page_response = session.get(book_page_url)
            book_page_response.raise_for_status()
            check_for_redirect(book_page_response.history)

            book_page_parsed = parse_book_page(
                book_page_response.text, url
            )
            title, author, image_url, comments, genres = book_page_parsed
            download_txt(url, params, f'{book_id}. {title}.txt')
            download_image(image_url)

            print(f'Заголовок: {title}')
            print(f'Автор: {author}', '\n')
        except requests.HTTPError:
            print('Txt file is absent', file=sys.stderr)
        except requests.ConnectionError:
            print("Connection error", file=sys.stderr)


if __name__ == '__main__':
    main()
