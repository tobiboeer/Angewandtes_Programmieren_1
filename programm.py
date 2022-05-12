import csv
from this import s
import numpy as np
import pandas as pd
import os
from os.path import exists
import random
from datetime import datetime
import time
import calendar


import threading
import time



data_names = ['agency','calendar','calendar_dates','feed_info','routes','stop_times','stops','trips']
name_dict = {}

for name in data_names:
    pfad = os.path.abspath(os.path.join(os.path.dirname( __file__ ), name + '.txt'))

    if exists(pfad):

        df = pd.read_csv(pfad)
        pd.set_option('display.min_rows', 10) 
        if name == 'stopshivz':
            #print(df.shape[0]+1)
            pd.set_option('display.min_rows', 400) 
        name_dict[name] = df

        print(name)
        print(df)
        print(" ")
        print(" ")
        print(" ")

    else:
        print("Die Datei " + name + " wurde nicht Gefunden")
        print(os.path.abspath(os.path.join(os.path.dirname( __file__ ), name + '.txt')))

print("---------------------------------------------------------")

if 1 == 0:
    df = pd.DataFrame(name_dict["stops"],columns=['stop_name'])
    df = df.drop_duplicates(subset = ["stop_name"])
    pd.set_option('display.min_rows', 50)
    index = df.index
    df = name_dict["stops"].loc[index]
    train_stachen = df.drop(labels=["stop_id"], axis=1)

    pfad = os.path.dirname(__file__) + '/' + 'train_stachen.csv'
    pd.DataFrame(train_stachen).to_csv(pfad)
    exit()

elif 1 == 0:

    pfad = os.path.dirname(__file__) + '/' + 'train_stachen.csv'
    train_stachen = pd.read_csv(pfad)
    pd.set_option('display.min_rows', 50) 













class myFred(threading.Thread):
    def __init__(self,all_rout_ids,parent,amount_of_trets):
        threading.Thread.__init__(self)
        self.all_rout_ids = all_rout_ids
        self.parent = parent
        self.amount_of_trets = amount_of_trets

    def run(self):
        conectons = []

        for done, rout_id in enumerate(self.all_rout_ids):
            trip_id_example_list = name_dict["trips"].loc[name_dict["trips"]["route_id"] == rout_id]['trip_id'].to_numpy()
            trip_id_example_list = set(trip_id_example_list)
            sub_stop_ids_inspected = []
            for trip_id_example in trip_id_example_list:
                all_stops = name_dict["stop_times"][name_dict["stop_times"].trip_id == trip_id_example]
                sub_stop_ids = list(all_stops["stop_id"].to_numpy())
                if not (sub_stop_ids in sub_stop_ids_inspected):
                    for count, stop_id in enumerate(sub_stop_ids):
                        if count != 0:
                            conectons.append([stop_id,last_stop_id])
                        last_stop_id = stop_id
                    sub_stop_ids_inspected.append(sub_stop_ids)

            if done % 20 == 0:
                print(done,len(self.all_rout_ids))

     
        df = pd.DataFrame (conectons, columns = ['stachen_1','stachen_2'])
        groub = df.groupby(['stachen_1','stachen_2'])
        groub = pd.DataFrame(groub.size())
        groub.reset_index(inplace=True)
        groub = groub.drop(labels=[0], axis=1)

        stachen_1 = list(groub["stachen_1"].to_numpy())
        stachen_2 = list(groub["stachen_2"].to_numpy())
        conectons = [stachen_1,stachen_2]
        
        print("conectons in Tret erstellt")

        while True:
            if self.parent.add_conectons(conectons):
                break
            time.sleep(0.01)


        self.parent.shreads_done += 1
        if self.parent.shreads_done == self.amount_of_trets:
            self.parent.ceap_going()

class Conectons():
    def __init__(self):
        self.shreads_done = 0

        self.add_conectons_actif = 0
        self.conectons = [[],[]]

        all_rout_ids = name_dict["routes"]["route_id"].to_numpy()
        all_rout_ids = all_rout_ids[0:200]

        if len(all_rout_ids) <= 1:
            print("len(all_rout_ids) ",len(all_rout_ids))
            exit()

        amount_of_trets = 64
        while amount_of_trets > len(all_rout_ids):
            amount_of_trets = int(amount_of_trets/2)

        print("amount_of_trets ", amount_of_trets)

        step_sise = int(len(all_rout_ids)/(amount_of_trets-1))
        for i in range(amount_of_trets-1):
            to_check_all_rout_ids = all_rout_ids[0:step_sise]
            all_rout_ids =  all_rout_ids[step_sise:]
            myFred(to_check_all_rout_ids,self,amount_of_trets).start()
        myFred(all_rout_ids,self,amount_of_trets).start()
        print("loob done")

    def add_conectons(self,add):
        if self.add_conectons_actif == 0:
            self.add_conectons_actif = 1

            self.conectons[0] = self.conectons[0] + add[0]
            self.conectons[1] = self.conectons[1] + add[1]

            self.add_conectons_actif = 0
            return True
        else:
            return False

    def ceap_going(self):
        print(len(self.conectons))

        d = {'stachen_1':self.conectons[0],'stop_id':self.conectons[1]}
        df = pd.DataFrame (d)
        #df = pd.DataFrame (self.conectons, columns = ['stachen_1','stop_id'])
        groub = df.groupby(['stachen_1','stop_id'])
        groub = pd.DataFrame(groub.size())
        groub.reset_index(inplace=True)
        groub = groub.drop(labels=[0], axis=1)
        new_df = pd.merge(name_dict["stops"],groub)
        new_df.rename(columns = {'stop_lat':'Station1_lat', 'stop_lon':'Station1_lon'}, inplace = True)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stachen_1':'stop_id'}, inplace = True)
        new_df = pd.merge(name_dict["stops"],new_df)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stop_lat':'Station2_lat', 'stop_lon':'Station2_lon'}, inplace = True)
        print("new_df \n", new_df)

        pfad = os.path.dirname(__file__) + '/' + 'connections.csv'
        new_df.to_csv(pfad)

