"""
Name: Rachel Ieda and Tony Ta
Description: This is the front end of the application, which allows for the user to interact with the methods in the
back end. The user can click on buttons and listboxes on tkinter windows to make selections of what urban area information
they would like to visualize or compare.
"""

import tkinter as tk
import tkinter.messagebox as tkmb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.filedialog
import os
from QualityBackEnd import UrbanAreas
from PIL import ImageTk


class SingClickWin(tk.Toplevel):
    """
    Top level window that allows user to choose one item from a listbox.
    """
    def __init__(self, master, choice_list):
        """
        Constructor that creates a window with a listbox of all options in the choice_list parameter and a scrollbar
        configured to the listbox.
        """
        super().__init__(master)
        self.title("Choose One")
        self.grab_set()  # Disables events for other windows
        self.focus_set()  # Sets focus to this window
        self.transient(master)  # Makes this window transient to its master window
        self._choice_list = choice_list
        self._user_choice = ''  # Will contain user choices
        self.geometry("325x190+1100+300")
        self.minsize(300, 190)
        self.resizable(True, True)

        self.LB = tk.Listbox(self, height=10, width=50, selectmode='single')
        self.LB.grid(row=1)

        scroll = tk.Scrollbar(self, orient="vertical")
        scroll.config(command=self.LB.yview)
        scroll.grid(row=1, column=1, sticky='ns')
        self.LB.config(yscrollcommand=scroll.set)

        self.LB.insert(tk.END, *self._choice_list)

        b1 = tk.Button(self, text="OK", command=self.set_choice)
        b1.grid(row=2)  # Grids the button

    def set_choice(self):
        """
        Sets the user choice to whatever the user selects in the listbox
        """
        if self.LB.curselection():
            self._user_choice = self._choice_list[self.LB.curselection()[0]]
            self.destroy()

    def get_choice(self):
        """
        Gets the user choice
        """
        return self._user_choice


class MultUrbanAreaWin(tk.Toplevel):
    """
    Top level class that allows the user to choose multiple urban areas to look at.
    """
    def __init__(self, master):
        """
        Constructor of the window that contains a listbox of all urban areas, a scrollbar that is configured to the
        listbox, and a button that allows the user to confirm their choices.
        """
        super().__init__(master)
        self._UrbanAreas = UrbanAreas()
        self.title("Choose Your Urban Areas")
        self.grab_set()  # Disables events for other windows
        self.focus_set()  # Sets focus to this window
        self.transient(master)  # Makes this window transient to its master window
        self.geometry("325x190+1100+300")
        self.minsize(300, 190)
        self.resizable(True, True)

        self._user_choices = []  # Will contain user choices

        self.LB = tk.Listbox(self, height=10, width=50, selectmode="multiple")  # Creates a Listbox
        self.LB.grid()  # Grids the Listbox

        S = tk.Scrollbar(self, orient="vertical")  # Creates a Scrollbar that configures to the Listbox
        S.config(command=self.LB.yview)
        S.grid(row=0, column=1, sticky='ns')  # Grids the Scrollbar
        self.LB.config(yscrollcommand=S.set)

        self._ua_list = self._UrbanAreas.getUrbanAreas()
        self.LB.insert(tk.END, *self._ua_list)

        b1 = tk.Button(self, text="OK", command=self.set_urban_areas)
        b1.grid(row=1)  # Grids the button

    def set_urban_areas(self):
        """
        Sets the user choices as a list of all the urban areas selected by user in the listbox
        """
        choice_num = list(self.LB.curselection())
        self._user_choices = [self._ua_list[i] for i in choice_num]
        self.destroy()

    def get_urban_areas(self):
        """
        Gets the list of user choices
        """
        return self._user_choices


