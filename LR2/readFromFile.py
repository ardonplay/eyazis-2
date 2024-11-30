from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
import os


def LoadFile():
    dirName = os.path.abspath("texts/")
    files = os.listdir("texts/")
    string = ''.join(files)
    file = (dirName + '/' + string)
    #print(file)
    return file


def readFromFile():
    try:
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        fp = open(LoadFile(), 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp,
                                      check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()
        fp.close()
        device.close()
        retstr.close()
        # print(text)
        return text
    except IOError:
        print("Отстутствует файл!")
