"""
Creates the widget for the interactive side window.

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

from PySide6 import QtWidgets
from datetime import datetime

class sideWindow(QtWidgets.QMainWindow):
    """
    Creating an interactive widget next to the german map.
    """

    def __init__(self, main_gui):
        """
        Instantiate the main aspects of an interactive planner. 
        It contains the comboboxes, textfields, 
        labels, layouts and buttons.

        Parameters
        ----------
        main_gui : mainWindow
            main window of the GUI     
        """
        
        super().__init__()
        self.main_gui = main_gui
        self.setMinimumSize(250, 450)
        
        # -------------- COMBOBOXES ----------------
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Bahnhof wählen -")
        self.combobox_start.currentTextChanged.connect \
            (self.change_start_station)
        
        # -------------- TEXT FIELDS ----------------
        self.textfield_date = QtWidgets.QDateEdit()
        start_date = datetime(2022, 0o1, 0o1)
        end_date = datetime(2022, 12, 31)
        self.textfield_date.setDateRange(start_date, end_date)
        
        self.textfield_time = QtWidgets.QTimeEdit()
        self.textfield_time_dif = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
        self.text = ""
        self.update_text(" ")
        self.start_station = " "
        
        # -------------- LABELS  ------------------
        label_button_traffic_style = QtWidgets.QLabel("Bahnart:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_textfield_date_time = QtWidgets.QLabel \
            ("Datum und Zeit der Abfahrt:")
        self.label_textfield_time_dif = QtWidgets.QLabel("Zeitfenster")
        label_textfield_allInfo = QtWidgets.QLabel \
            ("Besondere Informationen:")
        label_button_request = QtWidgets.QLabel \
            ("Daten zum Bahnhof erstellen:")

        # -------------- BUTTONS ------------------
        self.button_nahverkehr = QtWidgets.QPushButton("Nahverkehr")
        self.button_fernverkehr = QtWidgets.QPushButton("Fernverkehr")
        self.button_regional = QtWidgets.QPushButton("Regional")
        self.button_request = QtWidgets.QPushButton("Anfrage stellen")
        self.button_request.setFixedSize(100, 40)

        self.button_fernverkehr.clicked.connect \
            (self.click_function_long_distance)
        self.button_nahverkehr.clicked.connect \
            (self.click_function_short_distance)
        self.button_regional.clicked.connect \
            (self.click_function_regional)
        self.button_request.clicked.connect(self.train_station_request)

        # -------------- LAYOUTS ------------------------------------
        button_layout_traffic = QtWidgets.QHBoxLayout()
        button_layout_traffic.addWidget(self.button_nahverkehr)
        button_layout_traffic.addWidget(self.button_fernverkehr)
        button_layout_traffic.addWidget(self.button_regional)
        
        date_time_layout = QtWidgets.QHBoxLayout()
        date_time_layout.addWidget(self.textfield_date)
        date_time_layout.addWidget(self.textfield_time)

        time_dif_layout = QtWidgets.QHBoxLayout()
        time_dif_layout.addWidget(self.textfield_time_dif)

        button_request_layout = QtWidgets.QHBoxLayout()
        button_request_layout.addWidget(self.button_request)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_button_traffic_style)
        layout.addLayout(button_layout_traffic)
        layout.addWidget(label_combobox_start) 
        layout.addWidget(self.combobox_start)
        layout.addWidget(label_textfield_date_time)
        layout.addLayout(date_time_layout)
        layout.addWidget(self.label_textfield_time_dif)
        layout.addLayout(time_dif_layout)
        layout.addWidget(label_button_request)
        layout.addLayout(button_request_layout)
        layout.addWidget(label_textfield_allInfo)
        layout.addWidget(self.textfield_allInfo)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)
        self.set_train_stations_list()

    def set_train_station(self, new_station):
        """
        Changes the station in the sidebar and 
        requests new station information

        Parameters
        ----------
        new_station : String
            name of the selected train station
        """
        self.combobox_start.setCurrentText(new_station)
        self.start_station = new_station
        self.train_station_request()
 
    def update_text(self, new_info):
        """
        Puts the new information into the text and if necessary, 
        deletes the old ones.

        Parameters
        ----------
        new_info : String
            new info for the text
        """
        self.text = self.text + new_info + "\n"
        splitted = self.text.splitlines( )
        lin_sub = len(splitted) - 10
        if len(splitted) > 10:
            self.text = ""
            for i in range(10):
                self.text = self.text + splitted[i+lin_sub] + "\n"
        self.textfield_allInfo.setText(self.text)
        
    def change_start_station(self, value):
        """
        Noted the selected start trainstation and updates the text box.  

        Parameters
        ----------
        value : String
            name of the selected train station  
        """
        self.start_station = value
  
    def click_function_long_distance(self):
        """
        Loads long distance data, if button 'Fernverkehr' is clicked.
        """
        self.main_gui.model.change_current_stops("stops_fern")
        self.set_train_stations_list()

    def click_function_short_distance(self):
        """
        Loads short distance data, if button 'Nahverkehr' is clicked.
        """
        self.main_gui.model.change_current_stops("stops_nah")
        self.set_train_stations_list()

    def click_function_regional(self):
        """
        Loads regional data, if button 'Regionalverkehr' is clicked.
        """
        self.main_gui.model.change_current_stops("stops_regional")
        self.set_train_stations_list()

    def set_train_stations_list(self): 
        """
        Train station list is added to the combobox.
        """ 
        stations = self.main_gui.model.get_current_stops()
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)

    def train_station_request(self):
        """
        Requestes train station information based on the train station,
        the date and the time.
        """
        time_span = int(self.textfield_time_dif.time().toString()[0:2])
        day_str = self.textfield_date.dateTime().toString()
        time_str = self.textfield_time.time().toString()
        days_dic =	{
            "Mon": 0,
            "Tue": 1,
            "Wed": 2,
            "Thu": 3,
            "Fri": 4,
            "Sat": 5,
            "Sun": 6
        }
        day = days_dic[day_str[0:3]]
        hour = int(time_str[0:2])
        minute = int(time_str[3:5])

        self.main_gui.model.change_train_station_info(time_span, day, \
            hour, minute, self.start_station)
