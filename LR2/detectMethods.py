import pymorphy3
from langdetect import detect
from transformers import pipeline
from ollama import chat
from ollama import ChatResponse
from printDocuments import printExpectation
import torch
from readFromFile import readFromFile
import re
from saveInFile import SaveFile
from collections import defaultdict



def frequencyWordMethod():
    fileRus = open('Training/frequencyMethodRussian.txt')
    contentRus = fileRus.read()
    fileEng = open('Training/frequencyMethodEnglish.txt')
    contentEng = fileEng.read()
    file = readFromFile()
    numberOfRussianMatches = 0
    for word in contentRus:
        i = 0
        if word in file:
            i = i + 1
            numberOfRussianMatches = numberOfRussianMatches + i
    numberOfEnglishMatches = 0
    for word in contentEng:
        i = 0
        if word in file:
            i = i + 1
            numberOfEnglishMatches = numberOfEnglishMatches + i
    if numberOfEnglishMatches > numberOfRussianMatches:
        result = 'Результат идентификации текста: en'
        print(result)
    elif numberOfEnglishMatches < numberOfRussianMatches:
        result = 'Результат идентификации текста: ru'
        print(result)
    else:
        result = 'Не удалось распознать язык'
        print(result)
    SaveFile(result, 3)
    printExpectation()


def load_words(filename):
    inFile = open(filename, 'r')
    words = inFile.readlines()
    counter = 0
    for word in words:
        words[counter] = re.sub('\n', '', word)
        counter = counter + 1
    return words


def shortWordMethod():
    # загрузка ПОЯ из файлов
    contentRus = load_words('Training/shortMethodRussian.txt')
    contentEng = load_words('Training/shortMethodEnglish.txt')
    # загрузка текста из анализируемого файла
    analyzing_file = readFromFile()
    # создание словарей
    engEntrances = {}
    ruEntrances = {}
    analyzer = pymorphy3.MorphAnalyzer()

    # инициализация словарей лексема -> кол-во вхождений
    for word in contentRus:
        ruEntrances[word] = 0
    for word in contentEng:
        engEntrances[word] = 0

    # подсчёт количества вхождений лексемы в тексте (учитываются все формы лексемы)
    # в подсчёте могут быть погрешности из-за того, что некоторые формы лексемы, найденные в pymorphy могут входить
    # список word_morph[0].lexeme дважды
    for word in contentRus:
        word_morph = analyzer.parse(word)
        lexemes = word_morph[0].lexeme
        for lexeme in lexemes:
            lexeme_word = lexeme.word
            matches = re.findall(lexeme_word, analyzing_file)
            ruEntrances[word] = ruEntrances[word] + len(matches)

    # аналогичный процесс для английских лексем
    for word in contentEng:
        word_morph = analyzer.parse(word)
        lexemes = word_morph[0].lexeme
        for lexeme in lexemes:
            lexeme_word = lexeme.word
            matches = re.findall(lexeme_word, analyzing_file)
            engEntrances[word] = engEntrances[word] + len(matches)
    # сумма всех вхождений русских лексем в тексте
    entrances_sum_ru = 0

    # сумма всех вхождений английских лексем в тексте
    entrances_sum_en = 0

    # подсчёт всех вхождений
    for lexeme, entrances in ruEntrances.items():
        entrances_sum_ru = entrances_sum_ru + entrances

    for lexeme, entrances in engEntrances.items():
        entrances_sum_en = entrances_sum_en + entrances

    # вычисление вероятностей появления для каждой лексемы
    if entrances_sum_ru != 0:
        for lexeme, entrances in ruEntrances.items():
            ruEntrances[lexeme] = entrances / entrances_sum_ru

    if entrances_sum_en != 0:
        for lexeme, entrances in engEntrances.items():
            engEntrances[lexeme] = entrances / entrances_sum_en

    ru_probability = 1.0
    eng_probability = 1.0

    # вычисление вероятности
    for entrances_amount in ruEntrances.values():
        if entrances_amount == 0:
            entrances_amount = 1
        ru_probability = ru_probability * entrances_amount
    for entrances_amount in engEntrances.values():
        if entrances_amount == 0:
            entrances_amount = 1
        eng_probability = eng_probability * entrances_amount

    print('Вероятность Русского языка: ' + str(ru_probability / 100))
    print('Вероятность Английского языка: ' + str(eng_probability / 100))
    # знаки инвертированы, т.к. в ходе вычисления вероятности языка происходит умножение дроби на дробь и результат
    # стремится к 0
    if eng_probability < ru_probability:
        result = 'Результат идентификации текста: en'
        print(result)
    elif eng_probability > ru_probability:
        result = 'Результат идентификации текста: ru'
        print(result)
    else:
        print('Не удалось распознать язык')
    SaveFile(result, 2)
    printExpectation()

def chunk_text(text, chunk_size=512):
    words = text.split()  # Разбиваем текст на слова
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])
        
def average_scores(results):
    scores = defaultdict(list)
    # Собираем результаты
    for result in results:
        for item in result:
            scores[item['label']].append(item['score'])
    
    # Считаем среднее для каждого языка
    avg_scores = {label: sum(scores[label]) / len(scores[label]) for label in scores}
    # Находим язык с наибольшей средней вероятностью
    most_probable_language = max(avg_scores, key=avg_scores.get)
    return most_probable_language, avg_scores[most_probable_language]

def ownMethod():

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    # Загружаем модель и указываем устройство
    from transformers import pipeline

    # Настройка pipeline
    language_identifier = pipeline(
        "text-classification",
        model="papluca/xlm-roberta-base-language-detection",
        truncation=True,
        device=0  # Убедитесь, что MPS доступен
    )

    # Разбиваем текст на части

    # Текст для анализа
    text = str(readFromFile())

    # Анализируем части текста
    results = []
    for chunk in chunk_text(text, chunk_size=512):
        result = language_identifier(chunk)
        results.append(result)

    # Объединяем результаты
    language, avg_score = average_scores(results)
    print(f"Определённый язык: {language}, Средняя вероятность: {avg_score:.4f}")

    # result = 'Результат идентификации текста: ', detect(str(readFromFile()))
    # print(result)3
    
    # SaveFile(result, 1)
    printExpectation()
