import csv
import numpy as np
import codecs

def getData(filename):
    with open(filename, "rb") as csv_file:
        csv_obj = csv.reader(codecs.iterdecode(csv_file, 'utf-8'))
        for row in csv_obj:
            yield row

my_gen = getData('Python_2015_1.csv')
next(my_gen)
