""" Individual section of the config file. """
from __future__ import annotations

from typing import TYPE_CHECKING
import customtkinter
from settings import ConstSettings
from app.common_view.widget_utils import init_placeholder

if TYPE_CHECKING:
    from configparser import SectionProxy

class PreferenceView(customtkinter.CTkCanvas):
    """ Preference view displaying individual sections of the config file. """
    WINDOW_WIDTH = 780 # width of the window

    def __init__(self, parent: customtkinter.CTkFrame, save_button: customtkinter.CTkButton, name: str, items: SectionProxy, config_changes: dict):
        """
        Initialize the preference view.

        Parameters
        ----------
        parent : customtkinter.CTkFrame
            The parent frame.
        save_button : customtkinter.CTkButton
            The save button.
        name : str
            The name of the section.
        items : SectionProxy
            The items in the section.
        config_changes : dict
            The changes to the config file.

        Returns
        -------
        None
        """
        # initialize the canvas
        super().__init__(master=parent, width=560, highlightthickness=0, bg='#2a2d2e')
        self.__items = items # the items in the section
        self.__name = name # the name of the section
        self.__var_info = {} # the variable info

        self.save_button = save_button # the save button
        self.config_changes = config_changes # the changes to the config file

        # setup the grid and make the canvas expandable
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(True)
        
        # write the section name as a text
        self.create_text(560//2, 16, anchor="center", text=f"{name} Preference", font=("Roboto Medium", 16), fill="#ffffff", tags=name)
        _, title_y0, _, title_y1 = self.bbox(name) # get the y coordinates of the title text
        margin_title = 5 # the margin between the title and the rectangle
        # create a rectangle around the title
        self.create_rectangle((0, title_y0-margin_title), (560, title_y1+margin_title), fill='gray45', tags=f'{name}_rect')
        _, _, _, rect_y1 = self.bbox(f'{name}_rect') # get the y coordinates of the rectangle
        self.lift(name, f'{name}_rect') # lift the title text above the rectangle

        margin_item = 15 # the margin between each row
        retrieve_changes_func = parent.register(self.__retrieve_changes) # register the function to retrieve the changes
        for idx, item in enumerate(self.__items.keys()):
            # create a label for the item
            self.create_text(560//3.5, rect_y1+margin_item+idx*30, anchor="center", text=item, font=("Roboto Medium", 10), fill="#ffffff", tags=f'{item}_left')

            # create an entry box for the item
            self.__var_info[item] = {} # initialize the variable info
            self.__var_info[item]['isbool'] = (self.__items[item].lower() in ("true", "false")) # check if the item is a boolean
            self.__var_info[item]['isnum'] = self.__items[item].replace('.','').isdigit() # check if the item is a number
            self.__var_info[item]['entry'] = customtkinter.CTkEntry(master=self, width=225, # create the entry box
                    validate="focusout", # validate the entry box when it loses focus
                    placeholder_text_color="grey40",
                    placeholder_text=self.__items[item], # set the placeholder to the value of the item
                    validatecommand=(retrieve_changes_func, '%P', self.__name, item)) # call the function to retrieve the changes
            # set the entry box's placeholder to the value of the item
            init_placeholder(self.__var_info[item]['entry'], self.__items[item])
            # bind the entry box to the canvas
            self.create_window(560-20, rect_y1+margin_item+idx*30, anchor="e", window=self.__var_info[item]['entry'], tags=f'{item}_right')
        # set the canvas's height to the items within it
        self.configure(height=len(self.__items.keys())*30+rect_y1)

    def __retrieve_changes(self, changed_val: str, main_key: str, sub_key: str) -> bool:
        """
        Retrieve the changes made to the entry box.

        Parameters
        ----------
        main_key : str
            The main key of the config file.
        sub_key : str
            The sub key of the config file.

        Returns
        -------
        bool
            True if the changes are valid, False otherwise.
        """
        # if the value is changed
        if changed_val:
            if main_key not in self.config_changes: # if the main key is not in the config changes
                self.config_changes[main_key] = {} # initialize the main key
                
            if self.__var_info[sub_key]['isbool']: # if the item type is a boolean
                if changed_val.lower() in ("true", "false"): # if the value is a boolean, update the config value to the boolean value
                    self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.CHANGED_ENTRY_BORDER_COLOR) # set the entry box's highlight to green
                    self.config_changes[main_key][sub_key] = changed_val # update the config changes
                    if self.save_button.cget('state') == customtkinter.DISABLED: # if the save button is disabled, enable it
                        self.save_button.configure(state=customtkinter.NORMAL)
                else: # if the value is not a boolean, highlight the entry box in red and set the value to the original value
                    self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.INVALID_ENTRY_BORDER_COLOR) # set the entry box's highlight to red
                    self.__var_info[sub_key]['entry'].delete(0, customtkinter.END)
            elif self.__var_info[sub_key]['isnum']: # if the item type is a number
                if changed_val.replace('.','',1).isdigit(): # if the value is a number, update the config value to the number value
                    self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.CHANGED_ENTRY_BORDER_COLOR) # set the entry box's highlight to green
                    self.config_changes[main_key][sub_key] = changed_val # update the config changes
                    if self.save_button.cget('state') == customtkinter.DISABLED: # if the save button is disabled, enable it
                        self.save_button.configure(state=customtkinter.NORMAL)
                else: # if the value is not a number, highlight the entry box in red and set the value to the original value
                    self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.INVALID_ENTRY_BORDER_COLOR) # set the entry box's highlight to red
                    self.__var_info[sub_key]['entry'].delete(0, customtkinter.END)
            else: # if the item type is not a boolean or a number
                self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.CHANGED_ENTRY_BORDER_COLOR) # set the entry box's highlight to blue
                self.config_changes[main_key][sub_key] = changed_val # update the config changes
                if self.save_button.cget('state') == customtkinter.DISABLED: # if the save button is disabled, enable it
                    self.save_button.configure(state=customtkinter.NORMAL)
        if not changed_val and main_key in self.config_changes and sub_key in self.config_changes[main_key]: # if the value is not changed and the main key and sub key are in the config changes
            del self.config_changes[main_key][sub_key] # delete the sub key from the config changes
            self.__var_info[sub_key]['entry'].configure(border_color=ConstSettings.DEFAULT_ENTRY_BORDER_COLOR) # remove the entry box's highlight
            if not list(self.config_changes[main_key].keys()): # if the main key is not empty
                del self.config_changes[main_key] # delete the main key from the config changes
            if not list(self.config_changes.keys()): # if the config changes is empty
                if self.save_button.cget('state') == customtkinter.NORMAL: # if the save button is enabled, disable it
                    self.save_button.configure(state=customtkinter.DISABLED)
        return True

    def clear_fields(self):
        """
        Clear the entry boxes and reset the placeholders.
        """
        # loop through the entry boxes
        for item, sub_val in self.__var_info.items():
            # remove the highlight from the entry box
            sub_val['entry'].configure(border_color=ConstSettings.DEFAULT_ENTRY_BORDER_COLOR)
            # reset the entry box's placeholder to the value of the item
            init_placeholder(sub_val['entry'], self.__items[item])
