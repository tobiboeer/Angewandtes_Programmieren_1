"""
Creates table and table widget for the overview.

Date: 13. May 2022

Authors:
    Fabian Kessener
    Tobias Boeer
    Timon Fass

Emails:
    fabian.kessener@student.jade-hs.de
    tobias.boeer@student.jade-hs.de
    timon.fass@student.jade-hs.de

Version: 1.0

Licence: 
    
    Copyright: (c) 2022, Kessener, Boeer, Fass
    This code is published under the terms of the 3-Clause BSD License.
    The full text can be seen in ABOUT.md or the 'About/Licence' dropdown
    menu.
"""

from PySide6 import QtCore
from PySide6 import QtWidgets

class tableCreator(QtCore.QAbstractTableModel):
    """
    Creates a table with the main functions: rowCount, 
    columnCount, data and headerData.
    These functions are setting the size of the matrix 
    and a clear arrangement.
    """
    
    def __init__(self, df):
        """
        Sets the dataframe for the table view.

        Parameters
        ----------
        df : dataframe
            train station information
        """
        super().__init__()
        self.train_station_info = df
        
        
    def rowCount(self, parent = None): 
        """
        Sets the amount of the rows of the read file.
        """
        self.number = len(self.train_station_info[0:])
        return self.number
        
    def columnCount(self, parent = None): 
        """
        Sets the amount of the columns of the read file.
        """
        return len(self.train_station_info.keys())
        
    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        Shows the file components.

        Parameters
        ----------
        index : QModelIndex
        role : int

        According to: Tutorial of Bastian Bechthold
        """
        if role != QtCore.Qt.DisplayRole:
            return None
            
        value = self.train_station_info.iloc[index.row(), index.column()]
        return str(value)
            
    def headerData(self, index, orientation, role = \
        QtCore.Qt.DisplayRole):
        """
        Shows the head of the columns seperately.

        Parameters
        ----------
        index : int
        orientation : Any
            horizontal or vertical
        role : ItemDataRole

        According to: Tutorial of Bastian Bechthold
        """
        if role != QtCore.Qt.DisplayRole or orientation != \
            QtCore.Qt.Orientation.Horizontal:
           return None
        
        return self.train_station_info.columns[index] 
 
class dataTable(QtWidgets.QMainWindow):
    """
    Contains data table for train station information.
    """

    def __init__(self, main_gui):
        """
        Takes the file components of the 'tableCreator', 
        creates a widget and merges
        them together.

        Parameters
        ----------
        main_gui : mainWindow
            contains the main frame of the GUI
        """
        super().__init__()
        self.main_gui = main_gui

        self.setMinimumSize(140, 250)
        
        self.table_view = QtWidgets.QTableView()
                
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table_view)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

    def set_dataframe(self, train_station_info):
        """
        Sets the dataframe.

        Parameters
        ----------
        train_station_info : dataframe
            contains the train station information
        """
        table_model = tableCreator(train_station_info)
        self.table_view.setModel(table_model)