import json
import fitz


def get_book_text(file_name):
    """
    Постранично читает всю книгу и составляет ее общий текст.

    :param file_name: Название файла с книгой.
    :return: Общий текст книги.
    """

    with fitz.open(file_name) as document:
        book_text = ''
        for page_number in range(len(document)):
            text = document.load_page(page_number).get_text()
            book_text += text
        return book_text


def get_structure_from_json(file_name):
    """
    Читает json файл структуры и возвращает словарь для дальнейшего заполнения тестом.

    :param file_name: Название json файла со структурой книги.
    :return: Словарь, соответствующий структуре книги.
    """

    with open(file_name, encoding='utf-8') as f:
        return json.load(f)


def book_parser(book_file_name, json_file_name):
    """
    Парсит книгу и заполняет соответствующий json файл.

    :param book_file_name: Название файла с книгой.
    :param json_file_name: Название json файла со структурой книги.
    :return: Заполненный текстами глав/разделов/подразделов словарь.
    """

    book_text = get_book_text(book_file_name)
    structure = get_structure_from_json(json_file_name)

    # Разделил весь текст книги на текст по главам.
    # Не беру никакого текста до глав (делаю срез), так как изначальный json не содержит соответствующих ключей.
    text_of_the_chapters = book_text.split('ГЛАВА')[1:]

    for chapter_index, chapter_text in enumerate(text_of_the_chapters):

        sections = structure[f"{chapter_index + 1}"]['sections']

        # Не каждая глава содержит разделы.
        if sections == {}:
            structure[f"{chapter_index + 1}"]['text'] = chapter_text  # Записываю текст просто для главы.
            continue

        sections_titles = [(sections[section_number]['title']).upper() for section_number in sections]

        # Составляю список из координат начала каждого раздела в тексте соответствующей главы.
        # Пара чисел нынешнее и следующее значение (i, i + 1) - начало и конец одного раздела.
        sections_start_end_indexes = []
        find_position = 0  # Чтобы не искать там, где уже искал.
        for section_title in sections_titles:
            find_position = chapter_text.find(section_title.split()[0], find_position)
            sections_start_end_indexes.append(find_position)
        sections_start_end_indexes.append(len(chapter_text))  # Конец последнего раздела - конец главы.

        # Записываю текст (срез главы) в соответствующее место.
        for section_index, section in enumerate(sections):
            if sections[section]['subsections'] == {}:  # Записываю, только если нет подраздела. Так бы записывал туда.
                section_start = section_index
                section_end = section_index + 1
                sections[section]['text'] = chapter_text[sections_start_end_indexes[section_start]: sections_start_end_indexes[section_end]]

        all_subsections_indexes = []  # Список для списков координат каждого подраздела.
        for section in sections:
            subsections = sections[section]['subsections']

            # Не каждый раздел содержит подразделы.
            if subsections == {}:
                continue

            subsection_titles = [subsections[subsection_number]['title'] for subsection_number in subsections]
            subsections_start_end_indexes = [chapter_text.find(name) for name in subsection_titles]
            all_subsections_indexes.append(subsections_start_end_indexes)

        # Дополняю каждый списочек, соответствующий одному разделу, концом последнего подраздела,
        # то есть началом следующего раздела, а если подраздел последний - концом главы.
        for i in range(len(all_subsections_indexes)):
            if i == len(all_subsections_indexes) - 1:  # Последний.
                all_subsections_indexes[-1].append(len(chapter_text))
            else:
                all_subsections_indexes[i].append(all_subsections_indexes[i + 1][0])

        i = j = 0
        for section in sections:
            subsections = sections[section]['subsections']

            # Не каждый раздел содержит подразделы.
            if subsections == {}:
                continue

            # Записываю текста подразделов в соответствующее место.
            for subsection in subsections:
                subsections[subsection]['text'] = chapter_text[all_subsections_indexes[i][j]: all_subsections_indexes[i][j + 1]]
                j += 1
            i += 1
            j = 0

    return structure


def write_parsed_book_to_json_file(structure, file_name):
    """
    Записывает заполненный словарь в json файл.

    :param structure: Заполненный текстами глав/разделов/подразделов словарь.
    :param file_name: Название json файла, в который нужно записать.
    :return:
    """

    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(structure, file, ensure_ascii=False, indent=4)
