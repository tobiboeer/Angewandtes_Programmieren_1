
import pandas as pd
import sys
import geojson
import os
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
import json



pfad = os.path.dirname(__file__) + '/conectons.csv'
df = pd.read_csv(pfad, encoding= 'utf8')



print(df)