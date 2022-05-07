import csv
from tkinter import N
import numpy as np
import pandas as pd
import os
from os.path import exists
import random
from datetime import datetime
import calendar



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

print("done - ----------------------------------------------------")





# Bahnhofs Nahme -->  stop IDs
stop_IDs = name_dict["stops"].loc[name_dict["stops"]["stop_name"] == "- Obermeiderich Bf"]['stop_id'].to_numpy()
print(stop_IDs)
# IDs -->  trip_id (nechste 3 stunden)
trip_id_IDs = set(name_dict["stop_times"].loc[name_dict["stop_times"]["stop_id"].isin(stop_IDs)]['trip_id'].to_numpy())
print(trip_id_IDs)
# trip_id --> stop_sequence (min/max)

conactions_df = 0
for trip_id_instanz in trip_id_IDs:
    print("Bahnhof infos - ----------------------------------------------------")

    trip_stachens = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]['stop_sequence'].to_numpy()
    last_stachen = max(trip_stachens)
    print("last_stachen \n",last_stachen)
    trips_trip_id = name_dict["trips"].loc[name_dict["trips"]["trip_id"] == trip_id_instanz]
    print("trips_trip_id \n",trips_trip_id)
    direction = trips_trip_id['direction_id'].to_numpy()[0]
    
    print("direction \n",direction)
    if direction == 0:
        end_station = last_stachen
    else:
        end_station = 0

    stop_times_all = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]
    end_station_stop_id = stop_times_all.loc[stop_times_all["stop_sequence"] == end_station]['stop_id'].to_numpy()[0]
    print("end_station_stop_id \n",end_station_stop_id)

    end_station_name = name_dict["stops"].loc[name_dict["stops"]["stop_id"] == end_station_stop_id]['stop_name'].to_numpy()[0]
    print("end_station_name \n",end_station_name)

    route_id_instanz = trips_trip_id['route_id'].to_numpy()[0]
    service_id_instanz = trips_trip_id['service_id'].to_numpy()[0]

    serves_days = name_dict["calendar"].loc[name_dict["calendar"]["service_id"] == service_id_instanz]
    if not serves_days.empty:
        print("serves_days \n",serves_days)
        day = calendar.day_name[datetime.today().weekday()].lower()
        day_is_serfed = serves_days[day].to_numpy()[0]
        print("day_is_serfed \n",day_is_serfed)

        hauer = int(datetime.now().strftime("%H"))
        print("now \n",hauer)

        if hauer < 3:
            yesterday_datetime = datetime.today() - datetime.timedelta(days=1)
            yesterday = calendar.day_name[yesterday_datetime.weekday()].lower()
            yesterday_is_serfed = serves_days[yesterday].to_numpy()[0]
            print("yesterday_is_serfed \n",yesterday_is_serfed)

            if yesterday_is_serfed == 1:

                routes_row = name_dict["routes"].loc[name_dict["routes"]["route_id"] == route_id_instanz]
                print("routes_row \n",routes_row)

                print("trip_id_instanz \n",trip_id_instanz)

                stop_times_trip_id_instanz = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]
                print("stop_times_trip_id_instanz \n",stop_times_trip_id_instanz)

                trip_id_stops = stop_times_trip_id_instanz.loc[stop_times_trip_id_instanz["stop_id"].isin(stop_IDs)]
                print("trip_id_stops \n",trip_id_stops)

                agency_id_instanz = routes_row['agency_id'].to_numpy()[0]
                agency_name_instanz = name_dict["agency"].loc[name_dict["agency"]["agency_id"] == agency_id_instanz]['agency_name'].to_numpy()[0]


                #Nordwest bahn
                agency_name_instanz
                #RE15
                route_long_name = routes_row['route_long_name'].to_numpy()[0]
                #Münster
                end_station_name
                #9:07
                arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
                #9:09
                departure_time = trip_id_stops['departure_time'].to_numpy()[0]

                print(" ")
                print(" ")
                print(agency_name_instanz)
                print("AAAAAAAAAAAA ")
                print(route_long_name)
                print("BBBBBBBBBBBBBBBBBBBBBB ")
                print(end_station_name)
                print("CCCCCCCCCCCCCCCCCCCCCCCCCC ")
                print(arrival_time)
                print("DDDDDDDDDDDDDDDDDDDDDDDD ")
                print(departure_time)

                if int(arrival_time[0:2]) >= 24:
                    real_houer = str(int(arrival_time[0:2]) - 24)
                    arrival_time[0:2] = real_houer[0:2]

                    print((int(arrival_time[0:2])-hauer)*60)
                    min = int(datetime.now().strftime("%M"))
                    print(min)
                    print((arrival_time[3:5]))
                    print((int(arrival_time[3:5])-min))

                    min = int(datetime.now().strftime("%M"))
                    time_diferenc = (int(arrival_time[0:2])-hauer)*60 + (int(arrival_time[3:5])-min)
                    print("time_diferenc \n",time_diferenc)

                    if time_diferenc > 0 and time_diferenc < 5*60:

                        if conactions_df == 0:
                            df = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                        else:
                            df_new = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                            df.append(df_new)
                        
                        print("df \n",df)

        if hauer > 24-5:
            tomorow_datetime = datetime.today() + datetime.timedelta(days=1)
            tomorow = calendar.day_name[tomorow_datetime.weekday()].lower()
            tomorow_is_serfed = serves_days[tomorow].to_numpy()[0]
            print("yesterday_is_serfed \n",tomorow_is_serfed)

            if tomorow_is_serfed == 1:

                routes_row = name_dict["routes"].loc[name_dict["routes"]["route_id"] == route_id_instanz]
                print("routes_row \n",routes_row)

                print("trip_id_instanz \n",trip_id_instanz)

                stop_times_trip_id_instanz = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]
                print("stop_times_trip_id_instanz \n",stop_times_trip_id_instanz)

                trip_id_stops = stop_times_trip_id_instanz.loc[stop_times_trip_id_instanz["stop_id"].isin(stop_IDs)]
                print("trip_id_stops \n",trip_id_stops)

                agency_id_instanz = routes_row['agency_id'].to_numpy()[0]
                agency_name_instanz = name_dict["agency"].loc[name_dict["agency"]["agency_id"] == agency_id_instanz]['agency_name'].to_numpy()[0]


                #Nordwest bahn
                agency_name_instanz
                #RE15
                route_long_name = routes_row['route_long_name'].to_numpy()[0]
                #Münster
                end_station_name
                #9:07
                arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
                #9:09
                departure_time = trip_id_stops['departure_time'].to_numpy()[0]

                print(" ")
                print(" ")
                print(agency_name_instanz)
                print("AAAAAAAAAAAA ")
                print(route_long_name)
                print("BBBBBBBBBBBBBBBBBBBBBB ")
                print(end_station_name)
                print("CCCCCCCCCCCCCCCCCCCCCCCCCC ")
                print(arrival_time)
                print("DDDDDDDDDDDDDDDDDDDDDDDD ")
                print(departure_time)

                
                houer_dif = 24 - hauer -1
                min = int(datetime.now().strftime("%M"))
                min_dif = 60 - min

                time_diferenc = int(arrival_time[0:2])*60 + int(arrival_time[3:5]) + houer_dif*60 + min_dif
                print("time_diferenc \n",time_diferenc)

                if time_diferenc > 0 and time_diferenc < 5*60:

                    if conactions_df == 0:
                        df = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                    else:
                        df_new = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                        df.append(df_new)
                        
                    print("df \n",df)
        

        if day_is_serfed == 1:
            routes_row = name_dict["routes"].loc[name_dict["routes"]["route_id"] == route_id_instanz]
            print("routes_row \n",routes_row)

            print("trip_id_instanz \n",trip_id_instanz)

            stop_times_trip_id_instanz = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]
            print("stop_times_trip_id_instanz \n",stop_times_trip_id_instanz)

            trip_id_stops = stop_times_trip_id_instanz.loc[stop_times_trip_id_instanz["stop_id"].isin(stop_IDs)]
            print("trip_id_stops \n",trip_id_stops)

            agency_id_instanz = routes_row['agency_id'].to_numpy()[0]
            agency_name_instanz = name_dict["agency"].loc[name_dict["agency"]["agency_id"] == agency_id_instanz]['agency_name'].to_numpy()[0]

            #Nordwest bahn
            agency_name_instanz
            #RE15
            route_long_name = routes_row['route_long_name'].to_numpy()[0]
            #Münster
            end_station_name
            #9:07
            arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
            #9:09
            departure_time = trip_id_stops['departure_time'].to_numpy()[0]

            print(" ")
            print(" ")
            print(agency_name_instanz)
            print("AAAAAAAAAAAA ")
            print(route_long_name)
            print("BBBBBBBBBBBBBBBBBBBBBB ")
            print(end_station_name)
            print("CCCCCCCCCCCCCCCCCCCCCCCCCC ")
            print(arrival_time)
            print("DDDDDDDDDDDDDDDDDDDDDDDD ")
            print(departure_time)

            
            print((int(arrival_time[0:2])-hauer)*60)
            min = int(datetime.now().strftime("%M"))
            print(min)
            print((arrival_time[3:5]))
            print((int(arrival_time[3:5])-min))

            min = int(datetime.now().strftime("%M"))
            time_diferenc = (int(arrival_time[0:2])-hauer)*60 + (int(arrival_time[3:5])-min)
            print("time_diferenc \n",time_diferenc)

            if time_diferenc > 0 and time_diferenc < 5*60:

                if conactions_df == 0:
                    df = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                else:
                    df_new = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["agency_name_instanz","route_long_name","end_station_name","arrival_time","departure_time"])
                    df.append(df_new)
                
                print("df \n",df)


        



# trip_id --> direction_id

# stop_sequence (min/max) + direction_id  -->  richtung

# trip_id --> Tag / färt heute

# die nächsten züge


























