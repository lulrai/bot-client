"""
Application entry point containing the main application loop.
"""
import os
from re import Pattern
import re
import signal
import threading
import logging
from typing import Any

import customtkinter
#from tktooltip import ToolTip
import psutil
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
from win10toast_click import ToastNotifier

from app.common_view.popups import Popups
from app.preference_view.pref_page import PrefPage
from backend.common.config import Client_Status, GameConfig, AppConfig

class App(customtkinter.CTk):
    """
    Application class containing the main window and functions.
    """

    MAIN_WIDTH = 780 # Beginning window width
    MAIN_HEIGHT = 520 # Beginning window height
    EXIT_WIDTH = 320 # Exit dialog width
    EXIT_HEIGHT = 100 # Exit dialog height

    def __init__(self, app_config: AppConfig) -> None:
        """
        Main application window and functions.

        Pqrameters
        ----------
        app_config : AppConfig
            The application config object.

        Returns
        -------
        None
        """
        super().__init__(fg_color=("#FFFFFF", "#121212")) # Initialize the window
        self.__app_config = app_config # Set the application config
        self.__debug = self.__app_config.get_config('debug') # Set the debug mode
        self.__game_config: GameConfig = GameConfig(self.__app_config, self.__debug) # Create the game config
        self.__sync_thread_event = threading.Event() # Create a thread event

        # =============== Define the main window and appearance ===============
        customtkinter.set_appearance_mode(self.__app_config.get_config('theme'))  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

        # Set icon path and icon for the application
        self.icon_path = os.path.join('extra', 'imgs', 'favicon.ico')
        self.iconbitmap(self.icon_path)

        # Specify the delete window protocol with custom function/dialog
        self.protocol("WM_DELETE_WINDOW", lambda: Popups.two_button_popup(self,
                                                       (App.MAIN_WIDTH, App.MAIN_HEIGHT),
                                                       (App.EXIT_WIDTH, App.EXIT_HEIGHT),
                                                       "Confirm Exit",
                                                       "Proceed to close or minimize application?",
                                                       "Minimize", "Quit", first_button_command=self.__withdraw_app,
                                                       second_button_command=self.__quit_both_app
                                                   ))

        # Title of the app
        self.title("Lotro Data Extractor")

        # set resizable to False
        self.resizable(False, False)

        # Placement of the window
        # get screen width and height
        screen_width = self.winfo_screenwidth() # width of the screen
        screen_height = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        self.main_x = int((screen_width/2) - (App.MAIN_WIDTH/2))
        self.main_y = int((screen_height/2) - (App.MAIN_HEIGHT/2))
        self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}+{self.main_x}+{self.main_y}")

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create the left frame that contains the menu
        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")
        self.frame_left.configure(fg_color=("#FFFBFE", "#1e1e1e"))

        # create the right frame that contains the content
        self.frame_right = customtkinter.CTkFrame(master=self, width=App.MAIN_WIDTH, corner_radius=10)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.frame_right.configure(fg_color=("#FFFBFE", "#222222"))

        # create the pages
        self.__create_home_page() # Create the home page
        self.__create_pref_page() # Create the preference page
        self.__create_info_page() # Create the info page
        self.__create_settings_page() # Create the settings page

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(7, weight=2) # empty row with minsize as spacing
        # self.frame_left.grid_rowconfigure(11, weight=1) # empty row with minsize as spacing

        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "imgs")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "icons", "CustomTkinter_logo_single.png")), size=(26, 26))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "icons", "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "icons", "home_light.png")), size=(20, 20))
        self.chat_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "icons", "chat_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "icons", "chat_light.png")), size=(20, 20))
        self.add_user_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "icons", "add_user_dark.png")),
                                                     dark_image=Image.open(os.path.join(image_path, "icons", "add_user_light.png")), size=(20, 20))

        # title of the app in the left frame
        self.frame_title = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Lotro Data\nExtractor",
                                              text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                              font=("Roboto Medium", 30))  # type: ignore font name and size in px
        self.frame_title.grid(row=1, column=0, pady=10, padx=10)

        # button to display the home page
        self.home_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Home",
                                                text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                fg_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                hover_color=("#42A5F5", "#0D47A1"), # (Light=Blue400, Dark=Blue900)
                                                command=self.__show_home_page)
        self.home_button.grid(row=2, column=0, pady=10, padx=10)

        # button to display the preference page
        self.pref_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Edit Preferences",
                                                text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                fg_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                hover_color=("#42A5F5", "#0D47A1"), # (Light=Blue400, Dark=Blue900)
                                                command=self.__display_pref_page)
        self.pref_button.grid(row=3, column=0, pady=10, padx=20)

        # button to display the character info page
        self.info_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Characters Info",
                                                text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                fg_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                hover_color=("#42A5F5", "#0D47A1"), # (Light=Blue400, Dark=Blue900)
                                                command=self.__display_info_page)
        self.info_button.grid(row=4, column=0, pady=10, padx=20)

        # button to display the settings page
        self.settings_button = customtkinter.CTkButton(master=self.frame_left,
                                                    text="Settings",
                                                    text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                    fg_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                    hover_color=("#42A5F5", "#0D47A1"), # (Light=Blue400, Dark=Blue900)
                                                    command=self.__display_settings_page)
        self.settings_button.grid(row=5, column=0, pady=10, padx=20)

        # button to enable or disable the syncing of the data
        self.sync_button = customtkinter.CTkButton(master=self.frame_left,
                                                text="Sync Data",
                                                text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                fg_color="#03a56a",
                                                hover_color="#037f51",
                                                command=self.__sync_data,
                                                state="disabled")
        self.sync_button.grid(row=6, column=0, pady=10, padx=20)

        # label to display the status of the running client
        self.client_label_header = customtkinter.CTkLabel(master=self.frame_left,
                                                text="Client Status:",
                                                text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                )
        self.client_label_header.grid(row=8, column=0, pady=0, padx=20)
        self.client_status_label = customtkinter.CTkLabel(master=self.frame_left,
                                                text="Not Running",
                                                text_color=("#B00020", "#CF6679")) # (Light=#B00020, Dark=#CF6679)
        self.client_status_label.grid(row=9, column=0, pady=0, padx=20)

        # button to change the theme mode of the app
        self.label_mode = customtkinter.CTkLabel(master=self.frame_left,
                                                 text="Appearance Mode:",
                                                 text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                 )
        self.label_mode.grid(row=10, column=0, pady=0, padx=20)

        self.optionmenu_1 = customtkinter.CTkOptionMenu(master=self.frame_left,
                                                        text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                        button_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                        button_hover_color=("#42A5F5", "#0D47A1"), # (Light=Blue400, Dark=Blue900)
                                                        fg_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                        values=["Dark", "Light"],
                                                        dropdown_fg_color=("#FFFBFE", "#1e1e1e"), # (Light=White, Dark=Black)
                                                        dropdown_hover_color=("#64B5F6", "#1565C0"), # (Light=Blue300, Dark=Blue800)
                                                        dropdown_text_color=("#000000", "#FFFFFF"), # (Light=Black, Dark=White)
                                                        command=self.__change_appearance_mode)
        self.optionmenu_1.grid(row=11, column=0, pady=10, padx=20)

        # Start the process monitor to enable/disable sync button
        self.__sync_thread = threading.Thread(target=self.__monitor_process, args=[self.__game_config, self.__app_config, self.__sync_thread_event, self.sync_button, self.client_status_label])
        self.__sync_thread.daemon = True
        self.__sync_thread_event.clear()
        self.__sync_thread.start()

        self.__show_home_page() # Show the home page at the start of the app

    def __monitor_process(self, game_config: GameConfig, app_config: AppConfig, event: threading.Event, sync_button: customtkinter.CTkButton, client_status_label: customtkinter.CTkLabel) -> None:
        """
        Check if the client is still running with given pid.

        Parameters
        ----------
        game_config : GameConfig
            The game config object.
        event : threading.Event
            The event to stop the thread.
        sync_button : customtkinter.CTkButton
            The sync button to enable/disable.

        Returns
        -------
        None
        """
        # Constantly monitor the process
        bit_match: Pattern = re.compile("lotroclient(64)*.exe") # Regex to match the game client exe.
        while not event.is_set():
            if game_config.client_status == Client_Status.NOT_FOUND:
                # If the process is not running, disable the sync button
                sync_button.configure(
                    text="Sync Data",
                    fg_color="#03a56a",
                    state="disabled", require_redraw=False)
                for proc in psutil.process_iter(): # Iterate over all the processes
                    name_match = bit_match.search(proc.name().lower()) # Check if the process name matches the regex
                    if bool(name_match):
                        game_config.set_address(name_match, proc.pid) # Set the address of the client
                    if game_config.client_status == Client_Status.RUNNING:
                        client_status_label.configure(text="Running", text_color=("#4DB6AC", "#00695C")) # (Light=#4DB6AC, Dark=#00695C)
                        # If the process is running, enable the sync button
                        sync_button.configure(
                            text="Sync Data",
                            fg_color="#03a56a",
                            state="normal", require_redraw=False)
                        break
                    elif game_config.client_status == Client_Status.MISSING_ADMIN:
                        client_status_label.configure(text="Missing Admin", text_color=("#FFA726", "#E65100")) # (Light=#FFA726, Dark=#E65100)
                    elif game_config.client_status == Client_Status.UNKNOWN_ERROR:
                        client_status_label.configure(text="Unknown", text_color=("#B00020", "#CF6679")) # (Light=#B00020, Dark=#CF6679)
            if not psutil.pid_exists(game_config.pid):
                # If the process is not running anymore, disable the sync button
                game_config.client_status = Client_Status.NOT_FOUND
                client_status_label.configure(text="Not Running", text_color=("#B00020", "#CF6679")) # (Light=#B00020, Dark=#CF6679)
                sync_button.configure(
                    text="Sync Data",
                    fg_color="#03a56a",
                    state="disabled", require_redraw=False)
            event.wait(app_config.get_config('lotro', 'client_check_interval')) # Wait 3 seconds before checking again

    def __create_home_page(self) -> None:
        """
        Create the home page variables.
        """
        if self.__debug:
            logging.info("Creating home page.")
        # create the home page frame
        self.home_page = customtkinter.CTkFrame(master=self.frame_right, fg_color=None)  # type: ignore
        # add the title of the home page
        self.home_page_title = customtkinter.CTkLabel(master=self.home_page,
                                            text="About",
                                            font=("Roboto Medium", -30))  # type: ignore font name and size in px
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
                                            font=("Roboto Medium", -14)) # type: ignore font name and size in px

    def __show_home_page(self) -> None:
        """
        Display the home page with main title and info.
        """
        if self.__debug:
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
        if self.__debug:
            logging.info("Hiding home page.")
        self.home_page.grid_forget() # hide the home page

    def __create_pref_page(self) -> None:
        """
        Create the preference page variables.
        """
        if self.__debug:
            logging.info("Creating preference page.")
        # create the preference page frame
        self.pref_page = PrefPage(self.frame_right, self.__game_config, self.__app_config, self.main_x, self.main_y)

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
            if self.__debug:
                logging.info("Stopping syncing data...")
            self.__data_extractor.stop_sync() # stop syncing the data
            # change the button text and color
            self.sync_button.configure(require_redraw=True, text = "Sync Data", fg_color="#03a56a", hover_color="#037f51")
        else: # if the data syncing is disabled
            if self.__debug:
                logging.info("Starting syncing data...")
            self.__data_extractor.sync() # start syncing the data
            # change the button text and color
            self.sync_button.configure(require_redraw=True, text = "Stop Syncing", fg_color="#A52A2A", hover_color="#731d1d")

    def __change_appearance_mode(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)

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
        if self.__debug:
            logging.info("Closing app...")

        if 'icon' in kwargs: # if the icon is passed, destroy it
            kwargs['icon'].stop()
        if 'popup' in kwargs: # if the popup is passed, destroy it
            kwargs['popup'].grab_release()
            kwargs['popup'].destroy()
        if self.__game_config.mem:
            self.__game_config.close_mem() # close the memory
        self.__sync_thread_event.set() # set the event to stop the thread
        # TODO - fix this
        # if self.__data_extractor.sync_enabled(): # if the data syncing is enabled
        #     self.__data_extractor.stop_sync() # stop syncing the data
        os.kill(os.getpid(), signal.SIGTERM) # kill the process

    def __show_app(self, icon, _) -> None:
        """
        Function to show the app window and destroy the icon if open.

        Parameters
        ----------
        icon: pystray.Icon
            The icon to destroy.
        """
        if self.__debug:
            logging.info("Unhiding the app window.")

        icon.stop()
        self.after(0, self.deiconify()) # show the window

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

        # Create a system tray icon and run the icon
        image = Image.open(self.icon_path)
        menu = (item('Show', action=self.__show_app, default=True), item('Quit', action=self.__quit_both_app))
        if self.__debug:
            logging.info("Creating system tray icon and hiding the app.")
        icon = Icon("Lotro Data Extractor", image, "Lotro Data Extractor", menu)

        # Withdraw the app itself and send a notification
        self.withdraw()
        toaster = ToastNotifier()
        toaster.show_toast("Lotro Extractor",
                   "Lotro Extractor is running in the system tray.",
                   icon_path=self.icon_path,
                   duration=3, threaded=True)
        icon.run_detached()
