# -*- coding: utf-8 -*-
# Запись последовательности слов на основе сгенерированного словаря
# Автор: Артем Ямалутдинов, 1 курс ФИВТ МФТИ
# Ревью №1
# 21 апреля 2018 года

from pickle import load
import random
import argparse

# Специальный служебный символ для начала и конца строки
ENDSYMBOL = '#'

# Аргументы командной строки:
parse = argparse.ArgumentParser(
    description='Запись сгенерированного на основе словаря биграмм текста')
parse.add_argument('--model',
                   help='Обязательный аргумент. '
                   'Путь к файлу, из которого загружается модель.',
                   required=True)
parse.add_argument('--seed', help='Необязательный аргумент.'
                                  ' Начальное слово текста. '
                   'Если не указано, выбираем слово случайно',
                   action='store', dest='seed')
parse.add_argument('--length', help='Обязательный аргумент. '
                   'Длина генерируемой последовательности слов',
                   required=True, action='store', dest='length')
parse.add_argument('--output',
                   help='Файл, в который будет записан результат. '
                   'Если не указан, текст выводится в stdout')
namespace = parse.parse_args()


def load_model(model):
    """
    Загрузка модели из файла
    :param model: Путь к файлу, в который сохраняется модель
    :type model: str
    :return: Модель, построенная по набору текстов
    :rtype: dict
    """
    with open(model, 'rb') as data:
        return load(data)


def weighted_choice(elements):
    """
    Выбор слова из словаря с учетом частоты вхождения
    :param elements: Словарь, из которого совершается выбор
    :type elements: dict
    :return: Слово, случайно выбранное из словаря
    :rtype: str
    """
    # Суммарная частота вхождения слов
    if len(elements) == 0:
        raise KeyError("Модель пуста")
    total = sum(weight for token, weight in elements.items())
    rand = random.uniform(0, total)
    tmp = 0
    for token, weight in elements.items():
        if tmp + weight > rand:
            return token
        tmp += weight


def build_phrase(model, number, seed):
    """
    Строит последовательность слов по переданной модели
    :param model: Словарь, состоящий из слов и частот их вхождения
    :param number: Длина (количество слов) в выводимой фразе
    :type model: dict
    :type number: int
    :param seed: Начальное слово(если указано, иначе выбирается случайно)
    :type seed: str
    :return: Фраза, построенная по указанной модели
    :rtype: str
    """
    phrase = []
    # Выбираем первое слово из модели
    if seed is None:
        token_0 = random.choice(list(model.keys()))
    elif seed not in model or seed == ENDSYMBOL:
        raise KeyError("Указанного слова нет в модели")
    else:
        token_0 = seed
    # Выбираем второе слово с учетом частоты вхождения
    token_1 = weighted_choice(model[token_0])
    # Записываем выбранные слова в список
    while len(phrase) < number:
        if token_0 == ENDSYMBOL:  # Необходимо, чтобы отсечь символ '#'
            token_0, token_1 = token_1, weighted_choice(model[token_1])
        phrase.append(token_0)
        token_0, token_1 = token_1, weighted_choice(model[token_1])
    return ' '.join(phrase)


def write_phrase(phrase, output):
    """
    Запись построенной последовательности в указанный файл
    (если не указан, то консольный вывод)
    :param phrase: Последовательность слов
    :type phrase: str
    :param output: Путь к файлу, в который производится запись
    :type output: str
    """
    if output is None:
        print(phrase)  # Консольный вывод текста
    else:
        with open(output, 'w') as data:
            data.write(phrase)  # Запись в указанный файл


if __name__ == "__main__":
    model = load_model(namespace.model)
    phrase = build_phrase(model, int(namespace.length), namespace.seed)
    write_phrase(phrase, namespace.output)
