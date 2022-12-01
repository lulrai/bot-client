""" Preference page for the application. """
import os
import shutil
import time
import logging

import customtkinter
from customtkinter import CTkCanvas

from app.preference_view.pref_view import PreferenceView
from app.common_view.popups import Popups
from backend.common.config import Config

class PrefPage():
    """ Preference page for client preference editing and saving."""
    PARENT_WINDOW_WIDTH = 780
    PARENT_WINDOW_HEIGHT = 520
    CONFIRM_WIDTH = 360
    CONFIRM_HEIGHT = 100

    def __init__(self, parent_frame: customtkinter.CTkFrame, config: Config, parent_x, parent_y):
        """
        Initialize the preference page.
        
        Parameters
        ----------
        parent_frame : customtkinter.CTkFrame
            The parent frame of the preference page.
        config : Config
            The config object.
        parent_x : int
            The x coordinate of the parent frame.
        parent_y : int
            The y coordinate of the parent frame.
            
        Returns
        -------
        None
        """
        self.__parent_frame = parent_frame # parent frame
        self.__config = config # config object
        self.config_changes = {} # dictionary of changes to the config file
        self.__preferences_ini = config.pref_ini # preference file
        self.__preferences_path: str = config.lotro_pref_path # path to the preferences file

        self.__search_string = '' # search string for searching through config file
        self.__search_locs = [] # list of found locations of search string
        self.__temp_search_locs = [] # copy of search_locs

        self.__current_frame_height = 0 # current height of the canvas
        self.__pref_view_list = [] # list of preference views (each preference view is a setting type)

        self.__parent_x = parent_x # x coordinate of the parent frame
        self.__parent_y = parent_y # y coordinate of the parent frame

        self.__create_search_bar() # create the search bar (search box, label and button)
        self.__create_pref_frame() # create the frame for the canvas
        self.__create_canvas() # create the canvas
        self.__create_pref_list() # create the preference list

    def __create_search_bar(self):
        """ Create the search bar. """
        if self.__config.debug: # if debug mode is on
            logging.debug('\tCreating search bar.')
            
        # create the search bar frame to hold the search bar, search button and save label
        self.search_bar = customtkinter.CTkFrame(master=self.__parent_frame, fg_color=None)

        # create the search bar label
        self.search_label = customtkinter.CTkLabel(master=self.search_bar, text="Find: ")
        self.search_label.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="e", padx=5, pady=5)

        # create the search bar entry
        self.search_str = customtkinter.StringVar()
        self.search_entry = customtkinter.CTkEntry(master=self.search_bar, width=270, placeholder_text="Search preferences", textvariable=self.search_str)
        self.search_entry.bind('<Return>', self.__search_parser) # bind the search parser to the search entry to parse the search string
        self.search_entry.grid(row=0, column=1, columnspan=1, rowspan=1, sticky="w", padx=5, pady=5)

        # create the save button to save changes to the preferences file
        self.save_button = customtkinter.CTkButton(master=self.search_bar, width=90, state="disabled", text="Save All", 
                                                   command=lambda: Popups.two_button_popup(
                                                       self.__parent_frame, (self.__parent_x, self.__parent_y),
                                                       (PrefPage.PARENT_WINDOW_WIDTH, PrefPage.PARENT_WINDOW_HEIGHT),
                                                       (PrefPage.CONFIRM_WIDTH, PrefPage.CONFIRM_HEIGHT),
                                                       "Are you sure?",
                                                       "Warning: Do not save unless you know what you're doing",
                                                       "Save All", "Cancel", popup_desc_color="#FF9632", first_button_command=self.__save_preference,
                                                       second_button_text_color="#A52A2A", second_button_hover_color="#731d1d"
                                                   ))
        self.save_button.grid(row=0, column=2, padx=20, pady=5)

    def __create_pref_frame(self):
        """ Create the frame for the canvas. """
        if self.__config.debug: # if debug mode is on
            logging.debug('\tCreating preference frame.')
        self.canvas_frame = customtkinter.CTkFrame(master=self.__parent_frame)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_propagate(False)

    def __create_canvas(self):
        """ Create the overall canvas. """
        if self.__config.debug: # if debug mode is on
            logging.debug('\tCreating general canvas.')
        
        # create the canvas
        self.canvas = CTkCanvas(master=self.canvas_frame, highlightthickness=0, bd=-2, bg='#2a2d2e')

        # move the canvas to the top
        self.origY = self.canvas.yview()[0]

        # create the scroll bar and bind it to the canvas
        vsb = customtkinter.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.canvas.yview)
        vsb.grid(row=0, column=1, sticky='nse')
        self.canvas.configure(yscrollcommand=vsb.set)
    
    def __create_pref_list(self):
        """ Create the preference list. """
        # create the frame to hold the preference list   
        self.list_frame = customtkinter.CTkFrame(self.canvas)

        # bind certain actions to the list frame
        self.list_frame.bind('<Configure>', self.__configure_window)
        self.list_frame.bind('<Enter>', self.__bound_to_mousewheel)
        self.list_frame.bind('<Leave>', self.__unbound_to_mousewheel)
        self.list_frame.columnconfigure(0, weight=1)

        # for each setting type in the config file, create a preference view
        row_num = 0
        for key, value in self.__preferences_ini.items():
            if list(value.keys()): # if the setting type has settings
                pref_view = PreferenceView(parent=self.list_frame, save_button=self.save_button, name=key, items=value, config_changes=self.config_changes)
                pref_view.grid(row=row_num, column=0, columnspan=2, rowspan=1, sticky='nw')
                self.__pref_view_list.append(pref_view)
                row_num += 1

        # resize the canvas to fit the preference list (IMPORTANT)
        self.canvas_frame.config(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
        # set the bounds of the canvas for scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        # add the list frame to the canvas
        self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        # add the canvas to the canvas frame
        self.canvas.grid(row=0, column=0, sticky="news")
        # add the canvas frame to the parent frame
        self.canvas_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky='nw')

    def hide_pref_page(self):
        """
        Hide the preference page.
        """
        #for each preference view, hide it
        for pref_view in self.__pref_view_list:
            # hide a tkinter canvas
            pref_view.grid_forget()
        # hide the search bar
        self.search_bar.grid_forget()
        # hide the canvas
        self.canvas.grid_forget()
        # hide the canvas frame
        self.canvas_frame.grid_forget()

    def show_pref_page(self):
        """
        Show the preference page.
        """
        # show the search bar
        self.search_bar.grid(row=0, column=0, columnspan=2, rowspan=1, pady=10, sticky="nsew")
        # show the canvas frame
        self.canvas_frame.grid_propagate(False)
        # bind important actions to the canvas frame
        self.list_frame.bind('<Configure>', self.__configure_window)
        self.list_frame.bind('<Enter>', self.__bound_to_mousewheel)
        self.list_frame.bind('<Leave>', self.__unbound_to_mousewheel)
        # for each preference view, show it
        for row_num, pref_view in enumerate(self.__pref_view_list):
            # show a tkinter canvas
            pref_view.grid(row=row_num, column=0, columnspan=2, rowspan=1, sticky='nw')
        # resize the canvas to fit the preference list (IMPORTANT)
        self.canvas_frame.config(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
        # set the bounds of the canvas for scroll region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        # add the list frame to the canvas
        self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        # add the canvas to the canvas frame
        self.canvas.grid(row=0, column=0, sticky="news")
        # add the canvas frame to the parent frame
        self.canvas_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky='nw')

    def __search_parser(self, _):
        """
        Parse the search bar input.

        Parameters
        ----------
        _ : Any
            The event that triggered the function.
        """
        # check if the search string is the same as the last search string
        if self.search_str.get().lower() == self.__search_string:
            if not self.__temp_search_locs: # if there are no temporary search locations, reset the locations using the original search locations
                self.__temp_search_locs = list(self.__search_locs)
            self.canvas.yview_moveto(self.__temp_search_locs.pop(0)/self.__current_frame_height if self.__current_frame_height else 0) # move the canvas to the next found location
            return

        # reset the search locations
        self.__search_locs = []
        self.__temp_search_locs = []
        # retrieve the search string
        self.__search_string = self.search_str.get().lower()

        # for each preference view, search for the search string
        if self.__search_string:
            self.list_frame.bind('<Configure>', self.__configure_window) # bind the configure window function to the list frame
            self.list_frame.bind('<Enter>', self.__bound_to_mousewheel) # bind the bound to mousewheel function to the list frame
            self.list_frame.bind('<Leave>', self.__unbound_to_mousewheel) # bind the unbound to mousewheel function to the list frame
            
            self.list_frame.rowconfigure(0, weight=1) # configure the row to be weight 1
            
            self.__current_frame_height = 0 # set the current frame height to 0
            for pref_view in self.__pref_view_list: # for each preference view
                for item_num, item_id in enumerate(pref_view.find_all(), start=1): # for each item in the preference view
                    tag_name = pref_view.itemcget(item_id, "tags") # get the tag name of the item
                    if self.__search_string in tag_name and tag_name.endswith("_left"): # if the search string is in the tag name and the tag name ends with _left
                        pref_view.itemconfigure(item_id, fill="yellow") # set the item color to yellow
                        self.__search_locs.append(self.__current_frame_height + (item_num-2)*16) # add the current frame height to the search locations
                    elif tag_name.endswith("_left"): # if the tag name ends with _left but the search string is not in the tag name
                        pref_view.itemconfigure(item_id, fill="#ffffff") # set the item color to white
                self.__current_frame_height += pref_view.winfo_reqheight() # add the preference view height to the current frame height

            self.canvas.yview_moveto(0 if not self.__current_frame_height else self.__search_locs[0]/self.__current_frame_height) # move the canvas to the first found location

            # resize the canvas to fit the preference list (IMPORTANT)
            self.canvas_frame.config(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
            # set the bounds of the canvas for scroll region
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            # add the list frame to the canvas
            self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
            # add the canvas to the canvas frame
            self.canvas.grid(row=0, column=0, sticky="news")
            # add the canvas frame to the parent frame
            self.canvas_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky='nw')
        else: # if the search string is empty
            for pref_view in self.__pref_view_list: # for each preference view
                for item_num, item_id in enumerate(pref_view.find_all()): # for each item in the preference view
                    tag_name = pref_view.itemcget(item_id, "tags") # get the tag name of the item
                    if self.__search_string in tag_name and tag_name.endswith("_left"): # if the search string is in the tag name and the tag name ends with _left
                        pref_view.itemconfigure(item_id, fill="#ffffff") # set the item color to white
            self.canvas.yview_moveto(self.origY) # move the canvas to the original y position

    def __unbound_to_mousewheel(self, _):
        """ Unbind the mousewheel to the canvas """
        self.canvas.unbind_all("<MouseWheel>")

    def __on_mousewheel(self, event):
        """ Scroll the canvas with the mouse wheel with certain sensitivity. """
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def __bound_to_mousewheel(self, _):
        """ Bind the mousewheel to the canvas to scroll the canvas. """
        self.canvas.bind_all("<MouseWheel>", self.__on_mousewheel)

    def __configure_window(self, _):
        """ Configure the window to update the scroll region and dimension. """
        # update the scrollbars to match the size of the inner frame
        size = (self.list_frame.winfo_reqwidth(), self.list_frame.winfo_reqheight())
        self.canvas.config(scrollregion=f'0 0 {size[0]} {size[1]}')
        if self.list_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width = self.list_frame.winfo_reqwidth())
        if self.list_frame.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canvas.config(height = self.list_frame.winfo_reqheight())

    def __save_preference(self, popup: customtkinter.CTkToplevel):
        """
        Save the preference to the config file.
        
        Parameters
        ----------
        popup : customtkinter.CTkToplevel
            The popup window that contains the preference.
        """
        popup.destroy() # destroy the popup
        try:
            src_fpath = self.__preferences_path # get the source file path
            dest_fpath, file_name = os.path.split(os.path.abspath(src_fpath)) # get the destination file path
            current_time = time.time() # get the current time
            # create a backup file name
            file_name = file_name.replace('.ini', f'{time.strftime("%Y%m%d_%H%M%S", time.localtime(current_time))}_bak.ini')

            # get backup directory path
            dest_fpath = os.path.join(dest_fpath, 'backup')
            # if the backup directory exists, remove the old backup files
            if os.path.isdir(dest_fpath):
                file_count = len([f for f in os.listdir(dest_fpath) if f.endswith('.ini') and os.path.isfile(os.path.join(dest_fpath, f))])
                if file_count >= 30: # if there are more than 30 backup files
                    oldest_file = sorted(os.listdir(dest_fpath), key=lambda x: os.path.getctime(os.path.join(dest_fpath,x)))[0]
                    os.remove(os.path.join(dest_fpath, oldest_file)) # remove the oldest file

            # create the backup directory if it doesn't exist
            dest_fpath = os.path.join(dest_fpath, file_name)
            # copy the current config file to the backup directory
            os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
            shutil.copy(src_fpath, dest_fpath)
        except OSError as os_error: # if there is an error
            logging.exception("Failed to backup the config file.")
            logging.exception(os_error)

        # update the config file changes
        for section, section_items in self.config_changes.items():
            for option, value in section_items.items():
                self.__preferences_ini.set(section, option, value)

        # save the config file
        with open(src_fpath, 'w', encoding='utf-8') as configfile:
            self.__preferences_ini.write(configfile, space_around_delimiters=False)

        # reset all the fields to their default values
        for pref_view in self.__pref_view_list:
            pref_view.clear_fields()
        # disable the save button
        if self.save_button.state == customtkinter.NORMAL:
            self.save_button.configure(state=customtkinter.DISABLED)
