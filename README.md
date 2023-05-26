# Books downloader #

Download books from [tululu.org](https://tululu.org)

[Site Example](https://jaggmort.github.io/books_downloader/static/pages/index1.html)

### How to install ###

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```python
pip install -r requirements.txt
```

### How to use ###

How to download science fiction books:

```python
python parse_tululu_category.py --start_page 20 --end_page 30  --dest_folder r:\5 --json_path r:\6 --skip_imgs False --skip_txt False
```

How to get access to books through web:

```python
python render_website.py
```

U will get information in console 
```[I 230523 20:48:40 server:335] Serving on http://127.0.0.1:5500```
Now u can access to books with link [offline-library](http://127.0.0.1:5500/static/pages/index1.html)

Or u can accesss to books if u open any index page from /static/pages/ folder

### Project Goals ###
The code is written for educational purposes on online-course for web-developers [dvmn.org](dvmn.org).
