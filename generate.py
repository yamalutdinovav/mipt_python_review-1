# -*- coding: utf-8 -*-

from pickle import load
import random
import argparse

parse = argparse.ArgumentParser()
parse.add_argument('--model', help='Путь к файлу, из которого загружается модель', required=True)
parse.add_argument('--seed', help='Начальное слово. Если не указано, выбираем слово случайно', action='store', dest='seed')
parse.add_argument('--length', help='Длина генерируемой последовательности', required=True, action='store', dest='length')
parse.add_argument('--output', help='Файл, в который будет записан результат')
namespace = parse.parse_args()


def load_model():
    with open(namespace.model, 'rb') as data:
        return load(data)


def weighted_choice(elements):
    total = sum(weight for token, weight in elements.items())
    rand = random.uniform (0, total)
    tmp = 0
    for token, weight in elements.items():
        if tmp + weight > rand:
            return token
        tmp += weight
    assert False


def build_phrase (model, number):
    phrase = ''
    if namespace.seed is None:
        token_0 = random.choice(list(model.keys()))
    else:
        token_0 = namespace.seed
    token_1 = weighted_choice(model[token_0])
    phrase += token_0.capitalize()
    while len(phrase.split()) < number:
        token_0, token_1 = token_1, weighted_choice(model[token_1])
        if not token_0.isalpha():
            continue
        phrase += ' ' + token_0
    return phrase


def write_phrase(phrase):
    if namespace.output is None:
        print(phrase)
    else:
        with open(namespace.output, 'w', encoding='utf-8') as data:
            data.write(phrase)


if __name__ == "__main__":
    write_phrase(build_phrase(load_model(), int(namespace.length)))
