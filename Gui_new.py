"""
Does everything related to the map.

Classes:
    GermanyMap: QGraphicsView
        Contains the Graphicsscene of the map of Germany.

    MainWindow: QMainWindow
        Contains the main window of the program

    MenuWindowAbout: QGraphicsView
        Contains the Graphicsscene of the 'About' menu.

    MenuWindowReadMe: QGraphicsView
        Contains the Graphicsscene of the 'ReadMe' menu.

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

import re
import pandas as pd
import sys
import geojson
import os
import json
import csv
import random
import time
import calendar
import threading
import concurrent.futures
import markdown
import numpy as np

from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
from os.path import exists
from datetime import datetime


class myThread(threading.Thread):
    """
    Creating a multithread.
    """
    
    def __init__(self, all_route_ids, parent, amount_of_threads, name_dict_input):
        threading.Thread.__init__(self)
        self.name_dict = name_dict_input
        self.all_route_ids = all_route_ids
        self.parent = parent
        self.amount_of_threads = amount_of_threads

    def run(self):
        """
        Based on the 'route id'. The connections between the train stations are put together.
        """
        connections = []

        for done, route_id in enumerate(self.all_route_ids):
        
            # Gets all the trip id's from the 'route id'.
            trip_id_example_list = self.name_dict["trips"].loc[self.name_dict["trips"]["route_id"] == route_id]['trip_id'].to_numpy()
            
            # Reducing the number of trip id's to reduce the runtime.
            trip_id_example_list = set(trip_id_example_list)
            sub_stop_ids_inspected = []
            
            for trip_id_example in trip_id_example_list:
            
                # Gets all the stop names from the trip id.
                all_stops = self.name_dict["stop_times"][self.name_dict["stop_times"].trip_id == trip_id_example]
                sub_stop_ids = list(all_stops["stop_id"].to_numpy())
                
                # Creates a list of all train station connections.
                if not (sub_stop_ids in sub_stop_ids_inspected):
                    for count, stop_id in enumerate(sub_stop_ids):
                        if count != 0:
                            connections.append([stop_id,last_stop_id])
                        last_stop_id = stop_id
                    sub_stop_ids_inspected.append(sub_stop_ids)

        # Reduces the couples of recurrent station names in the list.
        df = pd.DataFrame (connections, columns = ['station_1', 'station_2'])
        group = df.groupby(['station_1', 'station_2'])
        group = pd.DataFrame(group.size())
        group.reset_index(inplace = True)
        group = group.drop(labels = [0], axis=1)

        # Reassembles the list.
        station_1 = list(group["station_1"].to_numpy())
        station_2 = list(group["station_2"].to_numpy())
        connections = [station_1,station_2]
        
        print(" Verbindungen im Thread erstellt.")

        # Writes to the main class
        while True:
            if self.parent.add_connections(connections):
                break
            time.sleep(0.01)
        
        # If all threads are done the main code can be run.
        self.parent.threads_done += 1
        if self.parent.threads_done == self.amount_of_threads:
            self.parent.keep_going()

class connections(threading.Thread):
    """
    Calculates a list of connections between train stations,
    based of GTFS data
    """
    
    def __init__(self, data_class, data_type):
        """
        Determines which GTFS data is used and sets the name
        of the resulting file.
        """
        threading.Thread.__init__(self)
        self.data_class = data_class
        self.data_type = data_type

        # Sets the variables to the needed type.
        if self.data_type == "long_distance":
            self.name_dict = self.data_class.gtfs_fern
            self.name = 'connections_fern.csv'
        if self.data_type == "regional":
            self.name_dict = self.data_class.gtfs_regional
            self.name = 'connections_regional.csv'
        if self.data_type == "short_distance":
            self.name_dict = self.data_class.gtfs_nah
            self.name = 'connections_nah.csv'

    def run(self):
        """
        Gets the list of route ids and distributes them to new threads.
        """
        self.threads_done = 0
        self.add_connections_active = 0
        self.connections = [[],[]]
        
        # Gets the route id's to get the connections.
        all_route_ids = self.name_dict["routes"]["route_id"].to_numpy()

        # If all_route_ids is smaller than 2 the list is incorrect
        if len(all_route_ids) <= 1:
            print("len(all_route_ids) ",len(all_route_ids))
            exit()

        # Starts with 64 threads for big data sets, if needed the amount is reduced.
        amount_of_threads = 64
        
        while amount_of_threads > len(all_route_ids):
            amount_of_threads = int(amount_of_threads/2)

        # The threads are set and started.
        step_size = int(len(all_route_ids)/(amount_of_threads-1))
        
        for i in range(amount_of_threads-1):
            to_check_all_route_ids = all_route_ids[0:step_size]
            all_route_ids =  all_route_ids[step_size:]
            myThread(to_check_all_route_ids, self, amount_of_threads, self.name_dict).start()
        myThread(all_route_ids, self, amount_of_threads, self.name_dict).start()

    def add_connections(self, add):
        """
        To avoid conflicts only one thread is allowed to write at a time.
        """
        
        if self.add_connections_active == 0:
            self.add_connections_active = 1

            self.connections[0] = self.connections[0] + add[0]
            self.connections[1] = self.connections[1] + add[1]

            self.add_connections_active = 0

            return True
        else:
            return False

    def keep_going(self):
        """
        Based on the collected train station couples a new dataframe of longitude
        and latitude values is created and printed to a csv file.
        """
        # Reduces the couples of recurrent station names in the list.
        d = {'station_1':self.connections[0], 'stop_id':self.connections[1]}
        df = pd.DataFrame (d)
        group = df.groupby(['station_1', 'stop_id'])
        group = pd.DataFrame(group.size())
        group.reset_index(inplace = True)
        group = group.drop(labels= [0], axis = 1)

        # Replaces the stop id's with the longitude and latitude values.
        new_df = pd.merge(self.name_dict["stops"],group)
        new_df.rename(columns = {'stop_lat':'Station1_lat', 'stop_lon':'Station1_lon'}, inplace = True)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stachen_1': 'stop_id'}, inplace = True)
        new_df = pd.merge(self.name_dict["stops"],new_df)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stop_lat':'Station2_lat', 'stop_lon':'Station2_lon'}, inplace = True)

        # Writes the data.
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data/" + self.name))
        new_df.to_csv(path)

        # Depending of the type, one file is restored.
        if self.data_type == "long_distance":
            self.data_class.free_fern_add_1()
        
        if self.data_type == "short_distance":
            self.data_class.free_nah_add_1()
        
        if self.data_type == "regional":
            self.data_class.free_regional_add_1()
        
class mapWidget(QtWidgets.QMainWindow):
    """
    Creates the main window for the map.
    """

    def __init__(self, main_gui):
        super().__init__()
        self.main_gui = main_gui
        self.germany_map = germanyMap(self)

    def draw_route_network(self, train_stations, filename_routes):
        self.germany_map.draw_route_network(train_stations, filename_routes)

class germanyMap(QtWidgets.QGraphicsView):
    """
    Graphicsscene of the map of Germany.
    """
  
    # Signals to react to mouse movement and clicking
    currentStation = QtCore.Signal(str)
    stationClicked = QtCore.Signal(str)

    def __init__(self, map_gui):
        """
        Creates a widget for the map.
        """
        super().__init__()

        self.main_gui = map_gui.main_gui
        self.map_gui = map_gui

        self.setMinimumSize(140, 180)
        self.setMouseTracking(True)
        self.previous_item = None
 
        self.pens_and_brushes() 

        self.zoom = 0
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        """
        Enables Zoom while using the mouse wheel.
        According to:
        https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
        """
        
        if event.angleDelta().y() > 0:
            factor = 1.25
            self.zoom += 1
        else:
            factor = 0.9
            self.zoom -= 1
        if self.zoom > 0:
            self.scale(factor, factor)
        elif self.zoom == 0:
            self.fitInView(self.sceneRect())
        else:
            self.zoom = 0

    def mousePressEvent(self, event):
        """
        Reacts to clicking of the mouse.
        """
        
        item = self.itemAt(event.pos())
        if item is not None:
            try:
                self.stationClicked.emit(item.station)
            except:
                pass
            
    def mouseMoveEvent(self, event):
        """
        Is used to track the items touched by the mouse and change their color.
        """
        
        item = self.itemAt(event.pos())

        # If all error messages are ignored, there are no error messages left.
        if self.previous_item is not None:
            try:
                self.previous_item.setBrush(QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = None
            
        if item is not None:
            try:
                item.setBrush(QtGui.QBrush("grey", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = item
            try:
                self.currentStation.emit(item.station)
            except:
                pass

    def resizeEvent(self, event):
        """
        Enables the widget to be resized properly.
        """
        
        scene_size = self.sceneRect()
        dx = (self.width()-4)/scene_size.width()
        dy = (self.height()-4)/scene_size.height()
        self.setTransform(QtGui.QTransform.fromScale(dx, -dy))

    def sizeHint(self):
        """
        Return of the preferred default size of the widget.
        """
        
        return QtCore.QSize(140*4, 180*4)

    def pens_and_brushes(self):
        """
        Contains all pens and brushes.
        """

        self.ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.BDiagPattern)
        self.country_pen = QtGui.QPen("black")
        self.country_pen.setWidthF(0.01)
        self.land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.point_pen = QtGui.QPen("red")
        self.point_pen.setWidthF(0.05)
        self.point_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.line_pen = QtGui.QPen("orange")
        self.line_pen.setWidthF(0.02)

    def draw_route_network(self, train_stations, routes):
        """
        Draws stations and routes to the base scene.

        Parameters:
            train_stations: 
                Pandas Dataframe containing names and
                coordinates of the train stations
            filename_routes: str
                Name of the file containing the routes
        """

        self.make_base_scene()

        # Drawing the stations 
        for one_station in train_stations.itertuples():
            whole_station_information = [(one_station.stop_lat, one_station.stop_lon),one_station.stop_name]
            station_information_coordinates = [[one_station.stop_lat, one_station.stop_lon]]
                
            for y,x in station_information_coordinates:
                width = 0.02
                height = 0.02
                point_item = self.map_gui.scene.addEllipse(x,y,width,height, pen=self.point_pen, brush=self.point_brush)
                point_item.station = y,x

                if point_item.station in whole_station_information:
                    point_item.station = whole_station_information[1]
        
        # Drawing the routes
        for start in routes.itertuples():
            y1,x1 = [start.Station1_lat, start.Station1_lon]
            
            y2,x2 = [start.Station2_lat, start.Station2_lon]
            self.map_gui.scene.addLine(x1,y1,x2,y2, pen=self.line_pen)
            
        self = germanyMap(self.map_gui)
        self.setScene(self.map_gui.scene)
        self.scale(10, -10)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.currentStation.connect(self.main_gui.status_bar.showMessage)
        self.stationClicked.connect(self.main_gui.click_function)

        self.main_gui.grid_layout.addWidget(self,0,0)

    def make_base_scene(self):
        """
        Creating the base scene, which shows the map of Germany.
        """

        self.map_gui.scene = QtWidgets.QGraphicsScene(5.8, 47.3, 9.4, 7.9) 
        states = self.main_gui.model.get_counts()

        # Drawing map of Germany
        for state in states:
            if state['geometry']['type'] == 'Polygon':
                for polygon in state['geometry']['coordinates']:
                    qpolygon = QtGui.QPolygonF()
                    for x, y in polygon:
                        qpolygon.append(QtCore.QPointF(x, y))
                    polygon_item = self.map_gui.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                    polygon_item.station = state['properties']['GEN']
                   
            else:
                for polygons in state['geometry']['coordinates']:
                    for polygon in polygons:
                        qpolygon = QtGui.QPolygonF()
                        for x, y in polygon:
                            qpolygon.append(QtCore.QPointF(x, y))
                        polygon_item = self.map_gui.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                        polygon_item.station = state['properties']['GEN']
                       
                    self.map_gui.scene.setBackgroundBrush(self.ocean_brush)

class menuWindowAbout(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'About' menu in the menubar.
    """
    
    def __init__(self,model):
        """
        Creates a widget for the About menu.
        """
        
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)

        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_about_text())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        
        return QtCore.QSize(700, 600)

