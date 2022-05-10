



from PyQt5.QtCore import QDate, QDateTime

#usando Date
datetime = QDate.currentDate().toPyDate()
print(datetime)
#datetime = datetime.date(2017, 3, 17)
print(datetime)
#usando DateTime
da = QDateTime.currentDateTime().time()

print(da)



#PySide6.QtCore.QTime(3, 0, 0, 0)