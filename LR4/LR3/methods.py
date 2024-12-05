import re
import pymorphy3

import string
import operator

from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from printDocumets import printExpectation
from readFromFile import readFromFile
from saveInFile import SaveFile

from ollama import chat
from ollama import ChatResponse


import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import spacy
import pymorphy3

# Загрузка моделей для обработки языков
nltk.download('punkt')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# Загружаем модель для немецкого языка
nlp_de = spacy.load("de_core_news_md")
nlp_en = spacy.load("en_core_web_sm")




def translate(text):
    from pymorphy2 import MorphAnalyzer
    morph = MorphAnalyzer()
    return morph.parse(text)[0].normal_form


def analize(en, german):
    german_text = german
    english_text = en
        ## Морфологический разбор для немецкого
    print("Немецкий текст (морфологический разбор):")
    doc_de = nlp_de(german_text)
    for token in doc_de:
        print(f"{token.text} -> Лемма: {token.lemma_}, Часть речи: {token.pos_}, Морфология: {token.morph}")

    # Морфологический разбор для английского
    print("\nАнглийский текст (морфологический разбор):")
    tokens_en = nltk.word_tokenize(english_text)
    for token in tokens_en:
        lemma = lemmatizer.lemmatize(token)
        synsets = wn.synsets(lemma)
        print(f"{token} -> Лемма: {lemma}, Синонимы: {[s.name() for s in synsets]}")

    # Синтаксический разбор для немецкого
    print("\nСинтаксическое дерево (немецкий):")
    for token in doc_de:
        print(f"{token.text} -> Зависимость: {token.dep_}, Главный токен: {token.head.text}")

    # Синтаксический разбор для английского
    print("\nСинтаксическое дерево (английский):")
    doc_en = nlp_en(english_text)
    for token in doc_en:
        print(f"{token.text} -> Зависимость: {token.dep_}, Главный токен: {token.head.text}")
def translate():
    
    print("Введите текст для перевода:")
    text = input()
    
    result = ""

    response = chat(model='ardonplay/english-to-german-translate', messages=[
    {
        'role': 'user',
        'content': text,
    }
    ],
    stream=True)
    for chunk in response:
        chank = chunk['message']['content'];
        result += chank
        print(chank, end='', flush=True)
    print('\n')
    
    analize(text, result)
    SaveFile(result, 1)
    printExpectation()

