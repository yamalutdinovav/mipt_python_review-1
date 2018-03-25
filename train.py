# -*- coding: utf-8 -*-

import re
import os
import sys
from collections import defaultdict
from pickle import dump
import argparse

# Шаблон, по которому производится поиск слов
alphabet = re.compile(u'[а-яА-яё-]+')

# Аргументы командной строки:
parse = argparse.ArgumentParser()
parse.add_argument('--input-dir',
                   help='Путь к директории, в которой лежат документы. Если не указана, текст вводится из stdin',
                   dest='dir')
parse.add_argument('--model', help='Обязательный аргумент. Путь к файлу, в который сохраняется модель', required=True)
parse.add_argument('--lc', help='Необязательный аргумент. Приводить тексты к lowercase', action='store_true')
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
        with open(input_file, 'r', encoding='utf-8') as data:
            for line in data.readlines():
                for token in alphabet.findall(line):
                    yield token



def gen_bigramms(tokens):
    '''

    :param tokens: Генератор слов
    :type tokens: generator
    :return: Возвращает пары вида (слово_1, слово_2)
    :rtype: tuple

    '''
    token_0 = "#" # Cпециальный символ, используемый для первого и последнего слова в словаре
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
    :return: Возвращает словарь, в котором первому слову из пары сопоставлено второе слово и частота его вхождения

    '''
    tokens = gen_tokens(text)
    bigramms = gen_bigramms(tokens)
    pairs = defaultdict(lambda: 0)
    for (token_0, token_1) in bigramms:
        if namespace.lc:  # Опционально приводим к lowercase
            token_0, token_1 = token_0.lower(), token_1.lower()
        pairs[token_0, token_1] += 1  # Считаем частоту вхождения пары (token_0, token_1)
    for ((token_0, token_1), frequency) in pairs.items():
        model[token_0][token_1] = frequency


def get_files(path, txt_files):
    '''

    :param path: Путь к рассматриваемому файлу
    :param txt_files: список файлов, имеющих разрешение .txt
    :return: По указанному пути возвращает список файлов .txt, лежащих в указанной директории
    '''
    if os.path.isfile(path):
        root, extension = os.path.splitext(path) # Получаем разрешение файла
        if extension == '.txt':
            txt_files.append(path)
    else:
        os.chdir(path)
        files = os.listdir(path)
        for file in os.listdir(path):
            if file[0] != '.': # Позволяет отсечь папки типа ".git" и др.
                get_files(os.path.normpath(path + '/' + file), txt_files) # Рекурсивно рассматриваем вложенные файлы


def write_train_result():
    '''

    :return: Записывает модель в файл, путь к которому передается в --model

    '''
    model = defaultdict(dict)
    with open(namespace.model, 'wb') as data:
        txt_files = []
        get_files(namespace.dir, txt_files)
        for text in txt_files:
            train(text, model)
        dump(model, data)


if __name__ == "__main__":
    write_train_result()
