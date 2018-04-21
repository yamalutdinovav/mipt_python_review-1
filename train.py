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

# Аргументы командной строки:
parse = argparse.ArgumentParser(
    description='Обучение генератора текстов на основе биграмм')
parse.add_argument('--input-dir',
                   help='Путь к директории, '
                        'в которой лежат тексты для обучения. '
                   'Если не указана, текст вводится из stdin',
                   dest='dir')
parse.add_argument('--model', help='Обязательный аргумент. '
                   'Путь к файлу, в который сохраняется модель '
                                   '(словарь с биграммами)',
                   required=True)
parse.add_argument('--lc', help='Необязательный аргумент. '
                   'Приводить слова в модели к lowercase',
                   action='store_true')
namespace = parse.parse_args()


def gen_tokens(dir, lc):
    """
    Создает генератор токенов (слов, очищенных от неалфавитных символов)
    на основе текстов с помощью регулярного выражения
    :param dir: Путь к директории, в которой лежат тексты
    :type dir: str
    :param lc: если True, то приводим тексты к lowercase
    :type lc: bool
    :return: Генератор слов, очищенных от неалфавитных символов
    """
    # Получим список .txt файлов для обучения
    if dir:
        corpus = get_files(dir)
    # Иначе производим консольный ввод
    else:
        corpus = [sys.stdin]
    for input_data in corpus:
        if dir:
            input_data = open(input_data, 'r')
            for line in input_data.readlines():
                for token in alphabet.findall(line):
                    yield token.lower() if lc else token
                if dir:
                    input_data.close()
                yield ENDSYMBOL  # Отмечаем конец строки


def gen_bigramms(tokens):
    """
    Создает генератор биграмм – пар слов вида (слово1, слово2)
    на основе генератора токенов
    :param tokens: Генератор токенов
    :type tokens: generator
    :return: Генератор биграмм
    :rtype: generator
    """
    token_0 = ENDSYMBOL
    for token_1 in tokens:
        yield token_0, token_1
        token_0 = token_1
    yield token_0, ENDSYMBOL


def train(dir, lc):
    """
    Обучение модели (заполнение словаря частот)
    :param dir: Путь к директории, в которой лежат тексты
    :type dir: str
    :param lc: если True, то приводим тексты к lowercase
    :type lc: bool
    :return: Словарь, в котором каждому слову
             сопоставляется следующее за ним и частота вхождения пары
    :rtype: dict
    """
    tokens = gen_tokens(dir, lc)
    bigramms = gen_bigramms(tokens)
    # Подсчитаем частоту вхождения биграмм,
    # кроме биграммы из двух служебных символов
    pairs = {(token_0, token_1): frequency
             for (token_0, token_1), frequency in Counter(bigramms).items()
             if (token_0, token_1) != (ENDSYMBOL, ENDSYMBOL)}
    # Строим модель, сопоставляя каждому слову его последователей
    # и частоты их вхождения
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
    :rtype: list
    """
    txt_files = []
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
                    txt_files.append(os.path.normpath(file_path))
    return txt_files


def write_train_result(model, dir, lc):
    """
    Запись модели в указанный файл
     :param model: Путь к файлу, в который сохраняется модель
     :type model: str
     :param dir: Путь к директории, в которой лежат тексты
     :type dir: str
     :param lc: если True, то приводим тексты к lowercase
     :type lc: bool
    """
    with open(model, 'wb') as data:
        model = train(dir, lc)
        dump(model, data)


if __name__ == "__main__":
    write_train_result(namespace.model, namespace.dir, namespace.lc)
