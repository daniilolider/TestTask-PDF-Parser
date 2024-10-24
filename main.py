from utilitys.jsonMaker import make_json
from utilitys.bookParser import book_parser, write_parsed_book_to_json_file

book_file_name = 'data/book.pdf'
json_file_name = 'result.json'

make_json(book_file_name, json_file_name)
parsed_book = book_parser(book_file_name, json_file_name)
write_parsed_book_to_json_file(parsed_book, json_file_name)
