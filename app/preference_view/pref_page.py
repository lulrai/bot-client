""" Preference page for the application. """
import os
import shutil
import time
import logging

import customtkinter
from customtkinter import CTkCanvas

from app.preference_view.pref_view import PreferenceView
from app.common_view.popups import Popups
from app.common_view.widget_utils import init_placeholder
from backend.common.config import GameConfig, AppConfig

class PrefPage():
    """ Preference page for client preference editing and saving."""
    PARENT_WINDOW_WIDTH = 780
    PARENT_WINDOW_HEIGHT = 520
    CONFIRM_WIDTH = 360
    CONFIRM_HEIGHT = 100

    def __init__(self, parent_frame: customtkinter.CTkFrame, game_config: GameConfig, app_config: AppConfig, parent_x: int, parent_y: int):
        """
        Initialize the preference page.

        Parameters
        ----------
        parent_frame : customtkinter.CTkFrame
            The parent frame of the preference page.
        game_config : GameConfig
            The game config object.
        parent_x : int
            The x coordinate of the parent frame.
        parent_y : int
            The y coordinate of the parent frame.
        """
        self.__parent_frame = parent_frame # parent frame
        self.__game_config = game_config # game config object
        self.__app_config = app_config # application config object
        self.config_changes = {} # dictionary of changes to the config file
        self.__preferences_ini = game_config.pref_ini # preference file
        self.__preferences_path: str = game_config.lotro_pref_path # path to the preferences file

        self.__search_string = '' # search string for searching through config file
        self.__search_locs = [] # list of found locations of search string
        self.__temp_search_locs = [] # copy of search_locs

        self.__current_frame_height = 0 # current height of the canvas
        self.__pref_view_list = [] # list of preference views (each preference view is a setting type)

        self.__create_search_bar() # create the search bar (search box, label and button)
        self.__create_pref_frame() # create the frame for the canvas
        self.__create_canvas() # create the canvas
        self.__create_pref_list() # create the preference list

    def __create_search_bar(self):
        """ Create the search bar. """
        if self.__game_config.debug: # if debug mode is on
            logging.debug('\tCreating search bar.')

        # create the search bar frame to hold the search bar, search button and save label
        self.search_bar = customtkinter.CTkFrame(master=self.__parent_frame, fg_color=None)
        self.search_bar.grid_rowconfigure(0, weight=1)
        self.search_bar.grid_columnconfigure(0, weight=12)
        self.search_bar.grid_columnconfigure(1, weight=1)
        # self.search_bar.grid_columnconfigure(2, weight=1)

        # create the search bar label
        # self.search_label = customtkinter.CTkLabel(master=self.search_bar,
        #                                            text="Search:",
        #                                            font=("Roboto Medium", 16))
        # self.search_label.grid(row=0, column=0, padx=(10, 2), pady=5, sticky="nsw")

        # create the search bar entry
        self.search_str = customtkinter.StringVar()
        self.search_entry = customtkinter.CTkEntry(master=self.search_bar, placeholder_text="Search preferences", textvariable=self.search_str)
        init_placeholder(self.search_entry, "Find preferences")
        self.search_entry.bind('<Return>', self.__search_parser) # bind the search parser to the search entry to parse the search string
        self.search_entry.grid(row=0, column=0, padx=(10, 10), pady=5, sticky="nsew")

        # create the save button to save changes to the preferences file
        self.save_button = customtkinter.CTkButton(master=self.search_bar, width=90, state="disabled", text="Save All", 
                                                   command=lambda: Popups.two_button_popup(self.__parent_frame,
                                                       (PrefPage.PARENT_WINDOW_WIDTH, PrefPage.PARENT_WINDOW_HEIGHT),
                                                       (PrefPage.CONFIRM_WIDTH, PrefPage.CONFIRM_HEIGHT),
                                                       "Are you sure?",
                                                       "Warning: Do not save unless you know what you're doing",
                                                       "Save All", "Cancel", popup_desc_color="#FF9632",
                                                       first_button_command=self.__save_preference,
                                                       second_button_text_color="#A52A2A"
                                                   ))
        self.save_button.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="nsew")

    def __create_pref_frame(self):
        """ Create the frame for the canvas. """
        if self.__game_config.debug: # if debug mode is on
            logging.debug('\tCreating preference frame.')
        self.canvas_frame = customtkinter.CTkFrame(master=self.__parent_frame)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_propagate(False)

    def __create_canvas(self):
        """ Create the overall canvas. """
        if self.__game_config.debug: # if debug mode is on
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
        self.canvas_frame.configure(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
        # set the bounds of the canvas for scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
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
        self.canvas_frame.configure(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
        # set the bounds of the canvas for scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
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
        # check if the search string is not the same as the last search string
        if self.search_str.get().lower() != self.__search_string:
            self.__search_locs = [] # reset the search locations
            self.__search_string = self.search_str.get().lower() # retrieve the search string
            
            self.__current_frame_height = 0 # reset the current frame height
            # for each preference view, search for the search string
            for pref_view in self.__pref_view_list:
                item_num = 0 # reset the item number
                for item_id in pref_view.find_all():
                    tag_name = pref_view.itemcget(item_id, "tags") # get the tag name of the item
                    if self.__search_string in tag_name and tag_name.endswith("_left"): # if the search string is in the tag name and the tag name ends with _left
                        location = self.__current_frame_height+34+(30*item_num)
                        item = (pref_view, item_id, location) # create a tuple of the preference view, item id, and location
                        self.__search_locs.append(item) # add the current frame height to the search locations
                    elif tag_name.endswith("_left"): # if the tag name ends with _left but the search string is not in the tag name
                        item_num += 1 # increment the item number
                self.__current_frame_height += pref_view.winfo_reqheight() # add the preference view height to the current frame height

        # if search_string is empty, reset the view
        if not self.__search_string or not self.__search_locs:
            if self.__search_locs:
                prev_item = self.__search_locs[-1] # get the last item in the search locations
                prev_item[0].itemconfigure(prev_item[1], fill="#ffffff") # set the item color to yellow
            self.canvas.yview_moveto(self.origY) # move the canvas to the original y position
        else:
            current_item = self.__search_locs[0] # get the first item in the search locations
            current_item[0].itemconfigure(current_item[1], fill="yellow") # set the item color to yellow
            
            # if there is a previous item, set the color back to white
            if len(self.__search_locs) > 1:
                prev_item = self.__search_locs[-1] # get the last item in the search locations
                prev_item[0].itemconfigure(prev_item[1], fill="#ffffff") # set the item color to yellow

            self.canvas.yview_moveto(current_item[2]/self.__current_frame_height if self.__current_frame_height else 0) # move the canvas to the next found location
            self.__search_locs.append(self.__search_locs.pop(0)) # move the first search location to the end of the list

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
        self.canvas.configure(scrollregion=f'0 0 {size[0]} {size[1]}')
        if self.list_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.configure(width = self.list_frame.winfo_reqwidth())
        if self.list_frame.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canvas.configure(height = self.list_frame.winfo_reqheight())

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
                if file_count >= self.__app_config.get_config('pref', 'backup_count'): # if there are more than 30 backup files
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
        if self.save_button.cget('state') == customtkinter.NORMAL:
            self.save_button.configure(state=customtkinter.DISABLED)
