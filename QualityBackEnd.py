"""
Name: Rachel Ieda and Tony Ta
Description: This is the back end of the application, which creates API calls to the Teleport website for data on
urban areas. There are methods for retrieving certain parts of the API, plotting the data onto different types of graphs,
and calculating distances between urban areas.
"""

import requests
import threading
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from PIL import Image
from io import BytesIO
import math


class UrbanAreas:
    """accessing data for UrbanAreas"""

    def __init__(self):
        """creates an object containing the list of urban areas and methods to access it's data"""

        # retrieve urban areas
        url = 'https://api.teleport.org/api/urban_areas/'
        page = requests.get(url)
        resultDict = page.json()

        urbanAreasID = {}  # dictionary with the country names as keys, links to salary data as values
        for d in resultDict['_links']["ua:item"]:
            urbanAreasID[d['name']] = d['href']
        self._urbanAreasID = urbanAreasID

        # retrieve list of jobs
        url2 = 'https://api.teleport.org/api/urban_areas/slug%3Aaarhus/salaries/'
        page2 = requests.get(url2)
        resultDict2 = page2.json()

        jobs = []
        for d in resultDict2['salaries']:
            jobs.append(d['job']['title'])
        self._jobs = jobs

        # retrieve list of metrics
        url3 = 'https://api.teleport.org/api/urban_areas/slug%253Aaarhus/scores/'
        page3 = requests.get(url3)
        resultDict3 = page3.json()

        metrics = []
        for d in resultDict3['categories']:
            metrics.append(d['name'])
        self._metrics = metrics

        # for sharing data and creating an SQLite database
        self._qualityData = None

        # retrieving image for plotMap()
        # url4 = 'https://upload.wikimedia.org/wikipedia/commons/8/83/Equirectangular_projection_SW.jpg'
        url4 = 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Equirectangular_projection_SW.jpg/1280px-Equirectangular_projection_SW.jpg'
        response4 = requests.get(url4)
        self._img = Image.open(BytesIO(response4.content))

    def getUrbanAreas(self):
        """gets a list of urban areas without the id

        :return: a list of urban areas
        """
        return list(self._urbanAreasID.keys())

    def getJobs(self):
        """gets a list of jobs

        :return: a list of jobs
        """
        return self._jobs

    def getMetrics(self):
        """get a list of quality of life metrics

        :return: a list of quality of life metrics
        """
        return self._metrics

    def plotSalaries(self, job, urbanAreas):
        """plots the salaries for a given job for a list of urban areas

        :param job: a string containing the name of the job
        :param urbanAreas: a list of strings of urban areas
        :return: None, but produces a plot that can be accessed through a lambda function
        """
        data = {}

        def salaryData(urbanArea, urbanAreasID):
            url = urbanAreasID[urbanArea] + 'salaries/'
            page = requests.get(url)
            resultDict = page.json()

            salary = [None] * 3
            for r in resultDict['salaries']:
                if r['job']['title'] == job:
                    salary[0] = r['salary_percentiles']['percentile_25']
                    salary[1] = r['salary_percentiles']['percentile_50']
                    salary[2] = r['salary_percentiles']['percentile_75']
                    data[urbanArea] = salary
                    break

        # threading to retrieve data faster
        threads = []

        for a in urbanAreas:  # convert this to multithreading
            t = threading.Thread(target=salaryData, args=(a, self._urbanAreasID))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # moving data away from thread safe container for plotting
        labels = []
        percentile_25 = []
        percentile_50 = []
        percentile_75 = []

        i = 0
        for k, v in data.items():
            labels.append(k)
            percentile_25.append(v[0])
            percentile_50.append(v[1])
            percentile_75.append(v[2])
            i += 1

        # forming stacked bar chart
        fig, ax = plt.subplots()

        ax.bar(labels, percentile_75, label='75th Percentile', zorder=3)
        ax.bar(labels, percentile_50, label='50th Percentile', zorder=3)
        ax.bar(labels, percentile_25, label='25th Percentile', zorder=3)

        ax.yaxis.set_major_formatter(mtick.StrMethodFormatter('${x:,.0f}'))
        ax.set_ylabel('Salary ($)')
        ax.set_xlabel('Urban Areas')
        ax.set_title('Salaries By Urban Area')
        ax.legend()

        xLocations = tuple([i for i in range(0, len(urbanAreas))])
        if len(urbanAreas) > 5:
            degrees = 90
        else:
            degrees = 0
        plt.xticks(xLocations, labels, rotation=degrees)
        plt.xticks()
        plt.grid(axis='y')
        plt.tight_layout()

        # plt.show()
        return fig  # this is needed to display subplots in tkinter

    def plotCompareQuality(self, metric, urbanAreas):
        """Compares and plots a single quality of life metric between multiple urban areas

        :param metric: a string with the quality of life metric
        :param urbanAreas: a list of strings of urban areas
        :return: None, but produces a plot that can be accessed through a lambda function
        """
        data = {}

        def metricData(urbanArea, metricIn, urbanAreasID):
            url = urbanAreasID[urbanArea] + 'scores/'
            page = requests.get(url)
            resultDict = page.json()

            for r in resultDict['categories']:
                if r['name'] == metricIn:
                    data[urbanArea] = r['score_out_of_10']
                    break

        # threading to retrieve data faster
        threads = []

        for a in urbanAreas:  # convert this to multithreading
            t = threading.Thread(target=metricData, args=(a, metric, self._urbanAreasID))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # forming stacked bar chart
        labels = []
        scores = []

        for k, v in data.items():
            labels.append(k)
            scores.append(v)

        plt.bar(labels, scores, zorder=3)

        # x-axis markings
        plt.xlabel('Urban Area')
        xLocations = tuple([i for i in range(0, len(urbanAreas))])
        if len(urbanAreas) > 5:
            degrees = 90
        else:
            degrees = 0
        plt.xticks(xLocations, labels, rotation=degrees)

        # y-axis markings
        yLocations = tuple([i for i in range(0, 11)])
        plt.yticks(yLocations, yLocations)
        plt.ylabel('Score out of 10')

        # general plot markings
        plt.title(f'Scores for {metric} by Urban Area')
        (xMin, xMax, yMin, yMax) = plt.axis()
        plt.axis((xMin, xMax, 0, 10))
        plt.grid(axis='y')
        plt.tight_layout()

        # plt.show()

    def plotAllQuality(self, urbanArea):
        """plots all quality of life metrics for one urban area

        :param urbanArea: a string containing a single urban area
        :return: None, but produces a plot that can be accessed through a lambda function
        """

        metrics = []
        scores = []
        url = self._urbanAreasID[urbanArea] + 'scores/'
        page = requests.get(url)
        resultDict = page.json()

        for r in resultDict['categories']:
            metrics.append(r['name'])
            scores.append(r['score_out_of_10'])

        # saves data into instances variable to be used in the SQLite database
        self._qualityData = (urbanArea, metrics, scores)

        plt.bar(metrics, scores, zorder=3)

        # x-axis markings
        plt.xlabel('Metric')
        xLocations = tuple([i for i in range(0, len(metrics))])
        plt.xticks(xLocations, metrics, rotation=90)

        # y-axis markings
        yLocations = tuple([i for i in range(0, 11)])
        plt.yticks(yLocations, yLocations)
        plt.ylabel('Score out of 10')

        # general plot markings
        plt.title(f'Quality of Life Scores in {urbanArea}')
        (xMin, xMax, yMin, yMax) = plt.axis()
        plt.axis((xMin, xMax, 0, 10))
        plt.grid(axis='y')
        plt.tight_layout()

        # plt.show()

    def getData(self):
        """getting the most recent quality of life data to be saved into a text file from the front end

        :return: a tuple of data containing (urbanArea, [list of metrics], [list of scores])
        """
        return self._qualityData

    def plotCostOfLiving(self, urbanArea):
        """plot details for cost of living

        :param urbanArea: a string containing a single urban area
        :return: None, but produces a plot that can be accessed through a lambda function
        """
        url = self._urbanAreasID[urbanArea] + 'details/'
        page = requests.get(url)
        resultDict = page.json()

        labels = []
        costs = []
        for r in resultDict['categories']:
            if r['data'][0]['id'] == 'CONSUMER-PRICE-INDEX-TELESCORE':
                for d in r['data']:
                    if 'currency_dollar_value' in d:
                        labels.append(d['label'])
                        costs.append(d['currency_dollar_value'])

        if costs: # if data is available
            bars = plt.bar(labels, costs, zorder=3)
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x(), yval+0.005, f'${yval}')
            xLocations = tuple([i for i in range(0, len(labels))])
            plt.xticks(xLocations, labels, rotation=90)
        else: # if data is not available
            plt.text(1,1,'(No Data Available)', fontsize=20, horizontalalignment='center',
                     verticalalignment='center')
            xLocations = (0,1,2)
            plt.xticks(xLocations,None)
            yLocations = (0,1,2)
            plt.yticks(yLocations,None)
            plt.axis('off')

        plt.xlabel('Metric')
        plt.ylabel('Cost ($)')
        plt.title(f'Cost of living in {urbanArea}')
        plt.grid(axis='y')
        plt.tight_layout()

        # plt.show()

    def plotMap(self, startingArea, urbanAreas):
        """plots the urban areas the user wants to go to on a map

        :param startingArea: a string containing the starting urban area of the user
        :param urbanAreas: a list of strings of urbanAreas the user intends to move to
        :return: None
        """

        imgWidth, imgHeight = self._img.size

        def mapCoord(urbanAreaID, area):
            url1 = urbanAreaID[area]
            page = requests.get(url1)
            resultDict = page.json()

            data = {}
            for k, v in resultDict['bounding_box']['latlon'].items():
                data[k] = v

            lon = (data['east'] + data['west']) / 2
            lat = (data['north'] + data['south']) / 2

            xCoord = ((lon + 180) / 360) * imgWidth
            yCoord = (1 - ((lat + 90) / 180)) * imgHeight

            return xCoord, yCoord

        startingAreaCoord = mapCoord(self._urbanAreasID, startingArea)

        destinationCoord = {}
        for a in urbanAreas:
            destinationCoord[a] = mapCoord(self._urbanAreasID, a)

        flightLength = {}
        pathCoord = {}

        for a in urbanAreas:
            xVal = [startingAreaCoord[0], destinationCoord[a][0]]
            yVal = [startingAreaCoord[1], destinationCoord[a][1]]
            pathCoord[a] = (xVal, yVal)

            lon1 = pathCoord[a][0][0]
            lat1 = pathCoord[a][1][0]
            lon2 = pathCoord[a][0][1]
            lat2 = pathCoord[a][1][1]

            R = 6373  # radius of the earth in km
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            ar = (math.sin(dlat / 2)) ** 2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon / 2)) ** 2
            c = 2 * math.atan2(math.sqrt(ar), math.sqrt(1 - ar))
            d = R * c
            vPlane = 926  # average cruising speed of commercial planes in km/h
            flightHours = d / vPlane
            flightLength[a] = round(flightHours*2)/2

        fig, ax = plt.subplots()
        fig.set_figheight(7)
        fig.set_figwidth(10)
        ax.imshow(self._img)

        plt.plot(startingAreaCoord[0], startingAreaCoord[1], 'ro')
        plt.annotate(startingArea, startingAreaCoord, color='k')

        for a in urbanAreas:
            plt.plot(pathCoord[a][0], pathCoord[a][1], 'r', label=a)
            plt.plot(pathCoord[a][0][1], pathCoord[a][1][1], 'ro')
            plt.annotate(f'{a}, {flightLength[a]:.1f} hours', (pathCoord[a][0][1], pathCoord[a][1][1]), color='k')

        plt.title('Location of Urban Areas and Hours by Flight')
        plt.axis('off')
        plt.tight_layout()

        # plt.show()

        return fig  # this is needed to display subplots in tkinter

    def nearestArea(self, latitude, longitude):
        """finds the nearest urban area to the user and an image of it

        :param longitude: longitude in degrees between the range of -180 to 180
        :param latitude: latitude in degrees between the range of -90 to 180
        :return: a tuple containing the nearest urban area of the user and an image of it (nearestArea, image)

        """
        url2 = 'https://api.teleport.org/api/locations/' + str(latitude) + ',' + str(longitude)
        page2 = requests.get(url2)
        resultDict2 = page2.json()
        nearestUrbanAreaImage = None

        try:
            nearestUrbanArea = resultDict2['_embedded']['location:nearest-urban-areas'][0]['_links']['location:nearest-' 
                                                                                                'urban-area']['name']
            url3 = self._urbanAreasID[nearestUrbanArea] + 'images/'
            page3 = requests.get(url3)
            resultDict3 = page3.json()

            imgLink = resultDict3['photos'][0]['image']['web']
            response = requests.get(imgLink)
            nearestUrbanAreaImage = Image.open(BytesIO(response.content))

        except (IndexError, TypeError):
            try:
                nearestUrbanArea = resultDict2['_embedded']['location:nearest-cities'][0]['_links']['location:nearest-'
                                                                                                'city']['name']
            except (IndexError, TypeError):
                nearestUrbanArea = None

        return nearestUrbanArea, nearestUrbanAreaImage


