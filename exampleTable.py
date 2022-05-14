import sys
import json
import pandas as pd
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

# Ideen zum Verbessern der Tabelle:
# - Überschrift: wenn auf auf einen Bahnhof gedrückt wird, werden die Werte angezeigt
# - Headerdata leserlicher gestalten
# - Fenstergröße festlegen
# - ...
# - Kommentieren
# - gerne noch erweitern :-) TB


class tableCreator(QtCore.QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.dataframe = pd.read_csv("stop_times.txt")      
        
    def rowCount(self, parent = None):
        return len(self.dataframe[0:])
        
    def columnCount(self, parent = None):
        return len(self.dataframe.keys())
        
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
            
        value = self.dataframe.iloc[index.row(), index.column()]
        return str(value)
            
    def headerData(self, index, orientation, role = QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Orientation.Horizontal:
           return None
        
        return self.dataframe.columns[index]
 
class dataTable(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        table_view = QtWidgets.QTableView()
        table_model = tableCreator()
        table_view.setModel(table_model)
        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(table_view)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)
        
if __name__ == "__main__":
    """ Da für eine GUI eine App notwendig ist, wird diese ersteinmal gebaut. """ 
    
    app = QtWidgets.QApplication(sys.argv)
    window = dataTable()
    window.show()
    sys.exit(app.exec())