"""
Application entry point containing the main application loop.
"""
import os
import signal
import threading
import time
import logging

import customtkinter
import psutil
import pymem

from app.view_window import ViewWindow
from backend.common.config import Config

class App(customtkinter.CTk):
    """
    Application class containing the main window and functions.
    """

    MAIN_WIDTH = 300 # Beginning window width
    MAIN_HEIGHT = 100 # Beginning window height
    EXIT_WIDTH = 320 # Exit dialog width
    EXIT_HEIGHT = 100 # Exit dialog height

    def __init__(self, debug: bool = False) -> None:
        """
        Main application window and functions.

        Pqrameters
        ----------
        debug : bool, optional
            Set to True to enable debug mode, by default False.

        Returns
        -------
        None
        """
        super().__init__() # Initialize the window
        self.__debug = debug

        # =============== Define the main window and appearance ===============
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # Set icon path and icon for the application
        self.icon_path = os.path.join('extra', 'imgs', 'favicon.ico')
        self.iconbitmap(self.icon_path)

        # Specify the delete window protocol
        self.protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), signal.SIGTERM))

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

        # =============== START OF MAIN WINDOW CONTENT ===============
        if self.__debug:
            logging.info("Starting main window...")
        self.waiting_label = customtkinter.CTkLabel(
            master=self,
            text="Waiting for lotro client to start..."
        )
        self.waiting_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        # =============== Threaded wait for client ==============
        self.__main_thread = threading.Thread(target=self.__run_config, args=[self.__debug])
        self.__main_thread.start()
        # self.__run_config(self.__debug)

    def __run_config(self, debug: bool = False) -> None:
        """
        Start the config and wait for the client to start.

        Parameters
        ----------
        debug : bool, optional
            Set to True to enable debug mode, by default False.

        Returns
        -------
        None
        """
        config: Config = Config(debug=debug)
        try:
            if config.await_process(): # Wait for the client to start
                print('Found process')
                # Start the process monitor to close the app when the client closes
                threading.Thread(target=self.__monitor_process, args=[config]).start()
                App.MAIN_WIDTH = App.MAIN_WIDTH+100 # Increase the window width
                config.set_address() # Set the address of the client
                self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}") # Resize the window
                self.waiting_label.configure( # Update the label
                    text=f"Client found at {config.lotro_exe} with PID: {config.pid}! Retrieving info.."
                )
                self.update() # Update the window
                self.withdraw() # Hide the waiting window
                ViewWindow(self, config) # Open the view window
        except pymem.pymem.exception.CouldNotOpenProcess as could_not_open: # Could not access the client memory (probably not running as admin)
            self.waiting_label.configure(
                text="Client requires Administrator permission!\n\nPlease rerun Lotro Extractor as Administrator.",
                text_color="#FF9632"
            )
            logging.exception(could_not_open)
            if not debug:
                time.sleep(5)
            else:
                time.sleep(3)
            os.kill(os.getpid(), signal.SIGTERM) # kill the process
        except Exception as gen_exception: # pylint: disable=broad-except
            self.waiting_label.configure(text="Something went wrong! Try again later.",
                                         text_color="#FF9632") # Update the label
            logging.exception(gen_exception) # Log the exception
            if not debug:
                time.sleep(5)
            else:
                time.sleep(3)
            os.kill(os.getpid(), signal.SIGTERM) # kill the process

    def __monitor_process(self, config: Config):
        """
        Check if the client is still running with given pid.

        Parameters
        ----------
        config : Config
            The config object.

        Returns
        -------
        None
        """
        while psutil.pid_exists(config.pid): # Check if the client is still running
            time.sleep(1)
        if self.__debug:
            logging.info("Client closed, closing app...") # Log the event
        config.close_mem() # Close the memory object
        os.kill(os.getpid(), signal.SIGTERM) # Kill the app if the user closes the game client