import seaborn as sns
import threading
import os
import fastf1
import customtkinter as ctk
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
class F1App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.database = {}
        self.cache_dir = './f1_cache'
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        fastf1.Cache.enable_cache(self.cache_dir)
        print("Cache successfully enabled!" )
        self.session_object=None    #The session we are currently looking at
        self.results = None  #the results of the session
        self.key = None   #key of the session stored in hash table
        self.year=None   #entry box that allows user to enter year of race they want to choose
        self.race=None   #entry box that allows user to enter name of race they want to choose
        self.choose_driver=None   #first driver chosen
        self.choose_driver2=None #second driver chosen
        self.main_frame = None #frame that holds inputs for user to enter drivers they want to compare 
        self.click_button=None #button that user clicks to direct to main_frame
        self.frame1 = None #frame that holds the information about the driver at the first position the user has chosen
        self.frame2 = None #frame that holds the information about the driver at the second position the user has chosen
        self.race_year=None  #year user has chosen
        self.race_wanted=None #race user has chosen
        self.all_details_needed=None  #dataset used for graphs
        self.graph_frame=None #frame that stores the Sector 1 Times Graph
        self.driver1_abbreviation=None #stores abbreviation of first driver
        self.driver2_abbreviation=None #stores abbreviation of second driver
        self.graph_frame2=None  #frame that stores the Sector 1 Times Graph
        self.graph_frame3=None  #frame that stores the Sector 2 Times Graph
        self.graph_frame4=None  #frame that stores the Sector 3 Times Graph
        self.graph_frame5=None  #frame that stores the Lap Times Graph
        self.graph_frame6=None  #frame that stores the Lap Speeds Graph
        self.telemetry2=None  #telemetry of first driver
        self.telemetry=None #telemetry of second driver
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.list_of_abbreviations=[]  #array that stores abbreviations of first drivers chosen
        self.list_of_abbreviations2 = [] #array that stores abbreviations of second drivers chosen
        self.i=0 #this variable is used to update the position of the most recent item added to list_of_abbreviations
        self.j=0 #this variable is used to update the position of the most recent item added to list_of_abbreviations2
        self.choose_a_race() #process automatically runs when an object is made
    def choose_a_race(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        new_frame = ctk.CTkFrame(self)
        self.year = ctk.CTkEntry(new_frame, placeholder_text="Please choose a year: ")
        self.race = ctk.CTkEntry(new_frame, placeholder_text="Please choose a race: ")
        self.click_button = ctk.CTkButton(new_frame, text="Find race", command=lambda: self.start_loading())
        new_frame.grid(row=0, column=0, rowspan=3, columnspan=2, padx=20, pady=20, sticky="nsew")
        new_frame.grid_rowconfigure((0,1,2,3), weight=1)
        new_frame.grid_columnconfigure(0, weight=1)
        self.year.grid(row=0, column=0, columnspan=2, padx=50, pady=30, sticky="ew")
        self.race.grid(row=1, column=0, columnspan=2, padx=50, pady=30, sticky="ew")
        self.click_button.grid(row=2, column=0, columnspan=2, padx=50, pady=30, sticky="ew")

    def start_loading(self):
        self.click_button.configure(text="Loading... Please Wait", state="disabled")
        self.update_idletasks()
        loading_thread = threading.Thread(target=self.check_data)
        loading_thread.daemon = False
        loading_thread.start()
    def check_data(self):
        try:
            self.race_year = int(self.year.get())
            self.race_wanted = self.race.get()
            self.session = fastf1.get_session(self.race_year,self.race_wanted, 'R')
            self.session.load(telemetry=True, weather=False, messages=False)
            self.key = str(self.race_year) + self.race_wanted
            self.database[self.key] = self.session
            self.session_object = self.database[self.key]
            self.results = self.session_object.results
            if self.winfo_exists():
                self.after(0, lambda: self.load_dates())
        except ValueError:
            if self.click_button.winfo_exists():
                self.temporary_message("Please enter a valid year and race")
                self.click_button.configure(text="Find race", state="normal")
    def temporary_message(self,message):
        error_message = ctk.CTkLabel(self, text=message)
        error_message.grid(row=3, column=0)
        self.after(5000, error_message.destroy)
    def check_if_valid(self,value):
        try:
            value1 = int(self.choose_driver.get())
            value2 = int(self.choose_driver2.get())
            if value1 != value2:
                if value==str(value1):
                    self.add_to_list1(value1)
                else:
                    self.add_to_list2(value2)
            else:
                self.temporary_message("Please enter different numbers")
        except ValueError:
            self.temporary_message("Please enter a valid number")
    def load_dates(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.main_frame = ctk.CTkFrame(self)
        self.choose_driver = ctk.CTkEntry(self.main_frame, placeholder_text="Please choose a position: ")
        self.choose_driver2 = ctk.CTkEntry(self.main_frame, placeholder_text="Please choose a second position: ")
        choose_another_race = ctk.CTkButton(self.main_frame, text="Choose another race", command=self.choose_a_race)
        self.frame1 = ctk.CTkFrame(self.main_frame)
        self.frame2 = ctk.CTkFrame(self.main_frame)
        button = ctk.CTkButton(self.main_frame, text="Get driver information",
                               command=lambda: self.check_if_valid(self.choose_driver.get()))
        button2 = ctk.CTkButton(self.main_frame, text="Get 2nd driver information",
                                command=lambda: self.check_if_valid(self.choose_driver2.get()))
        self.main_frame.rowconfigure((0,1,2,3,4,5,6,7), weight=1)
        self.main_frame.columnconfigure((0, 1), weight=1)
        self.choose_driver.grid(row=0, column=0,padx=20,pady=20,sticky="ew")
        self.choose_driver2.grid(row=0, column=1,padx=20,pady=20,sticky="ew")
        button.grid(row=1, column=0,padx=20,pady=20,sticky="ew")
        button2.grid(row=1, column=1,padx=20,pady=20,sticky="ew")
        self.frame1.grid(row=2, column=0,padx=20,pady=20,sticky="nsew")
        self.frame2.grid(row=2, column=1,padx=20,pady=20,sticky="nsew")
        choose_another_race.grid(row=7, column=0, rowspan=1,padx=20,pady=20,sticky="ew")

        self.main_frame.grid(row=0, column=0,padx=20,pady=20,sticky="nsew")

    def check_driver(self,input1,frame):
        try:
            driver_position = int(input1)
            if driver_position > 0:
                data = self.results.iloc[driver_position - 1]
                for widget in frame.winfo_children():
                    if widget.winfo_exists():
                        widget.destroy()
                all_laps = self.session_object.laps
                fastest_lapp = all_laps.pick_driver(data["Abbreviation"])
                lap = fastest_lapp.pick_fastest()
                clean_results = f"Driver: {data['FullName']}\nNumber: {data['DriverNumber']}\nTeam: {data['TeamName']}\nPoints: {data['Points']}"
                driver_results = ctk.CTkLabel(frame, text=clean_results)
                driver_results.grid(row=3, column=0,padx=20,pady=20,sticky="ew")
                lap_time = f"Their fastest lap was {lap['LapTime']}"
                which_lap = f"This happened on lap {lap['LapNumber']}"
                fastest_lap_time = ctk.CTkLabel(frame, text=lap_time)
                lap_it_happened = ctk.CTkLabel(frame, text=which_lap)
                fastest_lap_time.grid(row=4, column=0,padx=20,pady=20,sticky="ew")
                lap_it_happened.grid(row=5, column=0,padx=20,pady=20,sticky="ew")
                fastest_lap_in_session = all_laps.pick_fastest()
                driver = fastest_lap_in_session['Driver']
                position = str(fastest_lap_in_session['LapTime']).replace("0 days", "")
                if data['Abbreviation'] == driver:
                    message = f"This driver had the fastest lap of the race"
                    show_message = ctk.CTkLabel(frame, text=message)
                    show_message.grid(row=6, column=0,padx=20,pady=20,sticky="ew")
                else:
                    message = f"Fastest lap of the race was by{driver}"
                    fast_lap = f"Their fastest lap time was {position}"
                    show_message = ctk.CTkLabel(frame, text=message)
                    show_message2 = ctk.CTkLabel(frame, text=fast_lap)
                    show_message.grid(row=7, column=0,padx=20,pady=20,sticky="ew")
                    show_message2.grid(row=8, column=0,padx=20,pady=20,sticky="ew")
                self.view_graphs = ctk.CTkButton(self.main_frame, text="View graphs", command=lambda: self.load_graphs_thread())
                self.view_graphs.grid(row=7, column=1,padx=20,pady=20,sticky="ew")
                abbreviation=data["Abbreviation"]
                return abbreviation
            else:
                app.after(self.temporary_message("Please re-enter a driver"))

        except ValueError:
            app.after(self.temporary_message("Please enter a number"))

    def add_to_list1(self,value):
        checks=self.check_driver(value,self.frame1)  #add checks to array list_of_abbreviations
        self.list_of_abbreviations.append(checks)
        self.i+=1
    def add_to_list2(self,value):
        checks=self.check_driver(value,self.frame2)   #add checks to array list_of_abbreviations2
        self.list_of_abbreviations2.append(checks)
        self.j+=1
    def load_graphs_thread(self):
        self.view_graphs.configure(text="Loading Graphs", state="disabled")  #change button to disabled while the graph is loading
        self.update_idletasks()
        loading_thread1 = threading.Thread(target=self.load_graph_data())
        loading_thread1.daemon = False
        loading_thread1.start()

    def load_graph_data(self):
            self.driver1_abbreviation=self.list_of_abbreviations[self.i-1]
            self.driver2_abbreviation = self.list_of_abbreviations2[self.j - 1]
            self.driver1 = self.session_object.laps.pick_driver(self.driver1_abbreviation)
            all_details_needed = self.driver1[['Driver','LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']].copy()
            all_details_needed['Sector1Seconds']=all_details_needed['Sector1Time'].dt.total_seconds()  #convert the times to seconds eg.00:01:27 becomes 87 
            all_details_needed['Sector2Seconds'] = all_details_needed['Sector2Time'].dt.total_seconds()
            all_details_needed['Sector3Seconds'] = all_details_needed['Sector3Time'].dt.total_seconds()
            all_details_needed['LapTimeSeconds']= all_details_needed['LapTime'].dt.total_seconds()
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.width', 1000)

            self.driver2 = self.session_object.laps.pick_driver(self.driver2_abbreviation)
            all_details_needed2 = self.driver2[['Driver','LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']].copy()
            all_details_needed2['Sector1Seconds'] = all_details_needed2['Sector1Time'].dt.total_seconds()
            all_details_needed2['Sector2Seconds'] = all_details_needed2['Sector2Time'].dt.total_seconds()
            all_details_needed2['Sector3Seconds'] = all_details_needed2['Sector3Time'].dt.total_seconds()
            all_details_needed2['LapTimeSeconds'] = all_details_needed2['LapTime'].dt.total_seconds()
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.width', 1000)
            self.combined_laps=pd.concat([all_details_needed, all_details_needed2], ignore_index=True)
            self.after(0,lambda: self.load_graphs())
    def load_graphs(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.graph_frame=ctk.CTkFrame(master=self)
        self.graph_frame.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame.columnconfigure((0), weight=1)
        self.graph_frame.grid(row=0, column=0, sticky="nsew")
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.x_label = "Lap Number"
        ax.y_label = "Sector1 Time in Seconds"
        sns.scatterplot(
            data=self.combined_laps,
            x="LapNumber",
            y="Sector1Seconds",
            hue='Driver',
            s=50,
            ax=ax)
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)    #convert the graph to a customtkinter widget
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_drivers=ctk.CTkButton(self.graph_frame, text="Back to Drivers",command= lambda:self.load_dates())
        go_back_to_drivers.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        go_to_Sector2_graph=ctk.CTkButton(self.graph_frame, text="Sector 2 Times",command= lambda:self.load_graph2())
        go_to_Sector2_graph.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    def load_graph2(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.graph_frame2 = ctk.CTkFrame(master=self)
        self.graph_frame2.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame2.columnconfigure((0), weight=1)
        self.graph_frame2.grid(row=0, column=0, sticky="nsew")
        fig2 = Figure(figsize=(5, 4), dpi=100)
        ax2 = fig2.add_subplot(111)
        ax2.x_label = "Lap Number"
        ax2.y_label = "Sector2 Time in Seconds"
        sns.scatterplot(
            data=self.combined_laps,
            x="LapNumber",
            y="Sector2Seconds",
            hue='Driver',
            s=50,
            ax=ax2)
        canvas = FigureCanvasTkAgg(fig2, master=self.graph_frame2)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_Sector1 = ctk.CTkButton(self.graph_frame2, text="Back to Sector1 times", command=lambda: self.load_graphs())
        go_back_to_Sector1.grid(row=1, column=0, padx=20,pady=20, sticky="nsew")
        go_to_Sector3_graph = ctk.CTkButton(self.graph_frame2, text="Sector 3 Times", command=lambda: self.load_graph3())
        go_to_Sector3_graph.grid(row=2, column=0, padx=20,pady=20,sticky="nsew")

    def load_graph3(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.graph_frame3 = ctk.CTkFrame(master=self)
        self.graph_frame3.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame3.columnconfigure((0), weight=1)
        self.graph_frame3.grid(row=0, column=0, sticky="nsew")
        fig3 = Figure(figsize=(5, 4), dpi=100)
        ax3 = fig3.add_subplot(111)
        ax3.x_label = "Lap Number"
        ax3.y_label = "Sector2 Time in Seconds"
        sns.scatterplot(
            data=self.combined_laps,
            x="LapNumber",
            y="Sector3Seconds",
            hue='Driver',
            s=50,
            ax=ax3)
        canvas = FigureCanvasTkAgg(fig3, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_Sector2 = ctk.CTkButton(self.graph_frame3, text="Back to Sector2 times",
                                           command=lambda: self.load_graph2())
        go_back_to_Sector2.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        go_to_next_graph = ctk.CTkButton(self.graph_frame3, text="Lap Times",
                                            command=lambda: self.load_next_graph())
        go_to_next_graph.grid(row=2, column=0, padx=20, pady=20 ,sticky="nsew")

    def load_next_graph(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.graph_frame4 = ctk.CTkFrame(master=self)
        self.graph_frame4.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame4.columnconfigure((0), weight=1)
        self.graph_frame4.grid(row=0, column=0, sticky="nsew")
        fig4 = Figure(figsize=(5, 4), dpi=100)
        ax4 = fig4.add_subplot(111)
        ax4.x_label = "Lap Number"
        ax4.y_label = "Sector2 Time in Seconds"
        sns.scatterplot(
            data=self.combined_laps,
            x="LapNumber",
            y="LapTimeSeconds",
            hue='Driver',
            s=50,
            ax=ax4)
        canvas = FigureCanvasTkAgg(fig4, master=self.graph_frame4)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_Sector3 = ctk.CTkButton(self.graph_frame4, text="Back to Sector3 times",
                                           command=lambda: self.load_graph3())
        go_back_to_Sector3.grid(row=1, column=0, padx=20, pady=20 ,sticky="nsew")
        go_to_next_graph = ctk.CTkButton(self.graph_frame4, text="Box Plots",
                                            command=lambda: self.load_box_plot())
        go_to_next_graph.grid(row=2, column=0, padx=20, pady=20 ,sticky="nsew")

    def load_box_plot(self):
        for frame in self.winfo_children():
            if frame.winfo_exists():
                frame.destroy()
        self.graph_frame5 = ctk.CTkFrame(master=self)
        self.graph_frame5.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame5.columnconfigure((0), weight=1)
        self.graph_frame5.grid(row=0, column=0, sticky="nsew")
        fig5 = Figure(figsize=(5, 4), dpi=100)
        ax5 = fig5.add_subplot(111)
        ax5.x_label = "Lap Number"
        ax5.y_label = "Sector2 Time in Seconds"
        sns.boxplot(
            data=self.combined_laps,
            x="Driver",
            y="LapTimeSeconds",
            hue='Driver',
            ax=ax5)
        canvas = FigureCanvasTkAgg(fig5, master=self.graph_frame5)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_next = ctk.CTkButton(self.graph_frame5, text="Back to Lap Times",
                                           command=lambda: self.load_next_graph())
        go_back_to_next.grid(row=1, column=0, padx=20, pady=20 ,sticky="nsew")
        go_to_nothing = ctk.CTkButton(self.graph_frame5, text="Telemetry of fastest lap",
                                         command=lambda: self.load_telemetry_of_fastest_lap())
        go_to_nothing.grid(row=2, column=0, padx=20, pady=20 ,sticky="nsew")

    def load_telemetry_of_fastest_lap(self):
        self.telemetry1=self.driver1.pick_fastest().get_telemetry()
        self.telemetry2 = self.driver2.pick_fastest().get_telemetry()
        self.telemetry1['Seconds']=self.telemetry1['Time'].dt.total_seconds()
        self.telemetry2['Seconds'] = self.telemetry2['Time'].dt.total_seconds()
        self.combined_telemetry = pd.concat([self.telemetry1, self.telemetry2], ignore_index=True)
        split_condition = (self.combined_telemetry['Seconds'] == 0).cumsum()
        self.combined_telemetry['Driver'] = np.where(split_condition == 1, self.driver1_abbreviation,self.driver2_abbreviation)
        self.graph_frame6 = ctk.CTkFrame(master=self)
        self.graph_frame6.rowconfigure((0, 1, 2), weight=1)
        self.graph_frame6.columnconfigure((0), weight=1)
        self.graph_frame6.grid(row=0, column=0, sticky="nsew")
        fig6 = Figure(figsize=(5, 4), dpi=100)
        ax6 = fig6.add_subplot(111)
        ax6.x_label = "Lap Number"
        ax6.y_label = "Sector2 Time in Seconds"
        sns.lineplot(data=self.combined_telemetry,x="Seconds",y="Speed",hue="Driver",ax=ax6)
        canvas = FigureCanvasTkAgg(fig6, master=self.graph_frame6)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        go_back_to_box = ctk.CTkButton(self.graph_frame6, text="Back to Box Plots",
                                        command= lambda: self.load_box_plot())
        go_back_to_box.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        go_to_drivers = ctk.CTkButton(self.graph_frame6, text="Go back to Drivers",
                                      command=lambda: self.load_dates())
        go_to_drivers.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")





app=F1App()
app.mainloop()
