# -*- coding: utf-8 -*-

from pickle import load
from collections import defaultdict
import random
import argparse

# Аргументы командной строки:
parse = argparse.ArgumentParser()
parse.add_argument('--model',
                   help='Обязательный аргумент. '
                   'Путь к файлу, из которого загружается модель.',
                   required=True)
parse.add_argument('--seed', help='Начальное слово. '
                   'Если не указано, выбираем слово случайно',
                   action='store', dest='seed')
parse.add_argument('--length', help='Обязательный аргумент. '
                   'Длина генерируемой последовательности',
                   required=True, action='store', dest='length')
parse.add_argument('--output',
                   help='Файл, в который будет записан результат. '
                   'Если не указан, текст выводится в stdout')
namespace = parse.parse_args()


def load_model():
    '''

    :return: Возвращает словарь, записанный по указанному пути
    :rtype: defaultdict

    '''
    with open(namespace.model, 'rb') as data:
        return load(data)


def weighted_choice(elements):
    '''
    :param elements: Словарь, из которого совершается выбор
    :type elements: dict
    :return: Возвращает слово, случайно выбранное из словаря
             с учетом частоты вхождения
    :rtype: str

    '''
    # Cуммарная частота вхождения слов
    total = sum(weight for token, weight in elements.items())
    rand = random.uniform(0, total)
    tmp = 0
    for token, weight in elements.items():
        if tmp + weight > rand:
            return token
        tmp += weight
    assert False  # Если не вывели ничего, то ошибка


def build_phrase(model, number):
    '''

    :param model: Словарь, состоящий из слов и частот их вхождения
    :param number: Длина (количество слов) в выводимой фразе
    :type model: dict
    :type number: int
    :return: Фраза, построенная по указанной модели
    :rtype: str

    '''
    phrase = ''
    if namespace.seed is None:
        token_0 = random.choice(list(model.keys()))
    elif namespace.seed not in model:
        raise ValueError("Указанного слова нет в модели")
    else:
        token_0 = namespace.seed
    token_1 = weighted_choice(model[token_0])
    while len(phrase.split()) < number:
        if not token_0.isalpha():  # Необходимо, чтобы отсечь символ '#'
            token_0, token_1 = token_1, weighted_choice(model[token_1])
            continue
        if phrase == '':
            phrase += token_0
        else:
            phrase += ' ' + token_0
        token_0, token_1 = token_1, weighted_choice(model[token_1])
    return phrase


def write_phrase(phrase):
    '''

    :param phrase: Фраза, которую нужно записать
    :return: Записывает фразу в указанный файл
             (или выводит в sys.stdin, если не указан аргумент --output)

    '''
    if namespace.output is None:
        print(phrase)  # Консольный вывод текста
    else:
        with open(namespace.output, 'w') as data:
            data.write(phrase)  # Запись в указанный файл


if __name__ == "__main__":
    write_phrase(build_phrase(load_model(), int(namespace.length)))
