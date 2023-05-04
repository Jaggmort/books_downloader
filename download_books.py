import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import argparse


def create_directory(directory):
    current_directory = f'{pathlib.Path().resolve()}\{directory}'
    Path(current_directory).mkdir(parents=True, exist_ok=True)


def check_for_redirect(response_history):
    if response_history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    create_directory(folder)
    correct_filename = sanitize_filename(filename)
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response.history)
        filename = f'{folder}\{correct_filename}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)
    except requests.HTTPError:
        print('wrong url')

    return f'{folder}{correct_filename}.txt'


def download_image(url, folder='Images/'):
    create_directory(folder)
    response = requests.get(url)
    response.raise_for_status()
    filename = url.split("/")[-1]
    path = f'{folder}\{filename}'
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('table').find('div', id='content').find('h1')
    content_text = content.text
    book_info = content_text.split('::')
    title = book_info[0].rstrip(' ').lstrip(' ').strip('\xa0')
    author = book_info[1].rstrip(' ').lstrip(' ').strip('\xa0')

    image_soup = soup.find('div', {'class': 'bookimage'}).find('a')
    prepared_url = 'https://tululu.org/'
    image_url = urljoin(prepared_url, image_soup.img['src'])

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
            response = requests.get(url, params=params)
            response.raise_for_status()
            check_for_redirect(response.history)
            url_book_info = f'https://tululu.org/b{book_id}/'
            response_book_info = requests.get(url_book_info)
            response_book_info.raise_for_status
            check_for_redirect(response_book_info.history)
            parse_result = parse_book_page(response_book_info.text)
            title, author, image_url, comments, genre = parse_result
            # download_txt(url, f'{book_id +1}. {title}')
            # download_image(image_url)
            print(f'Заголовок: {title}')
            # for comment in comments:
            #     print(comment)
            # print('image_url', '\n')
            # print(genre, '\n')
            print(f'Автор: {author}', '\n')
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