class QolForOneUAWin(tk.Toplevel):
    """
    Top level class that allows user to choose to plot the quality of life data or cost of living data.
    If the user chooses the first option, a PlotWin object is created. When the PlotWin window is closed,
    the user can select to save that data to the file. If the user chooses the second option, a PlotWin object
    is created and the cost of living data is plotted.
    """
    def __init__(self, master, ua):
        """
        Constructor of the window that contains two buttons, one to plot the quality of life data and another to
        plot the cost of living data.
        """
        super().__init__(master)
        self._UrbanAreas = UrbanAreas()
        self._ua = ua
        self.title("Option Window")
        self.geometry("550x250+1100+300")
        self.minsize(550, 250)
        self.resizable(True, True)
        self.configure(bg='orange2')
        tk.Label(self, text="Choose one of the following options:", fg='dark green', font=('Trebuchet MS', 18),
                 bg='orange2').grid(columnspan=3)
        tk.Button(self, text="Plot Quality of Life Data", command=self.plt_qol, font=('Arial', 12), width=20, height=3,
                  bg='linen', fg='dark green').grid(row=1, column=0, padx=30, pady=10)
        tk.Label(self, text='Select this option to see all\nquality of life data plotted', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=3, column=0, padx=30, pady=10)
        tk.Button(self, text="Plot Cost of Living Data", command=self.plt_col, font=('Arial', 12), width=20, height=3,
                  bg='linen', fg='dark green').grid(row=1, column=2, padx=30, pady=10)
        tk.Label(self, text='Select this option plot\ndetailed cost of living data', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=3, column=2, padx=30, pady=10)

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def plt_qol(self):
        """
        This method creates a PlotWin object that plots the quality of life data. When the window is closed, the user
        can select to save the data to a file. If they choose it, then the save_to_file static method is called.
        """
        win = PlotWin(self, lambda: self._UrbanAreas.plotAllQuality(self._ua))
        self.wait_window(win)
        save_choice = tkmb.askokcancel("Save", "Save result to file?")
        if save_choice:
            save_data = self._UrbanAreas.getData()
            self.save_to_file(save_data)

    @staticmethod
    def save_to_file(s_data):
        """
        This static method asks for the user's directory and changes their current directory to it. An output text file
        is open/created and the data is written into the file.
        """
        d = tk.filedialog.askdirectory(initialdir='.')  # user is prompted to choose a directory
        if d != '':  # in case the user selects to save but then cancels when directory opens
            os.chdir(d)  # the current directory will now be at the user-chosen directory
            with open('saved.txt', 'w') as outFile:
                outFile.write('Urban Area: ')
                outFile.write(s_data[0])
                outFile.write('\n')
                for i in range(len(s_data[1])):
                    outFile.write(s_data[1][i])
                    outFile.write(": ")
                    outFile.write(str(s_data[2][i]))
                    outFile.write("\n")
                outFile.write("\n\n")

    def plt_col(self):
        """
        A PlotWin object is created that plots the cost of living for the user-chosen urban area.
        """
        win = PlotWin(self, lambda: self._UrbanAreas.plotCostOfLiving(self._ua))
        win.transient()


class DistanceUAWin(tk.Toplevel):
    """
    Top level window that contains two buttons: one that allows the user to choose urban areas and to plot their locations
    on a map, and the other to get the nearest urban area to the coordinates of their choosing.

    * NOTE: In the project proposal, we were going to have the user select an urban area first before choosing one of
    the buttons. However, we found that using the coordinates of an urban area to show the nearest urban area would actually
    give the user the current urban area, rather than the nearest one. So, if the user chooses to show the nearest urban
    area, they will input coordinates instead of choosing an urban area.
    """
    def __init__(self, master):
        super().__init__(master)
        self._UrbanAreas = UrbanAreas()
        self.title("Option Window")
        self.geometry("600x250+1100+300")
        self.minsize(600, 250)
        self.resizable(True, True)
        self.configure(bg='orange2')

        tk.Label(self, text="Choose one of the following options:", fg='dark green', font=('Trebuchet MS', 18),
                 bg='orange2').grid(columnspan=3)
        tk.Button(self, text="Map Distance by Flight", command=self.select_ua, font=('Arial', 12), width=25, height=3,
                  bg='linen', fg='dark green').grid(row=1, column=0, padx=30, pady=10)
        tk.Label(self, text='Select this option to map\nselected area to other areas and\nsee distance by flight',
                 fg='dark green', font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=3, column=0,
                                                                                                 padx=30, pady=10)
        tk.Button(self, text="Show Nearest Urban Area", command=self.show_ua, font=('Arial', 12), width=25, height=3,
                  bg='linen', fg='dark green').grid(row=1, column=2, padx=30, pady=10)
        tk.Label(self, text='Select this option to see nearest\nurban area and an image of it\n(depending on location '
                            'selected,\ndata is not always available)', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=3, column=2, padx=30, pady=10)

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def select_ua(self):
        """
        Method that creates a SingClickWin object and gets the user's urban area choice. Then, a MultUrbanAreaWin object
        is created, where the user can select multiple urban areas to compare their initial urban area choice to.
        A PlotFigureWin is then created with those choices, where the locations are plotted on a world map.
        """
        ua_list = self._UrbanAreas.getUrbanAreas()
        sqol_win = SingClickWin(self, ua_list)
        self.wait_window(sqol_win)
        ua = sqol_win.get_choice()
        if ua:
            mult = MultUrbanAreaWin(self)
            self.wait_window(mult)
            ua_choices = mult.get_urban_areas()
            if ua_choices:
                win = PlotFigureWin(self, lambda: self._UrbanAreas.plotMap(ua, ua_choices))
                win.transient()

    def show_ua(self):
        """
        Method that creates a NearestAreaWin object.
        """
        win = NearestAreaWin(self)
        win.transient()


