"""
Calculates the connections between train stations.

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

import pandas as pd
import os
import time
import threading

class myThread(threading.Thread):
    """
    Creating a multithread.
    """
    
    def __init__(self, all_route_ids, parent, amount_of_threads, \
        name_dict_input):
        """
        Initializes a thread, which gets the train station \
            connections based on the route ids.

        Parameters
        ----------

        all_route_ids : List
            containing all route ids

        parent : connections
            class, which distributes tasks to myThread objects

        amount_of_threads : int
            contains the amount of threads

        name_dict_input : dictionary
            containing GTFS data  
        """

        threading.Thread.__init__(self)
        self.name_dict = name_dict_input
        self.all_route_ids = all_route_ids
        self.parent = parent
        self.amount_of_threads = amount_of_threads

    def run(self):
        """
        Based on the 'route id'. The connections between the train \
            stations are put together.
        """
        connections = []

        for route_id in self.all_route_ids:
        
            # Gets all the trip id's from the 'route id'.
            trip_id_example_list = self.name_dict["trips"].loc[self. \
                name_dict["trips"]["route_id"] == route_id]['trip_id'] \
                    .to_numpy()
            
            # Reducing the number of trip id's to reduce the runtime.
            trip_id_example_list = set(trip_id_example_list)
            sub_stop_ids_inspected = []
            
            for trip_id_example in trip_id_example_list:
            
                # Gets all the stop names from the trip id.
                all_stops = self.name_dict["stop_times"][self.name_dict \
                    ["stop_times"].trip_id == trip_id_example]
                sub_stop_ids = list(all_stops["stop_id"].to_numpy())
                
                # Creates a list of all train station connections.
                if not (sub_stop_ids in sub_stop_ids_inspected):
                    for count, stop_id in enumerate(sub_stop_ids):
                        if count != 0:
                            connections.append([stop_id,last_stop_id])
                        last_stop_id = stop_id
                    sub_stop_ids_inspected.append(sub_stop_ids)

        # Reduces the couples of recurrent station names in the list.
        df = pd.DataFrame (connections, columns = \
            ['station_1', 'station_2'])
        group = df.groupby(['station_1', 'station_2'])
        group = pd.DataFrame(group.size())
        group.reset_index(inplace = True)
        group = group.drop(labels = [0], axis=1)

        # Reassembles the list.
        station_1 = list(group["station_1"].to_numpy())
        station_2 = list(group["station_2"].to_numpy())
        connections = [station_1, station_2]

        # Writes to the main class
        while True:
            if self.parent.add_connections(connections):
                break
            time.sleep(0.01)
        
        # If all threads are done the main code can be run.
        self.parent.threads_done += 1
        if self.parent.threads_done == self.amount_of_threads:
            print("Thread " + self.parent.threads_done + " finished.")
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

        Parameters
        ----------
        data_class : data
            containing all data

        data_type : String
            name of type
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

        # Starts with 64 threads for big data sets, 
        # if needed the amount is reduced.
        amount_of_threads = 64
        
        while amount_of_threads > len(all_route_ids):
            amount_of_threads = int(amount_of_threads/2)

        # The threads are set and started.
        step_size = int(len(all_route_ids)/(amount_of_threads-1))
        
        for i in range(amount_of_threads-1):
            to_check_all_route_ids = all_route_ids[0:step_size]
            all_route_ids =  all_route_ids[step_size:]
            myThread(to_check_all_route_ids, self, amount_of_threads, \
                self.name_dict).start()
        myThread(all_route_ids, self, amount_of_threads, self.name_dict) \
            .start()

    def add_connections(self, add):
        """
        To avoid conflicts only one thread is allowed to write at a time.

        Parameters
        ----------
        add : List
            couples of train stations
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
        Based on the collected train station couples a new 
        dataframe of longitude
        and latitude values is created and printed to a csv file.
        """
        # Reduces the couples of recurrent station names in the list.
        d = {'station_1':self.connections[0], \
            'stop_id':self.connections[1]}
        df = pd.DataFrame (d)
        group = df.groupby(['station_1', 'stop_id'])
        group = pd.DataFrame(group.size())
        group.reset_index(inplace = True)
        group = group.drop(labels= [0], axis = 1)

        # Replaces the stop id's with the longitude and latitude values.
        new_df = pd.merge(self.name_dict["stops"],group)
        new_df.rename(columns = {'stop_lat':'Station1_lat', \
            'stop_lon':'Station1_lon'}, inplace = True)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'station_1': 'stop_id'}, inplace = True)
        new_df = pd.merge(self.name_dict["stops"],new_df)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stop_lat':'Station2_lat', \
            'stop_lon':'Station2_lon'}, inplace = True)

        # Writes the data.
        path = os.path.abspath(os.path.join(os.path. \
            dirname( __file__ ), "Data/" + self.name))
        new_df.to_csv(path)

        # Depending of the type, one file is restored.
        if self.data_type == "long_distance":
            self.data_class.free_fern_add_1()
        
        if self.data_type == "short_distance":
            self.data_class.free_nah_add_1()
        
        if self.data_type == "regional":
            self.data_class.free_regional_add_1()