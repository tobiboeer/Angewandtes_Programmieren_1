import csv
from this import s
import numpy as np
import pandas as pd
import os
from os.path import exists
import random
from datetime import datetime
import time
import calendar


import threading
import time




my_list = [1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,10,1231,234,252,239][0:6]
my_list_2 = [6,17,18,19,10,1231,234,252,239][0:6]



d = {'Month':my_list,'Day':my_list_2}
df = pd.DataFrame (d)


print(df)






