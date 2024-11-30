def printExpectation():
    printAct = int(input('Желаете распечатать документ:\n'
                           '1 - Да\n'
                           '2 - Нет\n'))
    if printAct == 1:
        chooseLanguage()


def chooseLanguage():
    chooseAct = int(input('Какой документ хотите распечатать?:\n'
                           '1 - На русском\n'
                           '2 - На английском\n'
                           '3 - Назад\n'))
    if chooseAct == 1:
        printRusDocument()
    elif chooseAct == 2:
        printEngDocument()
    elif chooseAct == 3:
        print('')
        printExpectation()


def printEngDocument():
    print('В разработке')

def printRusDocument():
    print('В разработке')