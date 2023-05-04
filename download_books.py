import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse
from requests.adapters import HTTPAdapter, Retry
import os


def create_directory(directory):
    current_directory = os.path.join(pathlib.Path().resolve(), directory)
    Path(current_directory).mkdir(parents=True, exist_ok=True)


def check_for_redirect(response_history):
    if response_history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    create_directory(folder)
    correct_filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    if check_for_redirect(response.history):
        raise requests.HTTPError
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
    content = soup.find('table').find('div', id='content').find('h1')
    content_text = content.text
    book_header = content_text.split('::')
    title = book_header[0].rstrip(' ').lstrip(' ').strip('\xa0')
    author = book_header[1].rstrip(' ').lstrip(' ').strip('\xa0')

    image_soup = soup.find('div', {'class': 'bookimage'}).find('a')
    image_url = urljoin(url, image_soup.img['src'])

    comments_soup = soup.find_all('div', {'class': 'texts'})
    comments = []
    for comment_soup in comments_soup:
        comments.append(comment_soup.find('span', {'class': 'black'}).text)

    genre = soup.find('span', {'class': 'd_book'}).text

    return title, author, image_url, comments, genre


def main():
    parser = argparse.ArgumentParser(description='Скачивает'
                                     'книги из заданного промежутка с сайта'
                                     'tululu.org'
                                     )
    parser.add_argument('--start_id',
                        type=int,
                        help='Номер начала выборки',
                        default=1,
                        )
    parser.add_argument('--end_id',
                        type=int,
                        help='Номер конца выборки',
                        default=2
                        )
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            params = {'id': f'{book_id}'}
            url = 'https://tululu.org/txt.php'
            session = requests.Session()
            retries = Retry(total=5,
                            backoff_factor=1,
                            status_forcelist=[502, 503, 504]
                            )
            session.mount('https://', HTTPAdapter(max_retries=retries))
            response = session.get(url, params=params)
            response.raise_for_status()
            check_for_redirect(response.history)
            book_page_url = f'https://tululu.org/b{book_id}'
            page_session = requests.Session()
            page_session.mount('https://', HTTPAdapter(max_retries=retries))
            book_page_response = page_session.get(book_page_url)
            book_page_response.raise_for_status
            book_page_parsed_set = parse_book_page(
                book_page_response.text, url
            )
            print(3)
            title, author, image_url, comments, genre = book_page_parsed_set
            print(f'Заголовок: {title}')
            print(f'Автор: {author}', '\n')
        except requests.HTTPError:
            print('Txt file is absent')


if __name__ == '__main__':
    main()
