import pandas as pd
import geojson
import os
import time
import calendar
import threading
import concurrent.futures
import markdown

from os.path import exists

from DB_connections import connections as connections

class data(threading.Thread):
    """
    Works with the data
    """

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        """
        Loads all necessary data and starts the threads 
        with loading other data.
        """
        self.delighted_category_options = []
        self.model_set = False
        self.queue_text = " "

        # Loads necessary and little data for the first overview.
        self.counts = self.load_map_data()
        self.about_text = self.load_about_text()
        self.readme_text = self.load_readme_text()

        self.tutorial_text = self.load_tutorial()
        self.stops_fern = self.load_text('stops_fern.txt')
        self.connections_fern = self.load_text('connections_fern.csv')
        self.gtfs_fern = self.load_gtfs("latest_fern")

        # Checks if the first files are ok, 
        # or if different files needed to be chosen.
        self.load_first = True
        if (self.stops_fern[1] == False) or (self.connections_fern[1] \
            == False) or (self.gtfs_fern == None):
            self.load_first = False

        # Presents the gtfs variables, therefore they can be checked, 
        # if they already have been loaded.
        self.gtfs_nah = None
        self.gtfs_regional = None
        
        # Values determing, if the variable is set. 
        self.connections_nah_set = False
        self.connections_regional_set = False
        self.stops_regional_set = False
        self.stops_nah_set = False

        # The loading of the rest of the data is stated.
        threading.Thread(target = self.gtfs_prep).start()
        
        # The time delay is needed, though every running process is 
        # started. This is necessary because the class 'model' might 
        # access them.
        time.sleep(0.1)

    def set_model(self, model):
        """
        Saves the model.

        Parameters
        ----------
        model : model
            interactions class
        """
        self.model = model
        self.model_set = True

    def text_field_update(self, new_text):
        """
        Updates the text field or saves it in the queue.

        Parameters
        ----------
        new_text : String
            new text for the text field 
        """
        if self.model_set == True:
            if self.queue_text != " ":
                self.model.text_field_update(self.queue_text)
                self.queue_text = " "
            self.model.text_field_update(new_text)
        else:
            self.queue_text = self.queue_text + "\n" + new_text

    def restore(self, key):
        """
        Based on the key, if files are missing they are recreated 
        and can be used after that

        Parameters
        ----------
        key : String
            containing type of train traffic.
        """

        # If the key fits and there is data to be restored.
        if key == "fern" and ("stops_fern" \
            in self.delighted_category_options):
        
            # Needed for restoring 
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

        if key == "nah" and ("stops_nah" \
            in self.delighted_category_options):
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

        if key == "regional" and ("stops_regional" \
            in self.delighted_category_options):
        
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
        """
        Restores the missing train station data.

        Parameters
        ----------
        datatype : String
            containing the type of train traffic
        """
        if data_type == "fern":
            self.restore_train_station_by_name \
                (self.gtfs_fern, 'stops_fern.txt')
            self.free_fern_add_1()
            
        if data_type == "nah":
            self.restore_train_station_by_name \
                (self.gtfs_nah, 'stops_nah.txt')
            self.free_nah_add_1()
            
        if data_type == "regional":
            self.restore_train_station_by_name \
                (self.gtfs_regional, 'stops_regional.txt')
            self.free_regional_add_1()

    def restore_train_station_by_name(self, dataframe_gtfs, name):
        """
        Based of the given data and name, a new data set of 
        the train stations is created and saved

        Parameters
        ----------
        dataframe_gtfs : dataframe
            contains the GTFS data

        name : String
            containing the file name
        """

        # Gets all train station names and drops multiple ones
        df = pd.DataFrame(dataframe_gtfs["stops"], columns =['stop_name'])
        df = df.drop_duplicates(subset = ["stop_name"])

        # Based on the index the information of 
        # the train station is collected
        index = df.index
        df = dataframe_gtfs["stops"].loc[index]

        # The unnecessary column is dropped
        train_station = df.drop(labels=["stop_id"], axis=1)

        # Writing the new data set
        path = os.path.abspath( \
            os.path.join(os.path.dirname( __file__ ), "Data/" + name))
        pd.DataFrame(train_station).to_csv(path)

    def free_regional_add_1(self):
        """
        Increases the number of restored files by 1.
        If all files are restored, 
        the data is written and the option is reinstated
        """
    
        self.free_regional += 1
        
        # The dataset is fully restored and can be loaded 
        # and the category is available again.
        if self.free_regional == 2:
            self.stops_regional = self.load_text('stops_regional.txt')
            self.connections_regional = self.load_text \
                ('connections_regional.csv')
            self.delighted_category_options.remove("stops_regional")

    def free_fern_add_1(self):
        """
        Compare to free_regional_add_1
        """
        self.free_fern += 1
        
        if self.free_fern == 2:
            self.stops_fern = self.load_text('stops_fern.txt')
            self.connections_fern = self.load_text('connections_fern.csv')
            self.delighted_category_options.remove("stops_fern")

    def free_nah_add_1(self):
        """
        Compare to free_regional_add_1
        """
        self.free_nah += 1
        
        if self.free_nah == 2:
            self.stops_fern = self.load_text('stops_nah.txt')
            self.connections_fern = self.load_text('connections_nah.csv')
            self.delighted_category_options.remove("stops_nah")

    def gtfs_prep(self):
        """
        Every file gets its own loading thread, 
        which is safed in the variable.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.gtfs_nah_pre = executor.submit \
                (self.load_gtfs, "latest_nah")
            self.gtfs_regional_pre = executor.submit \
                (self.load_gtfs, "latest_regional")
            self.connections_nah_pre = executor.submit \
                (self.load_text, "connections_og.csv")
            self.connections_regional_pre = executor.submit \
                (self.load_text, "connections_regional.csv")
            self.stops_regional_pre = executor.submit \
                (self.load_text, "stops_regional.txt")
            self.stops_nah_pre = executor.submit \
                (self.load_text, "stops_nah.txt")

    def get_stops_fern(self):
        """
        If the value is incorrect, 
        the category option is closed and a restoration is tried

        Return
        ------
        stops_fern : dataframe
            containing the train station information
        """
        if self.stops_fern[1] == False:
            if not ("stops_fern" in self.delighted_category_options):
                self.delighted_category_options.append("stops_fern")
            self.restore("fern")

        return self.stops_fern

    def get_stops_nah(self):
        """
        If the value is not pulled, its done now. 
        If the value is incorrect, the category option is closed
        and a restoration is tried.

        Return
        ------
        stops_nah : dataframe
            containing the train station information
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
        """
        If the value is not pulled, its done now. 
        If the value is incorrect, the category option is closed 
        and a restoration is tried.

        Return
        ------
        stops_regional : dataframe
            containing the train station information
        """
        if not self.stops_regional_set:
            self.stops_regional_set = True
            self.stops_regional = self.stops_regional_pre.result()
            
            if self.stops_regional[1] == False:
            
                if not ("stops_regional" in \
                    self.delighted_category_options):
                    self.delighted_category_options.append \
                        ("stops_regional")
                self.restore("regional")

        return self.stops_regional

    def get_connections_regional(self):
        """
        If the value is not pulled, its done now. If the 
        value is incorrect, the category option is closed
        and a restoration is tried.

        Return
        ------
        connections_regional : dataframe
            containing the connections between two train station
        """
        if not self.connections_regional_set:
            self.connections_regional_set = True
            self.connections_regional = self.connections_regional_pre \
                .result()
            
            if self.connections_regional[1] == False:
            
                if not ("stops_regional" in \
                    self.delighted_category_options):
                    self.delighted_category_options.append \
                        ("stops_regional")
                self.restore("regional")

        return self.connections_regional

    def get_connections_nah(self):
        """
        If the value is not pulled, its done now. If the 
        value is incorrect, the category option is closed
        and a restoration is tried.

        Return
        ------
        connections_nah : dataframe
            containing the connections between two train stations
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
        """
        If the value is incorrect, the category option is closed 
        and a restoration is tried

        Return
        ------
        connections_fern : dataframe
            containing the connections between two train stations
        """
        if self.connections_fern[1] == False:
        
            if not ("stops_fern" in self.delighted_category_options):
                    self.delighted_category_options.append("stops_fern")
                    
            self.restore("fern")
            
        return self.connections_fern

    def gtfs(self, category):
        """
        The GTFS are pulled if needed. If gtfs data is missing, 
        the option to use the given category is closed.

        Parameters
        ----------
        category : String
            Containing the type of train traffic

        Returns
        -------
        gtfs_nah : dataframe
            containing GTFS data of short distance traffic
        gtfs_fern : dataframe
            containing GTFS data of long distance traffic
        gtfs_regional : dataframe
            containing GTFS data of regional traffic
        """ 
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
                    self.delighted_category_options.append \
                    ("stops_regional")
                    
            return self.gtfs_regional

    def load_gtfs(self, category):
        """
        Loads GTFS data.

        Parameters
        ----------
        category : String
            Containing the type of train traffic

        Returns
        -------
        loaded_data : dictionary
            containing the loaded data
        """

        # Creates path
        path_start = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), category))+ '\\'
        data_names = ['agency','calendar','calendar_dates','feed_info' \
            ,'routes','stop_times','stops','trips']
        loaded_data = {}

        gtfs_is_missing_files = False

        # Reads in all the data.
        for name in data_names:
            path = path_start + name + '.txt'
            
            if exists(path):
                df = pd.read_csv(path)
                loaded_data[name] = df

            else:
                # If data is not found the user is informed.
                print("Die Datei " + name + " wurde nicht Gefunden")
                print(os.path.abspath(os.path.join(os.path.dirname \
                    ( __file__ ), name + '.txt')))
                gtfs_is_missing_files = True

        # If the data is not found, the user is informed.
        if gtfs_is_missing_files:
            text = "Da die Daten der Kategorie " + category + \
                " nicht geladen werden konnten, \n" + \
                "kann diese nicht verwendet werden."
            print(text)
            self.text_field_update(text)
            
            return None

        return loaded_data

    def load_map_data(self):
        """
        Loads the data of the map of Germany.
        Source of the file:
        http://opendatalab.de/projects/geojson-utilities/

        Return
        ------
        data['features'] : dataframe
            containing the counties of Germany
        """
        path_to_map = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data" + \
            '/landkreise_simplify200.geojson'))
        
        if exists(path_to_map):
        
            with open(path_to_map,encoding='utf8') as f:
                data = geojson.load(f)
                f.close()
            
            return data['features']
            
        else:
            text = "Die Datei landkreise_simplify200.geojson fehlt."
            text = text + "\n" + "Sie ist essentiell, deswegen wird" + \
                " das Programm abgebrochen."
            text = text + "\n" + "Datei unter: " + \
                "http://opendatalab.de/projects/geojson-utilities/"
            self.text_field_update(text)
            print(text)
            exit()

    def load_about_text(self):
        """
        Loads the 'About' file and returns it.

        Return
        ------
        about_text : str
            containing the ABOUT text.
        """
        
        path_to_about = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data" + '/ABOUT.md'))
        
        if exists(path_to_about):
        
            with open(path_to_about, encoding='utf8') as about_file:
                about_text = about_file.read()
                about_file.close()
                
            return about_text
        else:
            return "No ABOUT text was found"

    def load_readme_text(self):
        """
        Loads the 'ReadMe' file and returns it.

        Return
        ------
        readme_text_md : str
            containing the README text.
        """
        
        path_str = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data")) + "\\" 
        path_to_readme = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data" + '/README.md'))
        
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
        Loads the 'Tutorial' file and returns it.

        Return
        ------
        tutorial_text_md : str
            containing the TUTORIAL text.
        """
        
        path_str = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data")) + "\\" 
        path_to_tutorial = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data" + '/TUTORIAL.md'))
        
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
        Loads a given file and returns it.

        Return
        ------
        List : List
            contains the routes if accessed and a confirmation of success.
        """
        path = os.path.abspath(os.path.join \
            (os.path.dirname( __file__ ), "Data" + '/' + filename_routes))
        
        if exists(path):
            routes = pd.read_csv(path, encoding='utf8')
            
            # An indication, if the reading 
            # was successfull, it is included.
            return [routes, True]
        return [None, False]

    def orders_according_to_time(self, hour, minute, connections_df):
        """
        Changes the dataframe order based on the time in connections_df.

        Parameters
        ----------

        hour : int
            contains the hour of time

        minute : int
            contains the minute of time

        connections_df : dataframe
            contains the train station information

        Return
        ------
        Dataframe : dataframe
            contains the train station information
        """

        connections_df = connections_df.sort_values(by=['Einfahrtszeit'])
        actual_time = str(hour) + ":" + str(minute) + ":00"

        connections_df_firs = connections_df.loc \
            [connections_df["Einfahrtszeit"] >= actual_time]
        connections_df_sec = connections_df.loc \
            [connections_df["Einfahrtszeit"] < actual_time]

        return pd.concat([connections_df_firs, connections_df_sec])

    def getting_service_days(self, gtfs, trip_id_instance):
        """
        Getting the service id from given trip id

        Parameters
        ----------

        gtfs : dictionary
            containing data in dataframes

        trip_id_instance : int
            contains the id of the trip

        Return
        ------
        service_days : dictionary
            contains the service days
        trips_trip_id : dictionary
            contains trips
        """
    
        trips_trip_id = gtfs["trips"].loc \
            [gtfs["trips"]["trip_id"] == trip_id_instance]
        service_id_instance = trips_trip_id['service_id'].to_numpy()[0]
        service_days = gtfs["calendar"].loc \
            [gtfs["calendar"]["service_id"] == service_id_instance]
        return service_days, trips_trip_id

    def create_train_station_info(self, date, train_station_name, \
            time_span, gtfs):
        """
        Creates a dataframe with train information of the next trains 
        departuring in given train station.

        Parameters
        ----------
        date : int
            contains the weekday

        train_station_name : String
            containing the name of the train station

        time_span : int
            containing the time span in hours 

        gtfs : dictionary
            containing data in dataframes

        Return
        ------
        dataframe : dataframe
            Can be the departuring trains or error messages.
        """

        if not (train_station_name in gtfs["stops"]["stop_name"] \
            .to_numpy()):
            return pd.DataFrame([["Bahnhof nicht bekannt"]] , \
                columns=["Info"])

        # If there is no time given, there cant be any trains
        if time_span <= 0:
            return pd.DataFrame([["Keine Züge gefunden"]], \
                columns=["Info"])

        day_given = date[0]
        hour = date[1]
        minute = date[2]

        # Get trip_id_IDs stopping at the train station
        stop_IDs = gtfs["stops"].loc[gtfs["stops"]["stop_name"] \
            == train_station_name]['stop_id'].to_numpy()        
        trip_id_IDs = set(gtfs["stop_times"].loc \
            [gtfs["stop_times"]["stop_id"].isin \
                (stop_IDs)]['trip_id'].to_numpy())

        # Counter containing how many lines are added to the Dataframe
        connections_df_counter = int(0)
        
        for trip_id_instance in trip_id_IDs:

            # Geting the service id from given trip id
            service_days , trips_trip_id \
            = self.getting_service_days(gtfs,trip_id_instance)

            if not service_days.empty:
                
                # Get the trip ids and their stop and the given 
                # train station from the route
                stop_times_trip_id_instance = gtfs["stop_times"].loc \
                    [gtfs["stop_times"]["trip_id"] == trip_id_instance]


                trip_id_stops = stop_times_trip_id_instance.loc \
                    [stop_times_trip_id_instance["stop_id"].isin \
                        (stop_IDs)]

                # Determines the arrival time and how many days 
                # in the future this is
                arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
                arrival_time_hour = int(arrival_time[0:2])
                days_over = int(arrival_time_hour / 24)

                day = day_given
                time_difference = 0
                
                # If the train stop is in the future, 
                # based on the service day
                # the previous service day needs to be checked
                if days_over > 0:

                    # Arrival time on this day
                    arrival_time_hour_str = str(arrival_time_hour - \
                        (24 * days_over))
                    
                    # Adjusts the str to two letters
                    if len(arrival_time_hour_str) == 1:
                        arrival_time_hour_str = "0" + \
                            arrival_time_hour_str

                    # Rearrange the arrival_time string to the given day
                    arrival_time = arrival_time_hour_str + \
                        arrival_time[2:]

                    # Calculates the service day, that needs to be checked
                    day = day_given - days_over
                    if (int(arrival_time[0:2]) < hour) or \
                        (int(arrival_time[0:2]) < hour) and \
                        (int(arrival_time[3:5]) < minute):
                        day = day + 1
                        time_difference = 24 * 60
                        
                    # Adjusts the day based on a scale 0-6
                    if day < 0:
                        day = day + 7

                    # Calculates the time_difference between arrival time
                    # and given time 
                    time_difference = time_difference + \
                        (int(arrival_time[0:2]) - hour) * 60 + \
                            (int(arrival_time[3:5]) - minute)
                    
                else:
                    # Calculates the time_difference between arrival time 
                    # and given time
                    time_difference = (int(arrival_time[0:2])- hour) \
                        * 60 + (int(arrival_time[3:5])- minute)

                day_is_served = service_days[calendar.day_name[day] \
                    .lower()].to_numpy()[0]
                
                # Only if the route is served and the arival time 
                # is in the future
                if (day_is_served == 1) and (time_difference > 0 and \
                    time_difference < time_span * 60):

                    # Gets the highest stop_sequence, 
                    # which is an end station
                    last_station = max(stop_times_trip_id_instance \
                        ['stop_sequence'].to_numpy())
                    direction = trips_trip_id['direction_id'].to_numpy()[0]
                    
                    # Depending on the direction the end station is chosen
                    if direction == 0:
                        end_station = last_station
                    else:
                        end_station = 0

                    # Gets the name of the destination train station
                    end_station_stop_id = stop_times_trip_id_instance \
                        .loc[stop_times_trip_id_instance \
                            ["stop_sequence"] == end_station] \
                                ['stop_id'].to_numpy()[0]
                    end_station_name = gtfs["stops"].loc[gtfs["stops"] \
                        ["stop_id"] == end_station_stop_id]['stop_name'] \
                            .to_numpy()[0]

                    # Gets the row routes of the route id
                    route_id_instance = trips_trip_id['route_id'] \
                        .to_numpy()[0]
                    routes_row = gtfs["routes"].loc[gtfs["routes"] \
                        ["route_id"] == route_id_instance]

                    # Retrieves the information of the trip 
                    agency_id_instance = routes_row['agency_id'] \
                        .to_numpy()[0]
                    agency_name_instance = gtfs["agency"] \
                        .loc[gtfs["agency"]["agency_id"] == \
                            agency_id_instance]['agency_name'] \
                                .to_numpy()[0]
                    route_long_name = routes_row['route_long_name'] \
                        .to_numpy()[0]
                    departure_time = trip_id_stops['departure_time'] \
                        .to_numpy()[0]

                    # The trip is added to the dataframe
                    if connections_df_counter == 0:
                        connections_df = pd.DataFrame([ \
                            [agency_name_instance, route_long_name, \
                            end_station_name, arrival_time, \
                            departure_time]], columns=["Betreiber", \
                            "Zugbezeichnung","Endstation", \
                                "Einfahrtszeit","Abfahrtszeit"])
                    else:
                        connections_df.loc[connections_df_counter] = \
                            [agency_name_instance, route_long_name, \
                                end_station_name, arrival_time, \
                                    departure_time]
                    connections_df_counter += 1

        # Returns dataframe in new order of the time, 
        # or a feedback dataframe
        if connections_df_counter > 0:
            return self.orders_according_to_time \
                (hour,minute,connections_df)
        else:
            feedback_df = pd.DataFrame([["Keine Züge gefunden"]], \
                columns=["Info"])
            return feedback_df
