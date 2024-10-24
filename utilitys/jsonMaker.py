import json
import re
import fitz


def create_toc(file_name):
    """
    Извлекает и возвращает оглавление.

    :param file_name: Название файла с книгой.
    :return: Список оглавления.
    """

    with fitz.open(file_name) as document:
        return document.get_toc()


# То, что желательно было сделать самому. Создает словарь для того самого json файла.
def create_structure(toc):
    """
    Создает словарь структуры книги.

    :param toc: Оглавление книги.
    :return: Словарь структуры книги.
    """

    structure = {}

    for entry in toc:
        level, title, page_num = entry

        # Первый уровень вложенности.
        if 'Глава' == title[:5]:
            title_match = re.search(r"\d+$", title)
            structure[title_match.group()] = {
                'title': toc[toc.index(entry) + 1][1],
                'sections': {},
                'text': ''
            }

        # Второй уровень вложенности.
        sections_match = re.search(r"(^(\d+)\.(\d+)\.?) ", title)
        if sections_match:
            chapter = structure[sections_match.group(2)]

            # Если есть разделы, то поле с текстом к главе не нужно.
            chapter.pop('text', None)

            chapter['sections'][sections_match.group(1)] = {
                'title': title[title.index(' ') + 1:],
                'subsections': {},
                'text': ''
            }

        # Третий уровень вложенности.
        subsections_match = re.search(r"^((\d+)\.(\d+))\.\d+", title)
        if subsections_match:
            sections = structure[subsections_match.group(2)]['sections']

            # Если есть подразделы, то поле с текстом к разделу не нужно.
            sections[subsections_match.group(1)].pop('text', None)

            subsections = sections[f"{subsections_match.group(2)}.{subsections_match.group(3)}"]['subsections']
            subsections[subsections_match.group()] = {
                'title': title[title.index(' ') + 1:],
                'text': ''
            }

    return structure


def write_structure_to_json_file(structure, file_name):
    """
    Записывает структуру книги в json файл.

    :param structure: Заполненный структурой книги словарь.
    :param file_name: Название json файла, в который нужно записать.
    :return:
    """

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=4, ensure_ascii=False)


def make_json(book_file_name, json_file_name):
    """
    Обертка. Полностью создает json файл со структурой книги.

    :param book_file_name: Название файла с книгой.
    :param json_file_name: Название json файла, в который нужно записать.
    :return:
    """

    toc = create_toc(book_file_name)
    structure = create_structure(toc)
    write_structure_to_json_file(structure, json_file_name)


if __name__ == '__main__':
    make_json('../data/book.pdf', 'structure.json')