### ---------- Documentation ---------- ###

### UrbanAreas() creates an object for accessing information for an urban area

### uncomment the line below when testing out the examples below
# u = UrbanAreas()

### here is a list of 10 countries in case you want to try cases with more than 3:
# ['Aarhus', 'Adelaide', 'Albuquerque', 'Almaty', 'Amsterdam', 'Anchorage', 'Andorra', 'Ankara', 'Asheville',
# 'Asuncion']

### ---------- Getting List of Urban Areas (all choices) -----------###

### Usage: getUrbanAreas()
### to print out a list of all the urban areas that you can put in your tkinter listbox

### run the example below to see the list of urban areas
# print('Urban areas:', u.getUrbanAreas())


### ---------- Getting List of Jobs (Choice 1)-----------###

### Usage: getJobs()
### Returns a list of jobs that you can put in your tkinter listbox

### run the example below to see the list of jobs
# print('Jobs:', u.getJobs())


### ---------- Getting Quality of Life Metrics (Choice 2)-----------###

### Usage: getMetrics()
### Returns a list of metrics that you can put in your tkinter listbox

### run the example below to see the list of jobs
# print('Metrics:', u.getMetrics())


### ---------- Plotting Salary (Choice 1) -----------###

### Usage: plotSalaries(job, urbanAreas)
### Plots out salaries for the job 'Account Manager' and the urban areas ['Aarhus','Adelaide','Albuquerque']

