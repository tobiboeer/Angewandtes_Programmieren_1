# README

**Date:** 13. May 2022

**Authors:** Fabian Kessener, Tobias Boeer, Timon Fass

**Version:** 1.0

---

**Executing the Program**

This program was only tested with Windows 10 (was habt ihr für
Betriebssysteme?) and Python 3.10.2 (Welche Version habt ihr?).
Before use you need to install following modules:
- pandas
- geojson
- PySide6
- numpy  

To start the program you need to execute the file XXXX.py. 
Data preparation can be done with XXXX.py but this takes a long time.

---

**Using the Program**

If you execute the program, you get the following window: (hier wird natürlich am Ende ein aktuelles Bild hingepackt)

![Screenshot](Data/images/ScreenshotProgramm.png)

In the center you can see the map of Germany, which shows stations and
routes for different train networks. This map is interactive. You can
zoom in and out by using the mousewheel. Unfortunately, the zoom does
not work like intended. Per default it always zooms to the bottom left
corner. If you click somewhere in the map (by using mousewheel or left-click)
you can zoom approximately in the right direction, but not precisely. 
For this reason, the map has scrollbars to navigate to the right location.
Clicking a station will open up its information in the table below the
map.

If you hover over a station or a district, it will always be shown in the
bottom left corner.

On the right side you can see an user interface. On the top you can choose
if you want to see local transport ("Nahverkehr"), long distance ("Fernverkehr")
or regional distance ("Regional") train stations by clicking the buttons. The 
map and the dropdown menu below will change and show the associated stations.

*Important:* Keep in mind, it will take a long time to load the local 
transport data and the program might hang up for a couple of seconds. If you
keep it running, it will do its work, but the navigation will be slow.

If you select a type of trains by using the three buttons on top, you can
choose the starting station ('Abfahrbahnhof') in the dropdown menu below.
When using this menu you can type the first letter of your wanted station
to jump to this point of the list. The selected items will be shown in the
small information window below.  
 

---

**Special Features**

List of special features:

- Map of Germany shows every district

- Showing the station and the districts in the bottom left corner if the mouse
hovers over them

- Markdown 'Help' Menu
	
	Allows to open an 'About/Licence' page and this ReadMe-file as a new
	window in the program.
	
- Switching between different train types

	By using the buttons 'Nahverkehr', 'Fernverkehr' and 'Regional'
	
- Dropdown Menu with train stations

	Allows to select the wanted station from a list instead of clicking it.
	Also reacts to typing, to make the search easier.
	
- Overview window

	Shows every selected item in a small overview. Can be cleared, by using the
	button 'Löschen'

---

Änderungshistorie?
