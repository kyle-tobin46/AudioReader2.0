from Functions import book

import ebooklib                                                     # type: ignore
from ebooklib import epub                                           # type: ignore

import warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

#print(egg.get_metadata('DC', 'creator'))

#print(extract_chapters('books/the-egg.epub'))
book = epub.read_epub('books/the-egg.epub')

print(book.get_metadata('DC', 'creator'))