class NearestAreaWin(tk.Toplevel):
    """
    Top level class that is called when the user wants to find the nearest urban area to a certain coordinate location.
    The user inputs latitude and longitude coordinates and the nearest urban area is displayed in a separate window, along
    with an accompanying image, if possible.
    """
    def __init__(self, master):
        """
        Constructor of the window that contains two entry boxes for the user to input their latitude and longitude
        coordinates. There is also a button for the user to lock in their coordinate choices.
        """
        super().__init__(master)
        self.title("Option Window")
        self.minsize(450, 300)
        self.geometry('450x300+1100+300')
        self.resizable(True, True)
        self.configure(bg='orange2')

        self._UrbanAreas = UrbanAreas()

        tk.Label(self, text="Please input current coordinates:", bg='orange2', fg='dark green',
                 font=('Trebuchet MS', 14)).grid(padx=10, pady=10)
        self._entryText1 = tk.DoubleVar()
        tk.Label(self, text="Latitude (-90.0 to 90.0): ", bg='orange2', fg='dark green',
                 font=('Trebuchet MS', 14)).grid(row=1, column=0, padx=10, pady=10)
        E1 = tk.Entry(self, textvariable=self._entryText1)
        E1.grid(row=1, column=1)

        self._entryText2 = tk.DoubleVar()
        tk.Label(self, text="Longitude (-180.0 to 180.0): ", bg='orange2', fg='dark green',
                 font=('Trebuchet MS', 14)).grid(row=2, column=0, padx=10, pady=10)
        E2 = tk.Entry(self, textvariable=self._entryText2)
        E2.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(self, text="OK", width=10, height=1, command=self.get_nearest).grid(row=3, column=1, padx=10, pady=10)

    def get_nearest(self):
        """
        Method that is called when the user selects coordinates. If the user chooses valid coordinates, a ShowNearestUAWin
        object is created, which is a top level window with the nearest urban area and an accompanying image. If the
        user didn't choose valid coordinates, an appropriate error message is displayed.
        """
        try:
            user_lat = self._entryText1.get()
            user_long = self._entryText2.get()
            if -90.0 <= user_lat <= 90.0 and -180.0 <= user_long <= 180.0:
                n_area, n_image = self._UrbanAreas.nearestArea(user_lat, user_long)
                if n_area:
                    win = ShowNearestUAWin(self, n_area, n_image)
                    win.transient()
                else:
                    tkmb.showerror("Error", "[Error] No urban area near your location.", parent=self)  # Error message
            else:
                tkmb.showerror("Error", "[Error] Inputs not in Range.", parent=self)  # Error message
        except tk.TclError:
            tkmb.showerror("Error", "[Error] Inputs could not be read.", parent=self)  # Error message


