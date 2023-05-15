# Books downloader #

Download books from [tululu.org](https://tululu.org)

### How to install ###

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```python
pip install -r requirements.txt
```

### How to use ###

How to download books:
```python
python download_books.py --start_id 20 --end_id 30
```

How to download science fiction books:

```python
python parse_tululu_category.py --start_page 20 --end_page 30  --dest_folder r:\5 --json_path r:\6 --skip_imgs False --skip_txt False
```

### Project Goals ###
The code is written for educational purposes on online-course for web-developers [dvmn.org](dvmn.org).