### run the example below and uncomment #plt.show in plotSalaries() to see an example plot without tkinter:
# u.plotSalaries('Account Manager', ['Aarhus', 'Adelaide', 'Albuquerque'])

### an example of how to use this with tkinter, where PlotWindow is the tk.TopLevel class:
# PlotWindow(lambda: u.plotSalaries('Account Manager', ['Aarhus', 'Adelaide', 'Albuquerque']))


### ---------- Plotting Comparing Quality of Life Across Multiple Areas (Choice 2) -----------###

### Usage: plotCompareQuality(metric, urbanAreas)
### Plots out quality of life scores for a given metric across multiple urban areas
### returns a figure to be used in PlotWindow() class, has multiple *subplots*

### run the example below and uncomment #plt.show in plotCompareQuality() to see an example plot without tkinter:
# u.plotCompareQuality('Housing', ['Aarhus', 'Adelaide', 'Albuquerque'])

### an example of how to use this with tkinter, where PlotWindow is the tk.TopLevel class:
# use a PlotWindow() class that takes in a figure from this method
# PlotWindow(lambda: u.plotCompareQuality('Housing', ['Aarhus', 'Adelaide', 'Albuquerque']))


### ---------- Plotting Comparing Quality of Life Across One Area (Choice 3A) -----------###

