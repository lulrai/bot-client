import os
import signal
import logging
from typing import Any

import customtkinter
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
from win10toast_click import ToastNotifier
from app.common_view.popups import Popups

from app.preference_view.pref_page import PrefPage
from backend.common.config import Config
from backend.data_extractor import DataExtractor

class ViewWindow(customtkinter.CTkToplevel):
    """
    Display the home page with main title and info
    """

    WINDOW_WIDTH = 780
    WINDOW_HEIGHT = 520
    EXIT_WIDTH = 320
    EXIT_HEIGHT = 100

    def __init__(self, parent: customtkinter.CTk, config: Config) -> None:
        """
        Initialize the window and the icon.

        Parameters
        ----------
        parent : customtkinter.CTk
            The parent window.
        config : Config
            The config object.

        Returns
        -------
        None
        """
        super().__init__(master=parent)
        self.__parent = parent
        self.__config = config
        self.__data_extractor = DataExtractor(config)

        self.resizable(False, False)

        # Set icon path and icon for the application
        self.icon_path = os.path.join('extra', 'imgs', 'favicon.ico')
        self.iconbitmap(self.icon_path)

         # Create a system tray icon and run the icon
        image = Image.open(self.icon_path)
        menu = (item('Show', action=self.__show_app), item('Quit', action=self.__quit_both_app))
        if self.__config.debug:
            logging.info("Creating system tray icon and hiding the app.")
        self.icon = Icon("Lotro Extractor", image, "Lotro Extractor", menu)

        # Setup the dimension and position
        width_screen = self.winfo_screenwidth() # width of the screen
        height_screen = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        self.main_x: int = int((width_screen/2) - (ViewWindow.WINDOW_WIDTH/2))
        self.main_y: int = int((height_screen/2) - (ViewWindow.WINDOW_HEIGHT/2))
        self.geometry(f"{ViewWindow.WINDOW_WIDTH}x{ViewWindow.WINDOW_HEIGHT}+{self.main_x}+{self.main_y}")

        # Specify the delete window protocol with custom function/dialog
        self.protocol("WM_DELETE_WINDOW", lambda: Popups.two_button_popup(
                                                       self, (self.main_x, self.main_y),
                                                       (ViewWindow.WINDOW_WIDTH, ViewWindow.WINDOW_HEIGHT),
                                                       (ViewWindow.EXIT_WIDTH, ViewWindow.EXIT_HEIGHT),
                                                       "Confirm Exit",
                                                       "Proceed to close or minimize application?",
                                                       "Minimize", "Quit", first_button_command=self.__withdraw_app,
                                                       second_button_command=self.__quit_both_app,
                                                       second_button_text_color="#A52A2A", second_button_hover_color="#731d1d"
                                                   ))

        # Title of the app
        self.title("Lotro Data Extractor")

        # Create the main frame
        self.bind_all("<1>", lambda event: event.widget.focus_set() if not isinstance(event.widget, str) else None)

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create the left frame that contains the menu
        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        # create the right frame that contains the content
        self.frame_right = customtkinter.CTkFrame(master=self, width=ViewWindow.WINDOW_WIDTH, corner_radius=10)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # create the pages
        self.__create_home_page() # Create the home page
        self.__create_pref_page() # Create the preference page
        self.__create_info_page() # Create the info page
        self.__create_settings_page() # Create the settings page

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(8, weight=2) # empty row with minsize as spacing
        # self.frame_left.grid_rowconfigure(11, weight=1) # empty row with minsize as spacing

        # title of the app in the left frame
        self.frame_title = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Lotro Data\nExtractor",
                                              text_font=("Roboto Medium", -24))  # type: ignore font name and size in px
        self.frame_title.grid(row=1, column=0, pady=10, padx=10)

        # button to display the home page
        self.home_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Home",
                                                command=self.__show_home_page)
        self.home_button.grid(row=2, column=0, pady=10, padx=10)

        # button to display the preference page
        self.pref_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Edit Preferences",
                                                command=self.__display_pref_page)
        self.pref_button.grid(row=3, column=0, pady=10, padx=20)

        # button to display the character info page
        self.info_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Characters Info",
                                                command=self.__display_info_page)
        self.info_button.grid(row=4, column=0, pady=10, padx=20)

        # button to display the settings page
        self.settings_button = customtkinter.CTkButton(master=self.frame_left,
                                                    text="Settings",
                                                    command=self.__display_settings_page)
        self.settings_button.grid(row=5, column=0, pady=10, padx=20)

        # button to enable or disable the syncing of the data
        self.sync_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Sync Data",
                                                fg_color="#03a56a",
                                                hover_color="#037f51",
                                                command=self.__sync_data)
        self.sync_button.grid(row=6, column=0, pady=10, padx=20)
        
        # button to change the theme mode of the app
        self.label_mode = customtkinter.CTkLabel(master=self.frame_left, text="Appearance Mode:")
        self.label_mode.grid(row=10, column=0, pady=0, padx=20, sticky="w")

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        values=["Dark", "Light"],
                                                        command=self.__change_appearance_mode)
        self.optionmenu_1.grid(row=11, column=0, pady=10, padx=20, sticky="w")

        self.__show_home_page() # Show the home page at the start of the app

    def __create_home_page(self) -> None:
        """
        Create the home page variables.
        """
        if self.__config.debug:
            logging.info("Creating home page.")
        # create the home page frame
        self.home_page = customtkinter.CTkFrame(master=self.frame_right, fg_color=None)  # type: ignore
        # add the title of the home page
        self.home_page_title = customtkinter.CTkLabel(master=self.home_page,
                                              text="About",
                                              text_font=("Roboto Medium", -30))  # type: ignore font name and size in px
        # create the text of the home page
        first_par_text = """"
                Lotro Extractor is an application that allows you to extract information and data\n
                from the game files and send the information from the LotRO game client to a database.\n
                The data can be used to create a website or other applications.\n
                It allows you to openly view the information from the client.\nAnd edit the preference file!
                """
        # add the text of the home page
        self.home_page_text = customtkinter.CTkLabel(master=self.home_page,
                                              text=first_par_text,
                                              text_font=("Roboto Medium", -14)) # type: ignore font name and size in px

    def __show_home_page(self) -> None:
        """
        Display the home page with main title and info.
        """
        if self.__config.debug:
            logging.info("Displaying home page.")

        # hide all the other pages
        self.__hide_pref_page()
        self.__hide_info_page()
        self.__hide_settings_page()

        # display the home page
        self.home_page.grid_rowconfigure(1, weight=1)
        self.home_page.grid_columnconfigure((0,1,2), weight=1)  # type: ignore
        self.home_page.grid()

        # display the title of the home page and the text
        self.home_page_title.grid(row=0, column=0, columnspan=3, pady=10)
        self.home_page_text.grid(row=1, column=0, columnspan=3, padx=(10,0), pady=10, sticky="ew")

    def __hide_home_page(self) -> None:
        """
        Hide the home page.
        """
        if self.__config.debug:
            logging.info("Hiding home page.")
        self.home_page.grid_forget() # hide the home page

    def __create_pref_page(self) -> None:
        """
        Create the preference page variables.
        """
        if self.__config.debug:
            logging.info("Creating preference page.")
        # create the preference page frame
        self.pref_page = PrefPage(self.frame_right, self.__config, self.main_x, self.main_y)

    def __display_pref_page(self) -> None:
        """
        Display the preference page.
        """
        # hide all the other pages
        self.__hide_home_page()
        self.__hide_info_page()
        self.__hide_settings_page()

        self.pref_page.show_pref_page() # display the preference page

    def __hide_pref_page(self) -> None:
        """
        Remove the preference page.
        """
        self.pref_page.hide_pref_page() # hide the preference page

    def __create_info_page(self) -> None:
        """ Create the info page variables. """
        print('Creating info page')

    def __display_info_page(self) -> None:
        """ Display the info page. """
        # hide all the other pages
        self.__hide_home_page()
        self.__hide_pref_page()
        self.__hide_settings_page()

        print('Displaying info page')

    def __hide_info_page(self) -> None:
        """ Hide the info page. """
        print('Hiding info page')

    def __create_settings_page(self) -> None:
        """ Create the settings page variables. """
        print('Creating settings page')

    def __display_settings_page(self) -> None:
        """ Display the settings page. """
        # hide all the other pages
        self.__hide_home_page()
        self.__hide_pref_page()
        self.__hide_info_page()

        print('Displaying settings page')

    def __hide_settings_page(self) -> None:
        """ Hide the settings page. """
        print('Hiding settings page')

    def __sync_data(self):
        """ Enable or disable the syncing of the data. """
        if self.__data_extractor.sync_enabled(): # if the data syncing is enabled
            if self.__config.debug:
                logging.info("Stopping syncing data...")
            self.__data_extractor.stop_sync() # stop syncing the data
            # change the button text and color
            self.sync_button.configure(require_redraw=True, text = "Sync Data", fg_color="#03a56a", hover_color="#037f51")
        else: # if the data syncing is disabled
            if self.__config.debug:
                logging.info("Starting syncing data...")
            self.__data_extractor.sync() # start syncing the data
            # change the button text and color
            self.sync_button.configure(require_redraw=True, text = "Stop Syncing", fg_color="#A52A2A", hover_color="#731d1d")

    def __change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.__parent.withdraw()

    def __quit_both_app(self, **kwargs: dict[str, Any]) -> None:
        """
        Function to destroy the window and the icon called from the icon menu.

        Parameters
        ----------
        popup: customtkinter.CTkToplevel
            The popup to destroy.
        icon: pystray.Icon
            The icon to destroy.
        """
        if self.__config.debug:
            logging.info("Closing app...")

        if 'icon' in kwargs: # if the icon is passed, destroy it
            kwargs['icon'].stop()
        if 'popup' in kwargs: # if the popup is passed, destroy it
            kwargs['popup'].grab_release()
            kwargs['popup'].destroy()
        self.__config.close_mem() # close the memory
        if self.__data_extractor.sync_enabled(): # if the data syncing is enabled
            self.__data_extractor.stop_sync() # stop syncing the data
        os.kill(os.getpid(), signal.SIGTERM) # kill the process

    def __show_app(self, **kwargs: dict[str, Any]) -> None:
        """
        Function to show the app window and destroy the icon if open.

        Parameters
        ----------
        icon: pystray.Icon
            The icon to destroy.
        """
        if self.__config.debug:
            logging.info("Unhiding the app window.")

        if 'icon' in kwargs: # if the icon is passed, destroy it
            kwargs['icon'].stop()
        self.after(0, self.deiconify) # show the window

    def __withdraw_app(self, **kwargs) -> None:
        """
        Function to withdraw the app window and create the icon in the system tray.

        Parameters
        ----------
        popup: customtkinter.CTkToplevel
            The popup to destroy.
        """
        # Release the focus and destroy the popup
        if 'popup' in kwargs:
            kwargs['popup'].grab_release()
            kwargs['popup'].destroy()

        # Withdraw the app itself and send a notification
        self.withdraw()
        toaster = ToastNotifier()
        toaster.show_toast("Lotro Extractor",
                   "Lotro Extractor is running in the system tray.",
                   icon_path=self.icon_path,
                   duration=3, threaded=True)
        self.icon.run()
