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
from PySide6 import QtCore
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
        
        
        #------------------ new -----------------------
        structurizer = QtWidgets.QTabWidget()
        
        self.information_page = QtWidgets.QWidget()
        self.set_information_page()
        
        self.set_planning_page()
        
        self.function_page = QtWidgets.QWidget()
        self.set_extension_page()
        
        
        structurizer.addTab(self.information_page, "Auskunft")
        structurizer.addTab(self.planning_page, "Routenplaner")
        structurizer.addTab(self.function_page, "Information")
       
        self.setCentralWidget(structurizer)
        #--------------------------------------------
        
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
        if self.text.replace(" ", "") == "":
            self.text = new_info
        else:
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
            
#--------------------------------new ---------------------------
    def set_information_page(self):
        """
        Sets the conditions of the information page in the tab structurizer.
        """
        
        # -------------- COMBOBOX  ------------------
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Bahnhof wählen -")
        
        # -------------- TEXTFIELD  ------------------
        self.textfield_date = QtWidgets.QDateEdit()
        start_date = datetime(2022, 0o1, 0o1)
        end_date = datetime(2022, 12, 31)
        self.textfield_date.setDateRange(start_date, end_date)
        
        self.textfield_time = QtWidgets.QTimeEdit()
        self.textfield_time_dif = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
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

        # -------------- LAYOUTS ------------------
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

        sublayout = QtWidgets.QVBoxLayout()
        self.information_page.setLayout(sublayout)
        sublayout.addWidget(label_button_traffic_style)
        sublayout.addLayout(button_layout_traffic)
        sublayout.addWidget(label_combobox_start) 
        sublayout.addWidget(self.combobox_start)
        sublayout.addWidget(label_textfield_date_time)
        sublayout.addLayout(date_time_layout)
        sublayout.addWidget(self.label_textfield_time_dif)
        sublayout.addLayout(time_dif_layout)
        sublayout.addWidget(label_button_request)
        sublayout.addLayout(button_request_layout)
        sublayout.addWidget(label_textfield_allInfo)
        sublayout.addWidget(self.textfield_allInfo)
        
        #--------------------- FUNCTIONS -----------
        self.combobox_start.currentTextChanged.connect \
            (self.change_start_station)
            
        self.text = ""
        self.update_text(" ")
        self.start_station = " "
        
        self.button_fernverkehr.clicked.connect \
            (self.click_function_long_distance)
        self.button_nahverkehr.clicked.connect \
            (self.click_function_short_distance)
        self.button_regional.clicked.connect \
            (self.click_function_regional)
        self.button_request.clicked.connect \
            (self.train_station_request)
    
    def set_planning_page(self):
        """
        sets the Options of the planning page in the tab structurizer.
        """
        self.planning_page = QtWidgets.QWidget()
        
        #--------------- CHECKBOX -----------------
        checkbox_nah = QtWidgets.QCheckBox('Nahverkehr')
        checkbox_fern = QtWidgets.QCheckBox('Fernverkehr')
        checkbox_regional = QtWidgets.QCheckBox \
            ('Regionalverkehr')
        
        # -------------- COMBOBOX  ------------------
        self.combobox_begin = QtWidgets.QComboBox()
        self.combobox_begin.setPlaceholderText \
            ("---This is where the fun begins---")
        self.combobox_end = QtWidgets.QComboBox()
        self.combobox_end.setPlaceholderText \
            ("---The boy who lived...---")
        combobox_route = QtWidgets.QComboBox()
        combobox_route.setPlaceholderText \
            ("--- Fast and the Furious ---")
        
        # -------------- TEXTFIELD  ------------------
        date_field = QtWidgets.QDateEdit()
        start_date = datetime(2022, 0o1, 0o1)
        end_date = datetime(2022, 12, 31)
        date_field.setDateRange(start_date, end_date)
        time_field = QtWidgets.QTimeEdit()
        change_train_time = QtWidgets.QTimeEdit()
        
        #--------------- PROGRESSBAR ---------------
        self.calculation_progressbar = QtWidgets.QProgressBar()
        self.calculation_progressbar.setRange(0,10000)
        self.calculation_progressbar.setValue(0)
        
        timer_progressbar = QtCore.QTimer(self)
        timer_progressbar.timeout.connect(self.edit_progressbar)
        timer_progressbar.start(1000)
        
        # -------------- BUTTONS ------------------
        button_search = QtWidgets.QPushButton('Suchen')
        button_delete = QtWidgets.QPushButton('Eingabe löschen')        
        
        # -------------- LABELS  ------------------
        combobox_begin_label = QtWidgets.QLabel \
            ("Abfahrtbahnhof/ -haltestelle:")
        combobox_end_label = QtWidgets.QLabel \
            ("Ankunftsbahnhof/ -haltestelle:")
        datetime_label = QtWidgets.QLabel \
            ("Datum und Uhrzeit:")
        change_train_time_label = QtWidgets.QLabel \
            ("Umstiegszeit:")
        combobox_route_label = QtWidgets.QLabel \
            ("Geschwindigkeit der Route:")
        calculation_progressbar_label = QtWidgets.QLabel \
            ("Berechnungen:")
        
        # -------------- LAYOUT  ------------------
        checkbox_layout = QtWidgets.QHBoxLayout()
        checkbox_layout.addWidget(checkbox_nah)
        checkbox_layout.addWidget(checkbox_fern)
        checkbox_layout.addWidget(checkbox_regional)
        
        combobox_layout = QtWidgets.QVBoxLayout()
        combobox_layout.addWidget(combobox_begin_label)
        combobox_layout.addWidget(self.combobox_begin)
        combobox_layout.addWidget(combobox_end_label)
        combobox_layout.addWidget(self.combobox_end)
        
        datetime_layout = QtWidgets.QHBoxLayout()
        datetime_layout.addWidget(date_field)
        datetime_layout.addWidget(time_field)
        
        organizing_times_layout = QtWidgets.QVBoxLayout()
        organizing_times_layout.addWidget(change_train_time_label)
        organizing_times_layout.addWidget(change_train_time)
        organizing_times_layout.addWidget(datetime_label)
        organizing_times_layout.addLayout(datetime_layout)
        
        route_layout = QtWidgets.QHBoxLayout()
        route_layout.addWidget(combobox_route_label)
        route_layout.addWidget(combobox_route)
        
        progress_layout = QtWidgets.QVBoxLayout()
        progress_layout.addWidget(calculation_progressbar_label)
        progress_layout.addWidget(self.calculation_progressbar)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(button_delete)
        button_layout.addWidget(button_search)
        
        sublayout = QtWidgets.QVBoxLayout()
        self.planning_page.setLayout(sublayout)
        sublayout.addLayout(checkbox_layout)
        sublayout.addLayout(combobox_layout)
        sublayout.addLayout(organizing_times_layout)
        sublayout.addLayout(route_layout)
        sublayout.addLayout(progress_layout)
        sublayout.addLayout(button_layout)
        
        #--------------------- FUNCTIONS -----------
        # Wenn die Checkboxen geklickt werden, soll sich die jeweilige Liste
        # um die angeklickte Version erweitern.
        
        # Die erstellte Liste wird in den Comboboxen angezeigt.
        
        # Die Wahl der Geschwindigkeit hat einen Einfluss auf die Route.
        
        # Wenn eine Haltestelle ausgewählt ist, soll der Verlauf in der Tabelle
        # angezeigt werden.
        
        # Die Zeit, die für die Berechnung verwendet wird, soll in der
        # Progress Bar als Prozent angegeben werden.
        
        
        self.combobox_begin.currentTextChanged.connect \
            (self.change_start_station)
            
        self.combobox_end.currentTextChanged.connect \
            (self.change_start_station)
        
        combobox_route.addItem("Kurz")
        combobox_route.addItem("Schnell")
            
        
    def edit_progressbar(self):
        """
        Edits the progressbar to show the progress.
        """
        current_value = self.calculation_progressbar.value()
        maximum_value = self.calculation_progressbar.maximum()
        self.calculation_progressbar.setValue \
            (current_value + (maximum_value - current_value) / 100)
        
    def set_extension_page(self):
        """
        Sets the conditions of the options page in the tab structurizer.
        """        
        weather_information = QtWidgets.QTextEdit()
        weather_information.setText \
            ('Hier könnten Live Daten vom Wetter' 
            '(weather.de) eingestellt werden.')
        
        news_field = QtWidgets.QTextEdit()
        news_field.setText \
            ('Hier könnten Live Nachrichten'
            '(web.de) eingestellt werden')
            
        travel_helper = QtWidgets.QTextEdit()
        travel_helper.setText \
            ('Hier könnte Angebote von Booking'
            '(booking.com) oder so reingebracht werden')
            
        troll_helper = QtWidgets.QTextEdit()
        troll_helper.setText \
            ('Hier könnte man eine Verbindung zu Bahn.de machen')

        sublayout = QtWidgets.QVBoxLayout()
        self.function_page.setLayout(sublayout)
        sublayout.addWidget(weather_information)
        sublayout.addWidget(news_field)
        sublayout.addWidget(travel_helper)
        sublayout.addWidget(troll_helper)