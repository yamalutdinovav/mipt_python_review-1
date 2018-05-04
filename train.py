# -*- coding: utf-8 -*-
# Создание частотной модели биграмм на основе набора текстов
# Автор: Артем Ямалутдинов, 1 курс ФИВТ МФТИ
# Ревью №1
# 21 апреля 2018 года

import re
import os
import sys
from collections import Counter
from pickle import dump
import argparse

# Специальный служебный символ для начала и конца строки
ENDSYMBOL = '#'

# Шаблон, по которому производится поиск слов
alphabet = re.compile(u'[a-zA-Zа-яА-яё]+')


def gen_tokens(directory, lc):
    """
    Создает генератор токенов (слов, очищенных от неалфавитных символов)
    на основе текстов с помощью регулярного выражения
    :param directory: Путь к директории, в которой лежат тексты
    :type directory: str
    :param lc: если True, то приводим тексты к lowercase
    :type lc: bool
    :return: Генератор слов, очищенных от неалфавитных символов
    """
    for file in get_files(directory):
        for line in file:
            for token in alphabet.findall(line):
                yield token.lower() if lc else token
            yield ENDSYMBOL  # Отмечаем конец строки


def train(directory, lc):
    """
    Обучение модели (заполнение словаря частот)
    :param directory: Путь к директории, в которой лежат тексты
    :type directory: str
    :param lc: если True, то приводим тексты к lowercase
    :type lc: bool
    :return: Словарь, в котором каждому слову
             сопоставляется следующее за ним и частота вхождения пары
    :rtype: dict
    """
    tokens = list(gen_tokens(directory, lc))
    # Строим модель, сопоставляя каждому слову его последователей
    # и частоты их вхождения
    pairs = Counter(zip(tokens[:-1], tokens[1:]))
    model = {token: {next_token: frequency
                     for (token_1, next_token), frequency in pairs.items()
                     if token_1 == token}
             for (token, next_token), frequency in pairs.items()}
    return model


def get_files(path):
    """
    Рекурсивный проход передаваемой директории
    с целью поиска файлов для обучения
    :param path: Директория, в которой лежат файлы
    :type path: str
    :return: Список нормализованных путей до текстовых файлов
    :rtype: generator
    """
    if path is None:
        yield sys.stdin
    else:
        # Рекурсивно обходим директорию
        for path, directories, files in os.walk(path):
            for file in files:
                # Отсекаем файлы типа ".Git" и др.
                if file[0] != '.':
                    file_path = str(os.path.join(path, file))
                    # Проверяем разрешение рассматриваемого файла
                    name, extension = os.path.splitext(file_path)
                    if extension == '.txt':
                        # Нормализуем путь до файла
                        with open(os.path.normpath(file_path), 'r') as data:
                            yield data


def write_train_result(model, directory, lc):
    """
    Запись модели в указанный файл
     :param model: Путь к файлу, в который сохраняется модель
     :type model: str
     :param directory: Путь к директории, в которой лежат тексты
     :type directory: str
     :param lc: если True, то приводим тексты к lowercase
     :type lc: bool
    """
    with open(model, 'wb') as data:
        model = train(directory, lc)
        dump(model, data)


if __name__ == "__main__":
    # Аргументы командной строки:
    parse = argparse.ArgumentParser(
        description='Обучение генератора текстов на основе биграмм')
    parse.add_argument('--input-dir',
                       help='Путь к директории, '
                            'в которой лежат тексты для обучения. '
                            'Если не указана, текст вводится из stdin',
                       dest='dir')
    parse.add_argument('--model', help='Обязательный аргумент. Путь к файлу, '
                                       'в который сохраняется модель '
                                       '(словарь с биграммами)',
                       required=True)
    parse.add_argument('--lc', help='Необязательный аргумент. '
                                    'Приводить слова в модели к lowercase',
                       action='store_true')
    namespace = parse.parse_args()
    write_train_result(namespace.model, namespace.dir, namespace.lc)
