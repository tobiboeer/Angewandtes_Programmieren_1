# README

**Note:** This is a short ReadMe. The extented version can be found in the menubar
while running the program or in the 'Data' directory.

**Date:** 13. May 2022 

**Authors:** Fabian Kessener, Tobias Boeer, Timon Fass 

**Version:** 1.0 

---

**Executing the Program** 

This program was only tested with Windows 10 and Python 3.8.4, 3.10.2, 3.10.3.
Before use you need to install following modules: 
 - pandas 
 - geojson
 - PySide6
 - numpy
 - markdown
 
To start the program you need to execute the file Start_Program.py. 
*Keep in mind:* If you delete one of the 'stops', 'connections' files in the directory
'Data' at the beginning, the programm is able to calculate them again by using the 
'latest' directories. But especially in the case of the 'Nahverkehr' data this can take
a very long time (around 6 hours). To trigger the calculation you need to start the program
and click one of the three buttons (Nahverkehr, Fernverkehr, Regional).

**The Nahverkehr data is not included in the GIT repository, because it takes up too much space.** 
But you can easily add it just by adding the directory 'latest_nah' manually. 

---

**Using the Program** 

In the center of the program you can see the map of Germany, which shows stations and
routes from different train networks. This map is interactive. You can
zoom in and out by using the mousewheel. Unfortunately, the zoom does
not work like intended. Per default it always zooms to the bottom left
corner. If you click somewhere in the map (by using mousewheel or left-click)
you can zoom approximately in the right direction, but not precisely. 
For this reason, the map has scrollbars to navigate to the right location.
Clicking a station will open up its information in the table below the
map.

If you hover over a station or a district, its name will always be shown in the
bottom left corner.

On the right side you can see an user interface. On the top you can choose
if you want to see local transport ("Nahverkehr"), long distance ("Fernverkehr")
or regional distance ("Regional") train stations by clicking the buttons. The 
map and the dropdown menu below will change and show the associated stations.

*Keep in mind:* If there is missing data it will be calculated again, but for
local transportation data this does take a long time and your CPU is fully occupied.

If you select a type of trains by using the three buttons on top, you can
choose the starting station ('Abfahrbahnhof') in the dropdown menu below or by clicking it directly in the map.
When using the menu you can type letters of your wanted station
to jump to this point of the list. You can also choose a date time and a time span. For further information
see the Tutorial.
After clicking 'Anfrage stellen' you get the train information, which are departuring from the train station in the chosen
time span in the table below. The time span is the time in hours before and after the 'Zeit der Abfahrt'. 
Only these trains will be shown.

---   

**Special Features**

List of special features:

 - Map of Germany shows every district
 
	Showing the station and the districts in the bottom left corner if the mouse hovers over them.
	Train stations can be selected by clicking on them directly.
	
 - Markdown 'Help' Menu
 
	Allows to open an 'About/Licence' page and this ReadMe-file as a new window in the program.
	
 - Switching between different train types
 
	By using the buttons 'Nahverkehr', 'Fernverkehr' and 'Regional'
	
 - Dropdown Menu with train stations
 
	Allows to select the wanted station from a list instead of clicking it.
	Also reacts to typing, to make the search easier.
	
 - Overview Window
 
	Shows messages for the user. For example if data is missing
	
 - Tutorial
 
	An image Tutorial in the Menubar will show you the usage of this program a little bit more detailed.
	
 - Restoring of missing data while running the program
 
	Restorable files are the ones beginning with 'stops', 'connections' in the 'Data' directory.
