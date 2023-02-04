""" Module containing the settings page for the application """
import customtkinter

from backend.common.config import AppConfig

class SettingsPage():
    """ Settings page for the application """
    PARENT_WINDOW_WIDTH = 780
    PARENT_WINDOW_HEIGHT = 520
    CONFIRM_WIDTH = 360
    CONFIRM_HEIGHT = 100

    def __init__(self, parent_frame: customtkinter.CTkFrame, app_config: AppConfig, parent_x: int, parent_y: int) -> None:
        """
        Initialize the settings page

        Parameters
        ----------
        parent_frame : customtkinter.CTkFrame
            The parent frame of the settings page
        app_config : AppConfig
            The application config
        parent_x : int
            The x coordinate of the parent window
        parent_y : int
            The y coordinate of the parent window
        """
        self.__parent_frame = parent_frame # The parent frame of the settings page
        self.__app_config = app_config # The application config

        self.__parent_x = parent_x # The x coordinate of the parent window
        self.__parent_y = parent_y # The y coordinate of the parent window

        self.__tab_control = customtkinter.CTkTabview(self.__parent_frame) # The tab control

        self.__general_tab = self.__tab_control.add("General") # The general tab
        self.__create_general_tab() # Create the general tab
        self.__lotro_tab = self.__tab_control.add("LoTRO") # The lotro tab
        self.__create_lotro_tab() # Create the lotro tab
        self.__preference_tab = self.__tab_control.add("Preference") # The preference tab
        self.__create_preference_tab() # Create the preference tab
        self.__sync_tab = self.__tab_control.add("Sync") # The sync tab
        self.__create_sync_tab() # Create the sync tab

    def __create_general_tab(self) -> None:
        """
        Create the general tab
        """
        button_1 = customtkinter.CTkButton(self.__general_tab, text="Button 1", width=10, height=2)
        button_1.grid(row=0, column=0, padx=10, pady=10)
        
    def __create_lotro_tab(self) -> None:
        """
        Create the lotro tab
        """
        button_1 = customtkinter.CTkButton(self.__lotro_tab, text="Button 1", width=10, height=2)
        button_1.grid(row=0, column=0, padx=10, pady=10)
        
    def __create_preference_tab(self) -> None:
        """
        Create the preference tab
        """
        button_1 = customtkinter.CTkButton(self.__preference_tab, text="Button 1", width=10, height=2)
        button_1.grid(row=0, column=0, padx=10, pady=10)
        
    def __create_sync_tab(self) -> None:
        """
        Create the sync tab
        """
        button_1 = customtkinter.CTkButton(self.__sync_tab, text="Button 1", width=10, height=2)
        button_1.grid(row=0, column=0, padx=10, pady=10)