class ShowNearestUAWin(tk.Toplevel):
    """
    Top level class that shows the nearest urban area to the user chosen area, as well as an accompanying image, if
    possible.
    """
    def __init__(self, master, n_area, n_image):
        """
        Constructor for the window that passes in the nearest urban area and its image as the parameters. They are both
        displayed. If the image doesn't exists, then a text label is displayed showing the user there is no available
        image.
        """
        super().__init__(master)
        label1_str = "Nearest Urban Area: " + n_area
        label1 = tk.Label(self, text=label1_str, font=14)  # label for the name of the nearest urban area
        label1.grid()

        if n_image:
            nearest_photo = ImageTk.PhotoImage(n_image)

            label2 = tk.Label(self, image=nearest_photo)
            label2.image = nearest_photo
            label2.grid()
        else:
            tk.Label(self, text="There is no available image for this urban area.").grid()


class PlotFigureWin(tk.Toplevel):
    """
    Top level class that is used to plot the world map and the nearest urban areas. Differs from the PlotWin class
    since it passes the plotting function when creating the canvas, rather than just a pyplot figure.
    """
    def __init__(self, master, plot_func):
        """
        Constructor of the plotting window. Puts a matplotlib plot onto the top level window
        """
        super().__init__(master)
        self.title('Plotting Window')
        figure = plot_func()
        plot_func()
        canvas = FigureCanvasTkAgg(figure, master=self)  # Creates a canvas specific for matplotlib plots
        canvas.get_tk_widget().grid()  # Grids the canvas object
        canvas.draw()  # Shows the plot to the user


class PlotWin(tk.Toplevel):
    """
    Top level class that is used to plot the world map and the nearest urban areas. Differs from the PlotFigureWin class
    since it passes the pyplot figure when creating the canvas, rather than just a plotting function.
    """
    def __init__(self, master, plot_func):
        """
        Constructor of the plotting window. Puts a matplotlib plot onto the top level window
        """
        super().__init__(master)
        self.title('Plotting Window')
        figure = plt.figure(figsize=(12, 8))
        plot_func()
        canvas = FigureCanvasTkAgg(figure, master=self)  # Creates a canvas specific for matplotlib plots
        canvas.get_tk_widget().grid()  # Grids the canvas object
        canvas.draw()  # Shows the plot to the user


