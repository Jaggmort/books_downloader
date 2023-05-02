import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename


def create_directory(directory):
    current_directory=f'{pathlib.Path().resolve()}\{directory}'
    Path(current_directory).mkdir(parents=True, exist_ok=True)

def check_for_redirect(response_history):
    if response_history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    create_directory(folder)
    correct_filename =  sanitize_filename(filename)
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


def get_name(url):
    title = ''
    response = requests.get(url)
    response.raise_for_status()
    try: 
        soup = BeautifulSoup(response.text, 'lxml')              
        content = soup.find('table').find('div', id = 'content').find('h1')
        content_text = content.text
        book_info = content_text.split('::')
        title = book_info[0].rstrip(' ').lstrip(' ').strip('\xa0')
    except AttributeError:
        pass
    return title


def main():
    directory = 'books'
    create_directory(directory)
    for book_id in range(10):
        url_title = f'https://tululu.org/b{book_id + 1}/'
        title = get_name(url_title)
        url = f'https://tululu.org/txt.php?id={book_id + 1}'     
        download_txt(url, f'{book_id +1}. {title}')


if __name__ == '__main__':
    main()
