from methods import translate
import sys


def chooseMethod():
    chooseAct = int(input('Выберите :\n'
                    '1 - Перевести текст\n'
                    '2 - Выход\n'))
    if chooseAct == 1:
        translate()
    elif chooseAct == 2:
        print('До новых встреч!')
        sys.exit()


def expectation():
    while True:
        act = int(input('Желаете продолжить?\n'
                        '1 - Да\n'
                        '2 - Нет\n'))
        if act == 1:
            chooseMethod()
        elif act == 2:
            print('До новых встреч!')
            break