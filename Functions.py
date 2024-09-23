import ebooklib                                                     # type: ignore
from ebooklib import epub                                           # type: ignore
from bs4 import BeautifulSoup                                       # type: ignore



def book(book_input):
    book = epub.read_epub(book_input)
    text = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html_doc = item.get_content()
            soup = BeautifulSoup(html_doc, 'html.parser')
            text += soup.get_text() + " "
    return text