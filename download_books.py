import requests
import pathlib
from pathlib import Path

def create_directory(directory):
    current_directory=f'{pathlib.Path().resolve()}\{directory}'
    Path(current_directory).mkdir(parents=True, exist_ok=True)  

def main():
    directory = 'books'
    create_directory(directory)
    for book_id in range(10):
        url = f'https://tululu.org/txt.php?id={book_id+1}'
        response = requests.get(url)
        response.raise_for_status() 

        filename = f'{directory}\{book_id+1}.txt'
        with open(filename, 'wb') as file:
            file.write(response.content)

if __name__ == '__main__':
    main()
