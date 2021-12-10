================================
READ ME:

This project aims to visualize and compare different metrics of urban areas,
including quality of life, cost of living, and salaries. 
The QualityBackEnd.py file contains the back end of the project, 
which is where the API calls, matplotlib graphs, and any calculations are made. 
The QualityFrontEnd.py file is the front end of the project, where the tkinter 
module is used to create an user interface to interact with the user.

Modules:
- requests: used to make API calls to https://developers.teleport.org/api/reference/#/ ,
  which is where the data for the project is retrieved from
- threading: used for multithreading, which is used for the API calls
- matplotlib: used to visualize the data through bar charts and the world map.
- PIL: used for getting an image to display
- tkinter: used to create the user interface
- os: used to access the user file directory system for the user to save data to