conect = Conectons()





















if 1 == 2:
    pfad = os.path.dirname(__file__) + '/' + 'file_name.csv'
    df = pd.read_csv(pfad)

    groub = df.groupby(['Stachen1','Stachen2'])
    groub = pd.DataFrame(groub.size())
    groub.reset_index(inplace=True)
    groub = groub.drop(labels=[0], axis=1)
    print(groub)

    index_list = groub.index.values.tolist()
    conectons = []
    for done, i in enumerate(index_list):

        element = groub[groub.index == i]
        Stachen_1_stop_id = int(element['Stachen1'])
        Stachen_2_stop_id = int(element['Stachen2'])

        Stachen_name_1 = name_dict["stops"][name_dict["stops"].stop_id == Stachen_1_stop_id]
        Stachen_name_2 = name_dict["stops"][name_dict["stops"].stop_id == Stachen_2_stop_id]
        
        Stachen_name_1 = pd.DataFrame(Stachen_name_1)['stop_name'].values[0]
        Stachen_name_2 = pd.DataFrame(Stachen_name_2)['stop_name'].values[0]

        element1 = train_stachen[train_stachen.stop_name == Stachen_name_1]
        element2 = train_stachen[train_stachen.stop_name == Stachen_name_2]

        element1 = pd.DataFrame(element1)
        element2 = pd.DataFrame(element2)

        element1_lat = element1['stop_lat'].values[0]
        element1_lon = element1['stop_lon'].values[0]

        element2_lat = element2['stop_lat'].values[0]
        element2_lon = element2['stop_lon'].values[0]

        conectons.append([element1_lat,element1_lon,element2_lat,element2_lon])

        if done == 100000000:
            break

        if (done % 10 == 0):
            print(done,len(index_list))

    conectons = np.array(conectons)
    df = pd.DataFrame(conectons, columns = ['Stachen1_lat','Stachen1_lon','Stachen2_lat','Stachen2_lon'])
    pfad = os.path.dirname(__file__) + '/' + 'conectons.csv'
    df.to_csv(pfad)

if 1 == 2:
    pfad = os.path.dirname(__file__) + '/' + 'conectons.csv'
    conectons = pd.read_csv(pfad)
    conectons = conectons.drop(labels=["Unnamed: 0"], axis=1)
    pd.set_option('display.min_rows', 50) 

if 1 == 2:
    pfad = os.path.dirname(__file__) + '/' + 'Train_staches'
    if not exists(pfad):
        pfad = os.path.dirname(__file__)
        os.chdir(pfad)
        os.mkdir("Train_staches")

    for index, row in train_stachen.iterrows():
        df = pd.DataFrame(row).T
        name = df['stop_name'].values[0]

        name = name.replace("/", "")
        name = name.replace("<", "")
        name = name.replace(">", "")
        name = name.replace("*", "")
        name = name.replace(".", "")
        #while name[0] == "*":
            #name = name[1:]

        pfad = os.path.dirname(__file__) + '/' + 'Train_staches' + '/' + name + ".csv"
        if not exists(pfad):
            #print(df)
            df.to_csv(pfad)

        #if index == 10:
            #break

        if index % 50 == 0:
            print(index)

if 1 == 2:

    print("---------------------------------------------------------")
    print("---------------------------------------------------------")
    print("---------------------------------------------------------")

    conactions_df_counter = 0
    conectons = [[],[]]
    count = 0
    all_rout_ids = name_dict["routes"]["route_id"].to_numpy()
    print(len(all_rout_ids))
    trips_df = name_dict["trips"]

    amount_of_trets = 16
    step_sise = int(len(all_rout_ids)/(amount_of_trets-1))
    for i in range(amount_of_trets):
        to_check_all_rout_ids = all_rout_ids[0:step_sise]
        all_rout_ids =  all_rout_ids[step_sise:]
        myFred(to_check_all_rout_ids).start()
    myFred(all_rout_ids).start()



    for done, rout_id in enumerate(all_rout_ids):
        trip_id_example = name_dict["trips"].loc[name_dict["trips"]["route_id"] == rout_id]['trip_id'].to_numpy()[0]
        all_stops = name_dict["stop_times"][name_dict["stop_times"].trip_id == trip_id_example]
        all_stop_ids = list(all_stops["stop_id"].to_numpy())


        if 1 == 2:
            all_stop_ids_len = len(all_stop_ids)
            lala1 = all_stop_ids[0:all_stop_ids_len-1]
            lala2 = all_stop_ids[1:all_stop_ids_len]

            for i in all_stop_ids_len:

                id_1 = lala1[i]
                id_2 = lala2[i]

                if conactions_df_counter == 0:
                    conactions_df = pd.DataFrame([[id_1, id_2]], columns=["stachen_id_1","stachen_id_2"])
                else:
                    conactions_df.loc[conactions_df_counter] = [id_1, id_2]
                conactions_df_counter += 1



        else:
            for count, stop_id in enumerate(all_stop_ids):
                if count != 0:
                    conectons[0].append(stop_id)
                    conectons[1].append(last_stop_id)
                last_stop_id = stop_id
            
            pass


        if done % 200 == 0:
            print(done,len(all_rout_ids))
    
exit()
























