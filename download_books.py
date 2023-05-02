import requests
import pathlib
from bs4 import BeautifulSoup
from pathlib import Path
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, urljoin

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


def download_image(url, folder='Images/'):
    create_directory(folder)
    response = requests.get(url)
    response.raise_for_status()
    filename = url.split("/")[-1]
    path = f'{folder}\{filename}'
    with open(path, 'wb') as file:
        file.write(response.content)


def get_book_information(url):
    title = ''
    image_url = ''
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response.history)
        soup = BeautifulSoup(response.text, 'lxml')              
        content = soup.find('table').find('div', id = 'content').find('h1')
        content_text = content.text
        book_info = content_text.split('::')
        title = book_info[0].rstrip(' ').lstrip(' ').strip('\xa0')

        image_soup = soup.find('div', {'class':'bookimage'}).find('a')
        url_netlock = urlparse(url).netloc
        prepared_url = f'https://{url_netlock}'
        image_url = urljoin(prepared_url, image_soup.img['src'])

        comments_soup = soup.find_all('div', {'class':'texts'})
        comments = []
        for comment_soup in comments_soup:
            comments.append(comment_soup.find('span', {'class':'black'}).text)
        
        genre_soup = soup.find('span', {'class':'d_book'}).text
            
    except requests.HTTPError:
        pass

    return title, image_url, comments, genre_soup


def main():
    directory = 'books'
    create_directory(directory)
    for book_id in range(10):
        try:
            url = f'https://tululu.org/txt.php?id={book_id + 1}'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response.history)                                 
            url_title = f'https://tululu.org/b{book_id + 1}/'
            title, image_url, comments, genre = get_book_information(url_title)     
            #download_txt(url, f'{book_id +1}. {title}')
            #download_image(image_url)
            print(f'Заголовок: {title}')
            #for comment in comments:
            #    print(comment)
            #print('image_url', '\n')
            print(genre, '\n')
        except requests.HTTPError:
            pass

if __name__ == '__main__':
    main()