class menuWindowReadMe(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'ReadMe' menu in the menubar.
    """
    
    def __init__(self,model):
        """
        Creates a widget for the ReadMe menu.
        """
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)
        
        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_readme_text())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        return QtCore.QSize(600, 600)

class menuWindowTutorial(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'Tutorial' menu in the menubar.
    """
    
    def __init__(self, model):
        """
        Creates a widget for the Tutorial menu.
        """
        
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)
        
        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_tutorial())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        
        return QtCore.QSize(1000, 1000)

class sideWindow(QtWidgets.QMainWindow):
    """
    Creating an interactive widget next to the german map.
    """

    def __init__(self, main_gui):
        """
        Instantiate the main aspects of an interactive planner. 
        It contains the comboboxes, textfields, labels, layouts and buttons.       
        """
        
        super().__init__()
        self.main_gui = main_gui
        self.setMinimumSize(250, 450)
        
        # -------------- COMBOBOXES ----------------
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Bahnhof wählen -")
        self.combobox_start.currentTextChanged.connect(self.change_start_station)
        
        # -------------- TEXT FIELDS ----------------
        self.textfield_date = QtWidgets.QDateEdit()
        start_date = datetime(2022, 0o1, 0o1)
        end_date = datetime(2022, 12, 31)
        self.textfield_date.setDateRange(start_date,end_date)
        
        self.textfield_time = QtWidgets.QTimeEdit()
        self.textfield_time_dif = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
        self.text = ""
        self.update_text(" ")
        
        # -------------- LABELS  ------------------
        label_button_traffic_style = QtWidgets.QLabel("Bahnart:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_textfield_date_time = QtWidgets.QLabel("Datum und Zeit der Abfahrt:")
        self.label_textfield_time_dif = QtWidgets.QLabel("Zeitfenster")
        label_textfield_allInfo = QtWidgets.QLabel("Besondere Informationen:")
        label_button_request = QtWidgets.QLabel("Daten zum Bahnhof erstellen:")

        # -------------- BUTTONS ------------------
        self.button_nahverkehr = QtWidgets.QPushButton("Nahverkehr")
        self.button_fernverkehr = QtWidgets.QPushButton("Fernverkehr")
        self.button_regional = QtWidgets.QPushButton("Regional")
        self.button_request = QtWidgets.QPushButton("Anfrage stellen")
        # Anpassen des Knopfes, weil er noch zu groß ist.
        # self.button_request.QtCore.QSize(40,40)

        self.button_fernverkehr.clicked.connect(self.click_function_long_distance)
        self.button_nahverkehr.clicked.connect(self.click_function_short_distance)
        self.button_regional.clicked.connect(self.click_function_regional)
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

        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addWidget(label_button_traffic_style)
        sub_layout.addLayout(button_layout_traffic)
        sub_layout.addWidget(label_combobox_start) 
        sub_layout.addWidget(self.combobox_start)
        sub_layout.addWidget(label_textfield_date_time)
        sub_layout.addLayout(date_time_layout)
        sub_layout.addWidget(self.label_textfield_time_dif)
        sub_layout.addLayout(time_dif_layout)
        sub_layout.addLayout(button_request_layout)
        sub_layout.addWidget(label_textfield_allInfo)
        sub_layout.addWidget(self.textfield_allInfo)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(sub_layout)
        self.setCentralWidget(window_content)
        self.set_train_stations_list()

    def set_train_station(self, new_station):
        """
        Changes the station in the sidebar and requests new station information
        """
        self.combobox_start.setCurrentText(new_station)
        self.start_station = new_station
        self.train_station_request()
 
    def update_text(self, new_info):
        """
        Puts the new information into the text and if necessary, deletes the old
        ones.
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

        self.main_gui.model.change_train_station_info(time_span, day, hour, minute, self.start_station)

class tableCreator(QtCore.QAbstractTableModel):
    """
    Creates a table with the main functions: rowCount, columnCount, data and headerData.
    These functions are setting the size of the matrix and a clear arrangement.
    """
    
    def __init__(self, df):
        """
        Sets the dataframe for the table view.
        """
        super().__init__()
        self.dataframe = df
        
        
    def rowCount(self, parent = None): 
        """
        Sets the amount of the rows of the read file.
        """
        self.number = len(self.dataframe[0:])
        return self.number
        
    def columnCount(self, parent = None): 
        """
        Sets the amount of the columns of the read file.
        """
        return len(self.dataframe.keys())
        
    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        Shows the file components.
        """
        if role != QtCore.Qt.DisplayRole:
            return None
            
        value = self.dataframe.iloc[index.row(), index.column()]
        return str(value)
            
    def headerData(self, index, orientation, role = QtCore.Qt.DisplayRole):
        """
        Shows the head of the columns seperately.
        """
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Orientation.Horizontal:
           return None
        
        return self.dataframe.columns[index] 
 
class dataTable(QtWidgets.QMainWindow):
    """
    Contains data table for train station information.
    """

    def __init__(self, main_gui):
        """
        Takes the file components of the 'tableCreator', creates a widget and merges
        them together. 
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
        """
        table_model = tableCreator(train_station_info)
        self.table_view.setModel(table_model)

class mainWindow(QtWidgets.QMainWindow):
    """
    Creates the main window of the GUI.
    """
    
    def __init__(self, model):
        """
        Creates the main frame of the GUI with grid layout and adds all subframes.
        """
        super().__init__()

        self.model = model

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
        self.germany_map.draw_route_network(train_stations, filename_routes)
        
    def open_about(self):
        """
        Shows the window of the 'About' menu.
        """
        about_window.show()
    
    def open_readme(self):
        """
        Shows the window of the 'ReadMe' menu. 
        """
        readme_window.show()

    def open_tutorial(self):
        """
        Shows the window of the 'Tutorial' menu. 
        """
        tutorial_window.show()

    @QtCore.Slot(str)
    def click_function(self, whole_station_information):
        """
        Reacts to clicking of the mouse.
        """
        if whole_station_information in self.model.get_current_stops()["stop_name"].to_numpy():
            self.side_window_instance.set_train_station(whole_station_information)

    def train_station_show(self):
        table_view = QtWidgets.QTableView()
        table_model = tableCreator()
        table_view.setModel(table_model)
        
        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.addWidget(table_view)
        
        self.layout.addLayout(sub_layout)
        
class model():
    """
    modell is 
    """

    def __init__(self,all_data):
        """
        Sets the basic values.
        """
        self.all_data = all_data
        self.all_data.set_model(self)
        self.train_station_info = None
        self.get_first_data()

    def get_first_data(self):
        # dependig if the data set is corect the set is lodet
        ## HIER BIN ICH MIR WEGEN DER ÜBERSETZUNG NICHT SICHER.
        """
        Depending on the data. If the set is correct, it will be loaded.
        """

        if self.all_data.load_first:
            # set is coreckt and is lodet
            # Checks for correctness and loads the data.
            self.current_stops = self.all_data.get_stops_fern()
            self.current_connections = self.all_data.get_connections_fern()
            self.current_gtfs = self.all_data.gtfs("latest_fern")
        else:
            #set incoreckt and is blockt
            # The incorrect data set is blocked.
            self.all_data.delighted_category_options.append("stops_fern")
            
            # Tries to restore the lost data.
            if not (self.all_data.gtfs("latest_fern") == None):
                self.all_data.restore("fern")

            # Loads the new data.
            self.current_stops = self.all_data.get_stops_regional()
            self.current_connections = self.all_data.get_connections_regional()
            self.current_gtfs = self.all_data.gtfs("latest_regional")
            
            # Checks the new data.
            if (self.current_stops[1] == False) or (self.current_connections[1] == False) or (self.current_gtfs == None):
                self.all_data.delighted_category_options.append("stops_regional")
                if not (self.all_data.gtfs("latest_regional") == None):
                    self.all_data.restore("regional")
                self.current_stops = self.all_data.get_stops_nah()
                self.current_connections = self.all_data.get_connections_nah()
                self.current_gtfs = self.all_data.gtfs("latest_nah")
                if (self.current_stops[1] == False) or (self.current_connections[1] == False) or (self.current_gtfs == None):
                    self.all_data.delighted_category_options.append("stops_nah")
                    if not (self.all_data.gtfs("latest_nah") == None):
                        self.all_data.restore("nah")
                    print("Es sind unvollständige Datensets vorhanden. Daraus folgt eine Einschränkung der Bedienbarkeit.")
        
    def set_main_gui(self, main_gui):
        self.main_gui = main_gui
        self.all_data.text_feald_update(" ")

    def get_current_stops(self):
        return self.current_stops[0]

    def get_connections(self):
        return self.current_connections[0]

    def change_current_stops(self, new_type):
        """
        If the category is available, it can be chosen.
        """

        if not (new_type in self.all_data.delighted_category_options):
        
            # Saves the current status as a backup
            start_values = [self.current_stops,self.current_connections,self.current_gtfs]

            # Loads the data, based on the type
            if new_type == "stops_fern":
                self.current_stops = self.all_data.get_stops_fern()
                self.current_connections = self.all_data.get_connections_fern()
                self.current_gtfs = self.all_data.gtfs("latest_fern")
                
            if new_type == "stops_nah":
                self.current_stops = self.all_data.get_stops_nah()
                self.current_connections = self.all_data.get_connections_nah()
                self.current_gtfs = self.all_data.gtfs("latest_nah")
                
            if new_type == "stops_regional":
                self.current_stops = self.all_data.get_stops_regional()
                self.current_connections = self.all_data.get_connections_regional()
                self.current_gtfs = self.all_data.gtfs("latest_regional")

            # If the data is incorrect
            if (self.current_gtfs == None) or (self.current_stops[1]==False) or (self.current_connections[1]==False):
                
                # The backup is used to restore the first values
                self.current_stops = start_values[0]
                self.current_connections = start_values[1]
                self.current_gtfs = start_values[2]
                
                # is tyt to resor data form every kategory, mait not be nasesery most times
                ## HIER BIN ICH MIR BEI DER ÜBERSETZUNG NICHT SICHER.
                # Is typed to restore data from every category, might not be necessary mostly.
                self.all_data.restore("fern")
                self.all_data.restore("nah")
                self.all_data.restore("regional")
            else:
                # The gui loades new data and shows it.
                self.main_gui.draw_route_network(self.get_current_stops(),self.get_connections()) 
        
    def get_about_text(self):
        return self.all_data.about_text

    def get_readme_text(self):
        return self.all_data.readme_text

    def get_tutorial(self):
        return self.all_data.tutorial_text

    def get_counts(self):
        return self.all_data.counts

    def change_train_station_info(self, time_span, day, hour, minute, train_station):
        """
        Calculates new train station data and fills it in.
        """
        self.train_station_info = self.all_data.create_train_station_info([day, hour, minute], train_station, time_span, self.current_gtfs)
        self.main_gui.dataTable_instance.set_dataframe(self.train_station_info)
        
    def text_feald_update(self,new_info):
        self.main_gui.side_window_instance.update_text(new_info)

class data(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.delighted_category_options = []
        self.model_set = False
        self.q_text = " "

        # Loads necessary and little data for the first overview.
        self.counts = self.load_map_data()
        self.about_text = self.load_about_text()
        self.readme_text = self.load_readme_text()

        self.tutorial_text = self.load_tutorial()
        self.stops_fern = self.load_text('stops_fern.txt')
        self.connections_fern = self.load_text('connections_fern.csv')
        self.gtfs_fern = self.load_gtfs("latest_fern")

        # Checks if the first files are ok, or if a different files needed to be chosen.
        self.load_first = True
        if (self.stops_fern[1] == False) or (self.connections_fern[1] == False) or (self.gtfs_fern == None):
            self.load_first = False

        # Presents the gtfs variables, therefore they can be checked, if they already have been loaded.
        self.gtfs_nah = None
        self.gtfs_regional = None
        
        # Values determing, if the variable is set. 
        self.connections_nah_set = False
        self.connections_regional_set = False
        self.stops_regional_set = False
        self.stops_nah_set = False

        # The loading of the rest of the data is stated.
        threading.Thread(target = self.gtfs_prep).start()
        
        # The time delay is needed, though every running process is started.
        # thes nesesry becas the modell class myd aces them
        # HIER BIN ICH MIR BEI DER ÜBERSEETZUNG NICHT SICHER.
        # This is necessary, becaus the class 'model' made access them.
        time.sleep(0.1)

    def set_model(self,model):
        self.model = model
        self.model_set = True

    def text_feald_update(self,new_text):
        if self.model_set == True:
            if self.q_text != " ":
                self.model.text_feald_update(self.q_text)
                self.q_text = " "
            self.model.text_feald_update(new_text)
        else:
            self.q_text = self.q_text + "\n" + new_text


    def restore(self, key):
        """
        HIER NOCH EIN KOMMENTAR WAS DIESE METHODE TUT.
        """# based on the key, if files are missing they are recreatet and can be uese after that

        # If the key fits and there is data to be restored.
        if key == "fern" and ("stops_fern" in self.delighted_category_options):
        
            # If the main data set is there. 
            #(nedert for restoring)HIER BIN ICH MIR NICHT SICHER, WAS DAS BEDEUTET.
            if not (self.gtfs_fern == None):
            
                # Value represents how much of the type is correct.
                self.free_fern = 0
                
                # If 'connections_fern' is wrong, a new file is created.
                if self.connections_fern[1] == False:
                    connections(self,"long_distance").run() 
                else:
                    # 'Connections_fern' is correct.
                    self.free_fern_add_1()
                    
                if self.stops_fern[1] == False:
                    self.restore_train_station_by_type("fern")
                else:
                    self.free_fern_add_1()

        if key == "nah" and ("stops_nah" in self.delighted_category_options):
            if not (self.gtfs_nah == None):
                self.free_nah = 0
                if self.connections_nah[1] == False:
                    connections(self,"short_distance").run() 
                else:
                    self.free_nah_add_1()
                if self.stops_nah[1] == False:
                    self.restore_train_station_by_type("nah")
                else:
                    self.free_nah_add_1()

        if key == "regional" and ("stops_regional" in self.delighted_category_options):
        
            if not (self.gtfs_regional == None):
                self.free_regional = 0
                if self.connections_regional[1] == False:
                    connections(self,"regional").run() 
                else:
                    self.free_regional_add_1()
                if self.stops_regional[1] == False:
                    self.restore_train_station_by_type("regional")
                else:
                    self.free_regional_add_1()

    def restore_train_station_by_type(self, data_type):
        if data_type == "fern":
            self.restore_train_station_by_name(self.gtfs_fern, 'stops_fern.txt')
            self.free_fern_add_1()
            
        if data_type == "nah":
            self.restore_train_station_by_name(self.gtfs_nah, 'stops_nah.txt')
            self.free_nah_add_1()
            
        if data_type == "regional":
            self.restore_train_station_by_name(self.gtfs_regional, 'stops_regional.txt')
            self.free_regional_add_1()

    def restore_train_station_by_name(self, name_dict, name):
        # baist of the given data and name, a new data set is created and saived

        #gets all train stachn names and drops all mutepils
        df = pd.DataFrame(name_dict["stops"], columns =['stop_name'])
        df = df.drop_duplicates(subset = ["stop_name"])
        # based on the index the informachen of the trainstachen is colected
        index = df.index
        df = name_dict["stops"].loc[index]
        # the (überflüssige) colum is droped
        train_station = df.drop(labels=["stop_id"], axis=1)

        # writing the new data set
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data/" + name))
        pd.DataFrame(train_station).to_csv(path)

    def free_regional_add_1(self):
        # increases the number of restored files by 1.
        # if all files are restored, the data is riten and the option is reinsated
        self.free_regional += 1
        
        # The dataset is fully restored and can be loaded and the category is available again.
        if self.free_regional == 2:
            self.stops_regional = self.load_text('stops_regional.txt')
            self.connections_regional = self.load_text('connections_regional.csv')
            self.delighted_category_options.remove("stops_regional")

    def free_fern_add_1(self):
        self.free_fern += 1
        
        if self.free_fern == 2:
            self.stops_fern = self.load_text('stops_fern.txt')
            self.connections_fern = self.load_text('connections_fern.csv')
            self.delited_kategorie_opchens.remove("stops_fern")

    def free_nah_add_1(self):
        self.free_nah += 1
        
        if self.free_nah == 2:
            self.stops_fern = self.lode_text('stops_nah.txt')
            self.connections_fern = self.lode_text('connections_nah.csv')
            self.delighted_category_options.remove("stops_nah")

    def gtfs_prep(self):
        """
        Every file gets its own loading thread, which is safer in the variable on the left.
        """# Every file gets its own loading thread, which is saifed in the variable.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.gtfs_nah_pre = executor.submit(self.load_gtfs, "latest_nah")
            self.gtfs_regional_pre = executor.submit(self.load_gtfs, "latest_regional")
            self.connections_nah_pre = executor.submit(self.load_text, "connections_og.csv")
            self.connections_regional_pre = executor.submit(self.load_text, "connections_regional.csv")
            self.stops_regional_pre = executor.submit(self.load_text, "stops_regional.txt")
            self.stops_nah_pre = executor.submit(self.load_text, "stops_nah.txt")

    def get_stops_fern(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the value is incorrect, the category option is delighted and a (restrachen) ?? is tried
        """
        if self.stops_fern[1] == False:
            if not ("stops_fern" in self.delighted_category_options):
                self.delighted_category_options.append("stops_fern")
            self.restore("fern")

        return self.stops_fern

    def get_stops_nah(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the value is not pulled, its done now. if the value is incorecht, the kategory option is closed
        and a restrachen is tryed
        """
        if not self.stops_nah_set:
            self.stops_nah_set = True
            self.stops_nah = self.stops_nah_pre.result()
            
            if self.stops_nah[1] == False:
            
                if not ("stops_nah" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_nah")
                self.restore("nah")
                
        return self.stops_nah

    def get_stops_regional(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the value is not pulled, its done now. If the value is incorrect, the category option is closed
        and a restrachen is tryed
        """
        if not self.stops_regional_set:
            self.stops_regional_set = True
            self.stops_regional = self.stops_regional_pre.result()
            
            if self.stops_regional[1] == False:
            
                if not ("stops_regional" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_regional")
                self.restore("regional")

        return self.stops_regional

    def get_connections_regional(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the value is not pulled, it's done now. If the value is incorrect, the category option is closed
        and a restrachen is tryed
        """
        if not self.connections_regional_set:
            self.connections_regional_set = True
            self.connections_regional = self.connections_regional_pre.result()
            
            if self.connections_regional[1] == False:
            
                if not ("stops_regional" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_regional")
                self.restore("regional")

        return self.connections_regional

    def get_connections_nah(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the value is not pulled, its done now.If the value is incorrect, the category option is closed
        and a restrachen is tryed
        """
        if not self.connections_nah_set:
            self.connections_nah_set = True
            self.connections_nah = self.connections_nah_pre.result()
            
            if self.connections_nah[1] == False:
            
                if not ("stops_nah" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_nah")
                self.restore("nah")
                
        return self.connections_nah

    def get_connections_fern(self):
        ## HIER BIN ICH MIR BEI DER ÜBERSEETZUNG UNSICHER.
        """
        If the valuue is incorecht, the kategory option is closed and a restrachen is tryed
        """
        if self.connections_fern[1] == False:
        
            if not ("stops_fern" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_fern")
                    
            self.restore("fern")
            
        return self.connections_fern

    def gtfs(self, category):
        """
        The gtfs are pulled if needed. If gtfs data is missing, the option is closed.
        """ # The gtfs are pulled if needed. If gtfs data is missing, the option to uste the given kategorie is closed.
        if category == "latest_nah":
        
            if self.gtfs_nah == None:
                self.gtfs_nah = self.gtfs_nah_pre.result()
                
                if self.gtfs_nah == None:
                    self.delighted_category_options.append("stops_nah")
                    
            return self.gtfs_nah

        if category == "latest_fern":
        
            if self.gtfs_fern == None:
                self.delighted_category_options.append("stops_fern")
                
            return self.gtfs_fern

        if category == "latest_regional":
        
            if self.gtfs_regional == None:
                self.gtfs_regional = self.gtfs_regional_pre.result()
                
                if self.gtfs_regional == None:
                    self.delighted_category_options.append("stops_regional")
                    
            return self.gtfs_regional

    def load_gtfs(self, category):

        # Creates path
        path_start = os.path.abspath(os.path.join(os.path.dirname( __file__ ), category))+ '\\'
        data_names = ['agency','calendar','calendar_dates','feed_info','routes','stop_times','stops','trips']
        name_dict = {}

        gtfs_is_missing_files = False

        # Reads in all the data.
        for name in data_names:
            path = path_start + name + '.txt'
            
            if exists(path):
                df = pd.read_csv(path)
                name_dict[name] = df

            else:
                # If data is not found the user is informed.
                print("Die Datei " + name + " wurde nicht Gefunden")
                print(os.path.abspath(os.path.join(os.path.dirname( __file__ ), name + '.txt')))
                gtfs_is_missing_files = True

        # If the data is not found, the user is informed.
        if gtfs_is_missing_files:
            print(" \n \n")
            print("da die daten von " + category + " nicht geladen werden konten \n Kann man diese auch nicht aus welen")
            return None

        return name_dict

    def load_map_data(self):
        """
        Loads the data of the map of Germany.
        Source of the file:
        http://opendatalab.de/projects/geojson-utilities/
        """
        path_to_map = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/landkreise_simplify200.geojson'))
        
        if exists(path_to_map):
        
            with open(path_to_map,encoding='utf8') as f:
                data = geojson.load(f)
                f.close()
            states = data['features']

            return states
            
        else:
            text = "the landkreise_simplify200.geojson file is missing."
            text = text + "\n" + "ists a criticel pat, therfor the program is shatig down."
            text = text + "\n" + "the data is awaleble at http://opendatalab.de/projects/geojson-utilities/"
            self.text_feald_update(text)
            print(text)
            #exit()

    def load_about_text(self):
        """
        Opens the 'About' file and prints it in a label of a new window.
        """# lodes the 'About' file and reterns it
        
        path_to_about = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/ABOUT.md'))
        
        if exists(path_to_about):
        
            with open(path_to_about, encoding='utf8') as about_file:
                about_text = about_file.read()
                about_file.close()
                
            return about_text
        else:
            return "No ABOUT text was found"

    def load_readme_text(self):
        """
        Opens the 'ReadMe' file and prints it in a label of a new window.
        """ # Opens the 'ReadMe' file and ajust the path to a dynamic one.
        #and reterns the result.
        
        path_str = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data")) + "\\" 
        path_to_readme = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/README.md'))
        
        if exists(path_to_readme):
        
            with open(path_to_readme, encoding='utf8') as readme_file:
                readme_text = readme_file.read()
                readme_file.close()
                
                # The dynamic path is inserted
                readme_text = readme_text.replace("/////", path_str)
                readme_text_md = markdown.markdown(readme_text)
                
            return readme_text_md
        else:
            return "No README text was found"

    def load_tutorial(self):
        """
        Opens the 'Tutorial' file and prints it in a label of a new window.
        """
        
        path_str = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data")) + "\\" 
        path_to_tutorial = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/TUTORIAL.md'))
        
        if exists(path_to_tutorial):
        
            with open(path_to_tutorial, encoding='utf8') as tutorial_file:
                tutorial_text = tutorial_file.read()
                tutorial_file.close()
                
                # The dynamic path is inserted
                tutorial_text = tutorial_text.replace("/////", path_str)
                tutorial_text_md = markdown.markdown(tutorial_text)
                
            return tutorial_text_md
        else:
            return "No TUTORIAL text was found"

    def load_text(self, filename_routes):
        """
        Loads the file with the routes.
        """# Loads a given file and reterns it.
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/' + filename_routes))
        
        if exists(path):
            routes = pd.read_csv(path, encoding='utf8')
            
            # An indication, if the reading was successfull, it is included.
            return [routes,True]
        return [None,False]

    def orders_ackording_to_time(self,hour,minute,connections_df):
        # chanhes the dataframe order baset on the time in "Einfahrtszeit"

        connections_df = connections_df.sort_values(by=['Einfahrtszeit'])
        actual_time = str(hour) + ":" + str(minute) + ":00"

        connections_df_firs = connections_df.loc[connections_df["Einfahrtszeit"] >= actual_time]
        connections_df_sec = connections_df.loc[connections_df["Einfahrtszeit"] < actual_time]

        return pd.concat([connections_df_firs,connections_df_sec])

    def geting_sevis_days(self,name_dict,trip_id_instance):
        # geting the sevis id from given trip id
        trips_trip_id = name_dict["trips"].loc[name_dict["trips"]["trip_id"] == trip_id_instance]
        service_id_instance = trips_trip_id['service_id'].to_numpy()[0]
        service_days = name_dict["calendar"].loc[name_dict["calendar"]["service_id"] == service_id_instance]
        return service_days,trips_trip_id

    def create_train_station_info(self, date, train_station_name, time_span, name_dict):

        # if ther is no time, ther cant be anny trains (driving ?)
        if time_span <= 0:
            return pd.DataFrame([["Keine Züge gefunden"]], columns=["Info"])

        day_given = date[0]
        hour = date[1]
        minute = date[2]

        # get trip_id_IDs stoping at the treanstachen
        stop_IDs = name_dict["stops"].loc[name_dict["stops"]["stop_name"] == train_station_name]['stop_id'].to_numpy()        
        trip_id_IDs = set(name_dict["stop_times"].loc[name_dict["stop_times"]["stop_id"].isin(stop_IDs)]['trip_id'].to_numpy())

        # counter contanig how many lines are addet on the Dataframe
        connections_df_counter = int(0)
        
        for trip_id_instance in trip_id_IDs:

            # geting the sevis id from given trip id
            service_days , trips_trip_id = self.geting_sevis_days(name_dict,trip_id_instance)

            if not service_days.empty:
                
                # get from the rout the trip ids and ter stop ant the given transtachen
                stop_times_trip_id_instance = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instance]
                trip_id_stops = stop_times_trip_id_instance.loc[stop_times_trip_id_instance["stop_id"].isin(stop_IDs)]

                # determens the arrival time and how many days in the futur this is
                arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
                arrival_time_hour = int(arrival_time[0:2])
                days_over = int(arrival_time_hour / 24)

                day = day_given
                time_difference = 0
                
                # if the train stop is in the futur, based on the servis day
                # the previs servis day needs to be chckt
                if days_over > 0:
                    # ariveltime on this day
                    arrival_time_hour_str = str(arrival_time_hour - (24 * days_over))
                    
                    # ajustirt the str to tow leters
                    if len(arrival_time_hour_str) == 1:
                        arrival_time_hour_str = "0" + arrival_time_hour_str

                    # re arange the arrival_time string to the given day
                    arrival_time = arrival_time_hour_str + arrival_time[2:]

                    # calculates the servisday thad needs to be checkt
                    day = day_given - days_over
                    if (int(arrival_time[0:2]) < hour) or (int(arrival_time[0:2]) < hour) and (int(arrival_time[3:5]) < minute):
                        day = day + 1
                        time_difference = 24 * 60
                        
                    # ajustirt the day bast on a skale 0-6
                    if day < 0:
                        day = day + 7

                    # calculates the time_difference
                    time_difference = time_difference + (int(arrival_time[0:2]) - hour) * 60 + (int(arrival_time[3:5]) - minute)
                    
                else:
                    # calculates the time_difference
                    time_difference = (int(arrival_time[0:2])- hour) * 60 + (int(arrival_time[3:5])- minute)

                day_is_served = service_days[calendar.day_name[day].lower()].to_numpy()[0]
                
                # only if the rout is served and the the ariveltime is in the futur
                if (day_is_served == 1) and (time_difference > 0 and time_difference < time_span * 60):

                    # gets the highest stop_sequence, witch is a and stachen
                    last_station = max(stop_times_trip_id_instance['stop_sequence'].to_numpy())
                    direction = trips_trip_id['direction_id'].to_numpy()[0]
                    
                    # depending on the direction the end atachen is shosen
                    if direction == 0:
                        end_station = last_station
                    else:
                        end_station = 0

                    # gets the name of the destinachen train stachen
                    end_station_stop_id = stop_times_trip_id_instance.loc[stop_times_trip_id_instance["stop_sequence"] == end_station]['stop_id'].to_numpy()[0]
                    end_station_name = name_dict["stops"].loc[name_dict["stops"]["stop_id"] == end_station_stop_id]['stop_name'].to_numpy()[0]

                    #gets the row routes of the route id
                    route_id_instance = trips_trip_id['route_id'].to_numpy()[0]
                    routes_row = name_dict["routes"].loc[name_dict["routes"]["route_id"] == route_id_instance]

                    # retrivs the informachen of the trip 
                    agency_id_instance = routes_row['agency_id'].to_numpy()[0]
                    agency_name_instance = name_dict["agency"].loc[name_dict["agency"]["agency_id"] == agency_id_instance]['agency_name'].to_numpy()[0]
                    route_long_name = routes_row['route_long_name'].to_numpy()[0]
                    departure_time = trip_id_stops['departure_time'].to_numpy()[0]

                    # the trip is addes to the dataframe
                    if connections_df_counter == 0:
                        connections_df = pd.DataFrame([[agency_name_instance, route_long_name, end_station_name, arrival_time, departure_time]], columns=["Betreiber","Zugbezeichnung","Endstation","Einfahrtszeit","Abfahrtszeit"])
                    else:
                        connections_df.loc[connections_df_counter] = [agency_name_instance, route_long_name, end_station_name, arrival_time, departure_time]
                    connections_df_counter += 1

        # reterns Dataframe in new order of time, or a fedbecg Data frame
        if connections_df_counter > 0:
            return self.orders_ackording_to_time(hour,minute,connections_df)
        else:
            feedback_df = pd.DataFrame([["Keine Züge gefunden"]], columns=["Info"])
            return feedback_df


# Calling the MainWindow, MenuWindowAbout and MenuWindowReadMe classes
# and display them as windows
if __name__ == "__main__":
    all_data = data()
    all_data.run()

    model = model(all_data)

    app = QtWidgets.QApplication(sys.argv)

    window = mainWindow(model)
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    about_window = menuWindowAbout(model)
    about_window.setWindowTitle("About - Über dieses Programm")
    readme_window = menuWindowReadMe(model)
    readme_window.setWindowTitle("Read Me - Wichtig zu wissen")
    tutorial_window = menuWindowTutorial(model)
    tutorial_window.setWindowTitle("Tutorial")

    sys.exit(app.exec())