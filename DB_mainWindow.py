"""
Main window of the program.

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
from PySide6 import QtGui

from DB_mapWidget import mapWidget as mapWidget
from DB_sideWindow import sideWindow as sideWindow
from DB_dataTable import dataTable as dataTable
from DB_dataTable import tableCreator as tableCreator
from DB_menuWindow import menuWindowAbout as menuWindowAbout
from DB_menuWindow import menuWindowReadMe as menuWindowReadMe
from DB_menuWindow import menuWindowTutorial as menuWindowTutorial

class mainWindow(QtWidgets.QMainWindow):
    """
    Creates the main window of the GUI.
    """
    
    def __init__(self, model):
        """
        Creates the main frame of the GUI with grid layout 
        and adds all subframes.

        Parameters
        ----------
        model : model
            interactions class
        """
        super().__init__()

        self.model = model

        self.about_window = menuWindowAbout(model)
        self.about_window.setWindowTitle("About - Über dieses Programm")
        self.readme_window = menuWindowReadMe(model)
        self.readme_window.setWindowTitle("Read Me - Wichtig zu wissen")
        self.tutorial_window = menuWindowTutorial(model)
        self.tutorial_window.setWindowTitle("Tutorial")

        #--------------- STATUSBAR ----------------------------------
        self.status_bar = self.statusBar()

        #--------------- MENUBAR ------------------------------------
        # According to:
        # https://realpython.com/python-menus-toolbars/#populating-menus-with-actions
        # https://pythonprogramming.net/menubar-pyqt-tutorial/

        menuBar = self.menuBar()
        help_menu = QtWidgets.QMenu("Help", self)
        menuBar.addMenu(help_menu)
    
        aboutAction = QtGui.QAction("About/Licence", self)
        readmeAction = QtGui.QAction("ReadMe", self)
        tutorialAction = QtGui.QAction("Tutorial", self)

        help_menu.addAction(aboutAction)
        help_menu.addAction(readmeAction)
        help_menu.addAction(tutorialAction)

        aboutAction.triggered.connect(self.open_about)
        readmeAction.triggered.connect(self.open_readme)
        tutorialAction.triggered.connect(self.open_tutorial)
       
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.germany_map = mapWidget(self)
        
        self.side_window_instance = sideWindow(self)
        self.grid_layout.addWidget(self.side_window_instance,0,1)

        self.model.set_main_gui(self)

        self.dataTable_instance = dataTable(self)
        self.grid_layout.addWidget(self.dataTable_instance,1,0,1,2)

        self.model.change_current_stops("stops_fern")
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(self.grid_layout)
        self.setCentralWidget(window_content)

    def draw_route_network(self, train_stations, filename_routes):
        """
        Draws the route network.
        
        Parameters
        ----------
        train_stations : dataframe
            contains station information
        filename_routes : dataframe
            contains route information
        """
        self.germany_map.draw_route_network \
            (train_stations, filename_routes)
        
    def open_about(self):
        """
        Shows the window of the 'About' menu.
        """
        self.about_window.show()
    
    def open_readme(self):
        """
        Shows the window of the 'ReadMe' menu. 
        """
        self.readme_window.show()

    def open_tutorial(self):
        """
        Shows the window of the 'Tutorial' menu. 
        """
        self.tutorial_window.show()

    @QtCore.Slot(str)
    def click_function(self, whole_station_information):
        """
        Reacts to clicking of the mouse.

        Parameters
        ----------
        whole_station_information : dataframe
            contains the whole information of the stations
        """
        if whole_station_information in self.model.get_current_stops() \
            ["stop_name"].to_numpy():
            self.side_window_instance.set_train_station \
                (whole_station_information)

    def train_station_show(self):
        """
        Enables the train stations as options in the combobox.
        """
        table_view = QtWidgets.QTableView()
        table_model = tableCreator()
        table_view.setModel(table_model)
        
        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.addWidget(table_view)
        
        self.layout.addLayout(sub_layout)
  