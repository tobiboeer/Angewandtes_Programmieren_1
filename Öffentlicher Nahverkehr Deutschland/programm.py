import csv
from tkinter import N
import numpy as np
import pandas as pd
import os
from os.path import exists
import random


data_names = ['agency','calendar','calendar_dates','feed_info','routes','stop_times','stops','trips']
name_dict = {}

for name in data_names:
    pfad = os.path.dirname(__file__) + '/' + name + '.txt'
    if exists(pfad):

        df = pd.read_csv(pfad)
        pd.set_option('display.min_rows', 10) 
        if name == 'calendar':
            #print(df.shape[0]+1)
            pd.set_option('display.min_rows', 100) 
        name_dict[name] = df

        print(name)
        print(df)
        print(" ")
        print(" ")
        print(" ")

    else:
        print("Die Datei " + name + " wurde nicht Gefunden")

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

pfad = os.path.dirname(__file__) + '/' + 'train_stachen.csv'
train_stachen = pd.read_csv(pfad)
pd.set_option('display.min_rows', 50) 
#print(train_stachen)


#print(len(name_dict["trips"]["trip_id"].unique()))
#print(len(name_dict["trips"]["route_id"].unique()))


#name_dict["stop_times"]

#df_triger = name_dict["stop_times"][name_dict["stop_times"].trip_id == 1]
#print(df_triger)

if 1 == 2:
    conectons = [[],[]]
    count = 0
    all_rout_ids = name_dict["trips"]["route_id"].unique()
    for done, rout_id in enumerate(all_rout_ids):
        df_triger = name_dict["stop_times"][name_dict["stop_times"].trip_id == rout_id]
        
        #print(len(df_triger))

        stop_sequence_numbers = df_triger["stop_sequence"].unique()
        for stop_sequence_number in stop_sequence_numbers:
            if stop_sequence_number == 0:
                previes_stop = df = df_triger[df_triger.stop_sequence == stop_sequence_number]
            else:
                curent_stop = df = df_triger[df_triger.stop_sequence == stop_sequence_number]
                #print(int(previes_stop["stop_id"]),int(curent_stop["stop_id"]))
                
                #conectons = conectons.append({'Stachen1' : previes_stop["stop_id"],'Stachen1' : curent_stop["stop_id"]} , ignore_index=True)
                conectons[0].append(previes_stop["stop_id"])
                conectons[1].append(curent_stop["stop_id"])

                previes_stop = curent_stop

                count += 1

        print(done,len(all_rout_ids))

        #break


    df = pd.DataFrame(np.array(conectons).T[0], columns = ['Stachen1','Stachen2'])
    pfad = os.path.dirname(__file__) + '/' + 'file_name.csv'
    df.to_csv(pfad)
    exit()


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
        element2 = train_stachen[train_stachen.stop_name == Stachen_name_1]

        element1 = pd.DataFrame(element1)
        element2 = pd.DataFrame(element2)

        element1_lat = element1['stop_lat'].values[0]
        element1_lon = element1['stop_lon'].values[0]

        element2_lat = element2['stop_lat'].values[0]
        element2_lon = element2['stop_lon'].values[0]

        conectons.append([element1_lat,element1_lon,element2_lat,element2_lon])

        if (done % 10 == 0):
            print(done,len(index_list))

    conectons = np.array(conectons)
    df = pd.DataFrame(conectons, columns = ['Stachen1_lat','Stachen1_lon','Stachen2_lat','Stachen2_lon'])
    pfad = os.path.dirname(__file__) + '/' + 'conectons.csv'
    df.to_csv(pfad)


if 1 == 1:
    pfad = os.path.dirname(__file__) + '/' + 'conectons.csv'
    conectons = pd.read_csv(pfad)
    conectons = conectons.drop(labels=["Unnamed: 0"], axis=1)
    pd.set_option('display.min_rows', 50) 


if 1 == 1:
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
            df.to_csv(pfad)

        #if index == 10:
            #break

        if index % 50 == 0:
            print(index)

print("done - ----------------------------------------------------")

