class MainWin(tk.Tk):
    """
    Tkinter class that serves as the main window to the application. Has 4 buttons for the user to choose from, of which
    each is used to compare or search for different data metrics of urban areas.
    """
    def __init__(self):
        """
        Constructor of the Main Window, which has 4 buttons, all of which call a unique function that performs several
        tasks for the user. The user can compare salary data or quality of life across multiple urban areas, search
        for quality of life in one urban area, or find the distance between urban areas.
        """
        super().__init__()
        self._UrbanAreas = UrbanAreas()
        self.title("Urban Data")
        self.minsize(700, 700)
        self.geometry('700x700+300+300')
        self.resizable(True, True)
        self.configure(bg='orange2')
        tk.Label(self, text="Welcome to the Urban Data Application\nPlease select one of the following options:",
                 fg='dark green', font=('Trebuchet MS', 18), bg='orange2').grid(columnspan=3, pady=30)

        ### Need to add commands to each button ###
        tk.Button(self, text="Compare Salary Data", command=self.salary_by_ua,
                  font=('Arial', 12), width=30, height=3, bg='linen', fg='dark green').grid(row=1, column=0, padx=30,
                                                                                            pady=10)
        tk.Button(self, text="Compare Quality of Life", command=self.comp_qol,
                  font=('Arial', 12), width=30, height=3, bg='linen', fg='dark green').grid(row=1, column=2, padx=30,
                                                                                            pady=10)
        tk.Label(self, text='A graph that displays salaries by\npercentile in a stacked bar graph\n\n\n'
                            '1. Select a job field\n2. Select multiple urban areas', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=2,column=0, pady=10, sticky='N')
        tk.Label(self, text='A graph that compares a single\nquality of life metric across\nmultiple urban areas\n\n'
                            '1. Select a quality of life metric\n2. Select multiple urban areas', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=2,column=2, pady=10, sticky='N')
        tk.Button(self, text="Search Quality of Life", command=self.search_qol,
                  font=('Arial', 12), width=30, height=3, bg='linen', fg='dark green').grid(row=4, column=0, padx=30,
                                                                                            pady=10)
        tk.Button(self, text="Distances Between Urban Areas", command=self.distance_ua,
                  font=('Arial', 12), width=30, height=3, bg='linen', fg='dark green').grid(row=4, column=2, padx=30,
                                                                                            pady=10)
        tk.Label(self, text='A graph that displays all quality\nof life metrics or cost of living\n'
                            'metrics for a single urban area\n\n1. Select an urban area\n'
                            '2. Select an option:\n    i) Plot quality of life\n    ii) Plot cost of living\n'
                            '3. If quality of life is selected,\n    data may be saved', fg='dark green',
                 font=('Trebuchet MS', 12), bg='orange2', justify=tk.LEFT).grid(row=5,column=0, pady=10, sticky='N')
        tk.Label(self, text='Shows a map of distances or an\nimage of the nearest urban area\n\n\n'
                            '1. Select an urban area\n2. Select an option:\n     i) Show a map between selected area\n'
                            '        to another\n    ii) Show the nearest urban area to\n        a coordinate and an '
                            'image of it', fg='dark green', font=('Trebuchet MS', 12), bg='orange2',
                 justify=tk.LEFT).grid(row=5,column=2, pady=10, sticky='N')

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def salary_by_ua(self):
        """
        Method that is called when user wants to compare salary data across multiple urban areas. A SingClickWin object
        is created and the user choice for jobs is taken. A MultUrbanAreaWin object is then created, where the user
        selects urban areas to search from. A PlotFigureWin object is then created to plot the 25th, 50th, and 75th
        percentile of salaries of the user-chosen job title in the user-chosen urban areas.
        """
        job_list = self._UrbanAreas.getJobs()
        sbua_win = SingClickWin(self, job_list)
        self.wait_window(sbua_win)
        job = sbua_win.get_choice()
        if job:  # if user closes window without choosing anything
            ua_win = MultUrbanAreaWin(self)
            self.wait_window(ua_win)
            urb_area = ua_win.get_urban_areas()
            if urb_area:  # if user closes window without choosing anything
                sbua_plt = PlotFigureWin(self, lambda: self._UrbanAreas.plotSalaries(job, urb_area))
                sbua_plt.transient()

    def comp_qol(self):
        """
        Method that is called when the user wants to compare quality of life metrics across multiple urban areas. A
        SingClickWin object is created and the user choice for quality of life metric to look at is taken. A
        MultUrbanAreaWin object is created, where the user chooses multiple urban areas to look at. A PlotWin object is
        then created to plot the user-chosen quality of life score for all the user-selected urban areas.
        """
        qol_list = self._UrbanAreas.getMetrics()
        sbqol_win = SingClickWin(self, qol_list)
        self.wait_window(sbqol_win)
        qol = sbqol_win.get_choice()
        if qol:  # if user closes window without choosing anything
            ua_win = MultUrbanAreaWin(self)
            self.wait_window(ua_win)
            urb_area = ua_win.get_urban_areas()
            if urb_area:  # if user closes window without choosing anything
                sbqol_plt = PlotWin(self, lambda: self._UrbanAreas.plotCompareQuality(qol, urb_area))
                sbqol_plt.transient()

    def search_qol(self):
        """
        Method that is called when the user wants to search the quality of life metrics for one urban area. A
        SingClickWin object is created where the user can choose an urban area to look at. Then, a QolForOneUAWin object
        is created.
        """
        ua_list = self._UrbanAreas.getUrbanAreas()
        sqol_win = SingClickWin(self, ua_list)
        self.wait_window(sqol_win)
        ua = sqol_win.get_choice()
        if ua:  # if user closes window without choosing anything
            choice_win = QolForOneUAWin(self, ua)
            self.wait_window(choice_win)

    def distance_ua(self):
        """
        Method that is called when the user wants to find the distance between urban areas. A DistanceUAWin object is
        created in order for this to happen.
        """
        win = DistanceUAWin(self)
        win.transient()

    def on_closing(self):
        """
        A message window pops up asking if the user would like to quit. If they click 'OK', the main window is closed
        and the program will terminate successfully.
        """
        if tkmb.askokcancel("Quit", "Are you sure you want to quit?"):
            self.quit()
            self.destroy()


if __name__ == '__main__':
    app = MainWin()  # Creates a Main Window object
    app.mainloop()  # Runs the Main Window


