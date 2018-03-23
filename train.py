# -*- coding: utf-8 -*-

import re
import os
import sys
from collections import defaultdict
from pickle import dump
import argparse

alphabet = re.compile(u'[а-яА-яё-]+')
parse = argparse.ArgumentParser()
parse.add_argument('--input-dir', help='Путь к директории, в которой лежит коллекция документов', dest='dir')
parse.add_argument('--model', help='Путь к файлу, в который сохраняется модель', required=True)
parse.add_argument('--lc', help='Приводить тексты к lowercase', action='store_true')
namespace = parse.parse_args()

def gen_tokens(input_file):
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
    token_0 = "#"
    for token_1 in tokens:
        yield token_0, token_1
        token_0 = token_1
    yield token_0, "#"


def train(text):
    tokens = gen_tokens(text)
    bigramms = gen_bigramms(tokens)
    pairs = defaultdict(lambda: 0)
    for (token_0, token_1) in bigramms:
        if namespace.lc is not None:
            token_0, token_1 = token_0.lower(), token_1.lower()
        pairs[token_0, token_1] += 1
    model = defaultdict(dict)
    for ((token_0, token_1), frequency) in pairs.items():
        model[token_0][token_1] = frequency
    return model


def write_train_result():
    with open(namespace.model, 'wb') as data:
        os.chdir(namespace.dir)
        files = os.listdir(namespace.dir)
        for filename in files:
            root, extension = os.path.splitext(filename)
            if extension == '.txt':
                model = train(filename)
                dump(model, data)


if __name__ == "__main__":
    write_train_result()