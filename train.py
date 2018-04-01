# -*- coding: utf-8 -*-

import re
import os
import sys
from collections import defaultdict
from pickle import dump
import argparse

# Шаблон, по которому производится поиск слов
alphabet = re.compile(u'[a-zA-Zа-яА-яё-]+')

# Аргументы командной строки:
parse = argparse.ArgumentParser()
parse.add_argument('--input-dir',
                   help='Путь к директории, в которой лежат документы. '
                   'Если не указана, текст вводится из stdin',
                   dest='dir')
parse.add_argument('--model', help='Обязательный аргумент. '
                   'Путь к файлу, в который сохраняется модель',
                   required=True)
parse.add_argument('--lc', help='Необязательный аргумент. '
                   'Приводить тексты к lowercase',
                   action='store_true')
namespace = parse.parse_args()


def gen_tokens(input_file):
    '''

    :param input_file: Путь к файлу, содержащему исходный текст
    :type input_file: str
    :return: Генерирует слова из файла без неалфавитных символов
    :rtype: str

    '''
    if namespace.dir is None:
        for line in sys.stdin:
            for token in alphabet.findall(line):
                yield token
    else:
        with open(input_file, 'r') as data:
            for line in data.readlines():
                for token in alphabet.findall(line):
                    yield token
                yield '#'
            yield '#'


def gen_bigramms(tokens):
    '''

    :param tokens: Генератор слов
    :type tokens: generator
    :return: Возвращает пары вида (слово_1, слово_2)
    :rtype: tuple

    '''
    # "#" – cпециальный символ, используемый для первого
    #  и последнего слова в словаре
    token_0 = "#"
    for token_1 in tokens:
        yield token_0, token_1
        token_0 = token_1
    yield token_0, "#"


def train(text, model):
    '''

    :param text: Путь к файлу, содержащему исходный текст
    :param model:
    :type text: str
    :type model: defaultdict(dict)
    :return: Возвращает словарь, в котором первому слову из пары
             сопоставлено второе слово и частота его вхождения

    '''
    tokens = gen_tokens(text)
    bigramms = gen_bigramms(tokens)
    pairs = defaultdict(lambda: 0)
    for (token_0, token_1) in bigramms:
        if (token_0, token_1) == ('#', '#'):
            continue
        if namespace.lc:  # Опционально приводим к lowercase
            token_0, token_1 = token_0.lower(), token_1.lower()
        # Считаем частоту вхождения пары (token_0, token_1)
        pairs[token_0, token_1] += 1
    for ((token_0, token_1), frequency) in pairs.items():
        model[token_0][token_1] = frequency


def get_files(path):
    '''

    :param path: Путь к рассматриваемому файлу
    :param txt_files: список файлов, имеющих разрешение .txt
    :return: По указанному пути возвращает список файлов .txt,
             лежащих в указанной директории
    '''
    # Восстанавливаем абсолютный путь до директории
    abs_path = os.path.abspath(path)
    txt_files = []
    if os.path.isfile(abs_path):
        # Получаем разрешение файла
        root, extension = os.path.splitext(abs_path)
        if extension == '.txt':
            txt_files.append(abs_path)
    else:
        os.chdir(path)
        for file in os.listdir(abs_path):
            if file[0] != '.':  # Позволяет отсечь папки типа ".git" и др.
                # Рекурсивно рассматриваем вложенные файлы
                txt_files += get_files(os.path.normpath(abs_path + '/' + file))
    return txt_files


def write_train_result():
    '''

    :return: Записывает модель в файл, путь к которому передается в --model

    '''
    model = defaultdict(dict)
    with open(namespace.model, 'wb') as data:
        for text in get_files(namespace.dir):
            train(text, model)
        dump(model, data)


if __name__ == "__main__":
    write_train_result()
