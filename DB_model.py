"""
Intermediates between the data and the GUI.

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

class model():
    """
    Connects the GUI with the database. 
    """

    def __init__(self, all_data):
        """
        Sets the basic values.

        Parameters
        ----------
        all_data : data
            contains all loaded data (every data of all files)
        """
        self.all_data = all_data
        self.all_data.set_model(self)
        self.train_station_info = None
        self.get_first_data()

    def get_first_data(self):
        """
        Depending on the data set. If the data is correct, 
        it will be loaded.
        """

        if self.all_data.load_first:
           
            # Checks for correctness and loads the set.
            self.current_stops = self.all_data.get_stops_fern()
            self.current_connections = self.all_data \
                .get_connections_fern()
            self.current_gtfs = self.all_data.gtfs("latest_fern")
        else:
            # The incorrect data set is blocked.
            self.all_data.delighted_category_options_append("stops_fern")
            
            # Tries to restore the lost data.
            if not (self.all_data.gtfs("latest_fern") == None):
                self.all_data.restore("fern")

            # Loads the new data.
            self.current_stops = self.all_data.get_stops_regional()
            self.current_connections = self.all_data \
                .get_connections_regional()
            self.current_gtfs = self.all_data.gtfs("latest_regional")
            
            # Checks the new data.
            if (self.current_stops[1] == False) or (self \
                .current_connections[1] == False) or (self.current_gtfs \
                    == None):
                self.all_data.delighted_category_options_append \
                    ("stops_regional")
                if not (self.all_data.gtfs("latest_regional") == None):
                    self.all_data.restore("regional")
                self.current_stops = self.all_data.get_stops_nah()
                self.current_connections = self.all_data \
                    .get_connections_nah()
                self.current_gtfs = self.all_data.gtfs("latest_nah")
                if (self.current_stops[1] == False) or \
                    (self.current_connections[1] == False) or \
                        (self.current_gtfs == None):
                    self.all_data.delighted_category_options_append \
                        ("stops_nah")
                    if not (self.all_data.gtfs("latest_nah") == None):
                        self.all_data.restore("nah")
                    print("Es sind unvollständige Datensets " + \
                        "vorhanden. Daraus folgt eine Einschränkung " + \
                            "der Bedienbarkeit.")
        
    def set_main_gui(self, main_gui):
        """
        Set main GUI and updates the text field.

        Parameters
        ----------
        main_gui : mainWindow
            contains the main frame of the GUI
        """
        self.main_gui = main_gui
        self.all_data.text_field_update(" ")

    def get_current_stops(self):
        return self.current_stops[0]

    def get_connections(self):
        return self.current_connections[0]

    def change_current_stops(self, new_type):
        """
        If the category is available, it can be chosen.

        Parameters
        ----------
        new_type : String
            contains the type of train traffic
        """

        if not (new_type in self.all_data.delighted_category_options):
        
            # Saves the current status as a backup
            start_values = [self.current_stops,self \
                .current_connections,self.current_gtfs]

            # Loads the data, based on the type
            if new_type == "stops_fern":
                self.current_stops = self.all_data.get_stops_fern()
                self.current_connections = self.all_data \
                    .get_connections_fern()
                self.current_gtfs = self.all_data.gtfs("latest_fern")
                
            if new_type == "stops_nah":
                self.current_stops = self.all_data.get_stops_nah()
                self.current_connections = self.all_data \
                    .get_connections_nah()
                self.current_gtfs = self.all_data.gtfs("latest_nah")
                
            if new_type == "stops_regional":
                self.current_stops = self.all_data.get_stops_regional()
                self.current_connections = self.all_data \
                    .get_connections_regional()
                self.current_gtfs = self.all_data.gtfs("latest_regional")

            # If the data is incorrect
            if (self.current_gtfs == None) or (self.current_stops[1]== \
                False) or (self.current_connections[1]==False):
                
                # The backup is used to restore the first values
                self.current_stops = start_values[0]
                self.current_connections = start_values[1]
                self.current_gtfs = start_values[2]
                
                # It tries to restore data from every category, 
                # might not be necessary most times.
                self.all_data.restore("fern")
                self.all_data.restore("nah")
                self.all_data.restore("regional")

            else:
                # Triggers a GUI update of the route network to 
                # the current type of train traffic
                self.main_gui.draw_route_network(self \
                    .get_current_stops(),self.get_connections()) 
        else :
            self.main_gui.draw_route_network(self \
                    .get_current_stops(),self.get_connections())
        
    def get_about_text(self):
        return self.all_data.about_text

    def get_readme_text(self):
        return self.all_data.readme_text

    def get_tutorial(self):
        return self.all_data.tutorial_text

    def get_counts(self):
        return self.all_data.counts

    def change_train_station_info(self, time_span, day, hour, \
         minute, train_station):
        """
        Calculates new train station data and fills it in.

        Parameters
        ----------
        time_span : int
            time span of the train departuring 

        day : int
            selected day

        hour : int
            selected hour

        minute : int
            selected minute

        train_station: String
            selected train station
        """
        self.train_station_info = self.all_data. \
            create_train_station_info([day, hour, minute], \
                train_station, time_span, self.current_gtfs)
        self.main_gui.dataTable_instance.set_dataframe \
            (self.train_station_info)
        
    def text_field_update(self,new_info):
        """
        Updates the text field.

        Parameters
        ----------
        new_info : String
            new information for the text field 
        """
        self.main_gui.side_window_instance.update_text(new_info)