### Usage: plotAllQuality(urbanArea)
### Plots out all quality of life scores for a given urban area, returns data in an SQLite database

### run the example below and uncomment #plt.show in plotCompareQuality() to see an example plot without tkinter:
# u.plotAllQuality('Aarhus')


### an example of how to use this with tkinter, where PlotWindow is the tk.TopLevel class:
# PlotWindow(lambda: u.plotAllQuality('Aarhus'))


### ---------- Plotting Cost of Living Across One Area (Choice 3B) -----------###

### Usage: plotCostOfLiving(urbanArea)
### Plots out costs of living for a given urban area

### run the example below and uncomment #plt.show in plotCostOfLiving() to see an example plot without tkinter:
# u.plotCostOfLiving('Aarhus')

### an example of how to use this with tkinter, where PlotWindow is the tk.TopLevel class:
# PlotWindow(lambda: u.plotCostOfLiving('Aarhus'))


### ---------- Getting Data for the Text file (Choice 3A1) -----------###

### Usage: getData()
### Returns the most recent quality of life data ran by user
### formatted as (urban area, [list of metrics], [list of scores out of 10])

### run the example below to see the data
# u.plotAllQuality('Aarhus')
# data = u.getData()
# print(data)


### ---------- Mapping Distances of Urban Areas (Choice 4) -----------###

### Usage: plotMap(startingArea, urbanAreas)
### Plots out the locations from a starting area to multiple urban areas
### returns a figure to be used in PlotWindow() class, has a *subplot*

# run the example below and uncomment #plt.show in plotMap() to see an example plot without tkinter:
# u.plotMap('Aarhus', ['Adelaide', 'Albuquerque', 'Almaty'])


### ---------- Nearest Urban Area (Choice 4) -----------###

### Usage: nearestArea(startingArea)
### finds the nearest urban area based on current coordinates retrieves an image for it
### run the example below to display the image in tkinter

# nearestArea, nearestAreaImage = u.nearestArea(20, 25)  # (latitude, longitude)
#
# import tkinter
# from tkinter import *
# from PIL import Image, ImageTk
#
# root = Tk()
# root.minsize(500, 500)
#
# # Create a photoimage object of the image in the path
# if nearestAreaImage is not None:
#     image1 = nearestAreaImage  # put image here
#     test = ImageTk.PhotoImage(image1)
#
#     label1 = tkinter.Label(image=test)
#     label1.image = test
#     # label1.place(x=20,y=20) # you can also use this to place at a specific location,
#     # with x='x_pixels' and y='y_pixels'
# else:
#     label1 = tkinter.Label(root, text='(Image Unavailable)', font=14)
#
# label1.pack()
#
# # Position image
# if nearestArea is None:
#     nearestArea = '(No nearby urban areas)' # change label if unavailable
#
# label2 = tkinter.Label(root, text=nearestArea, font=14)  # label for the name of the nearest urban area
# label2.pack()
#
# root.mainloop()
