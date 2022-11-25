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
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
from win10toast_click import ToastNotifier

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
        :param debug: Set to True to enable debug mode
        :type debug: bool
        :returns: None
        """
        super().__init__()
        self.__debug = debug

        # =============== Define the main window and appearance ===============
        customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # Set icon path and icon for the application
        self.icon_path = os.path.join('extra', 'imgs', 'favicon.ico')
        self.iconbitmap(self.icon_path)

        # Specify the delete window protocol with custom function/dialog
        self.protocol("WM_DELETE_WINDOW", self.__custom_dialog)

        # Title of the app
        self.title("Lotro Extractor")

        # Placement of the window
        # get screen width and height
        screen_width = self.winfo_screenwidth() # width of the screen
        screen_height = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        self.main_x = int((screen_width/2) - (App.MAIN_WIDTH/2))
        self.main_y = int((screen_height/2) - (App.MAIN_HEIGHT/2))
        self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}+{self.main_x}+{self.main_y}")

        # =============== START OF MAIN WINDOW CONTENT ===============
        self.waiting_label = customtkinter.CTkLabel(
            master=self,
            text="Waiting for lotro client to start..."
        )
        self.waiting_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        # =============== Threaded wait for client ==============
        # self.__main_thread = threading.Thread(target=self.__run_config, args=[self.__debug])
        # self.__main_thread.start()
        self.__run_config(self.__debug)

    def __run_config(self, debug: bool = False) -> None:
        """
        Start the config and wait for the client to start.
        :param debug: Set to True to enable debug mode
        :type debug: bool
        :returns: None
        """
        config = Config(debug=debug)
        try:
            if config.await_process(): # Wait for the client to start
                print('Found process')
                # Start the process monitor to close the app when the client closes
                threading.Thread(target=self.__monitor_process, args=[config]).start()
                config.set_address() # Set the address of the client
                App.MAIN_WIDTH = App.MAIN_WIDTH+100 # Increase the window width
                self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}") # Resize the window
                self.waiting_label.configure( # Update the label
                    text=f"Client found at {config.lotro_exe} with PID: {config.pid}! Retrieving info.."
                )
                self.update() # Update the window
                self.withdraw() # Hide the waiting window
                ViewWindow(self, config, debug) # Open the view window
        except pymem.pymem.exception.CouldNotOpenProcess: # Could not access the client memory (probably not running as admin)
            self.waiting_label.configure(
                text="Client requires Administrator permission!\n\nPlease rerun Lotro Extractor as Administrator.",
                text_color="#FF9632"
            )
            if not debug: time.sleep(5)
            else: time.sleep(3)
            self.__quit_app() # Close the app
        except Exception as gen_exception: # pylint: disable=broad-except
            logging.exception(gen_exception) # Log the exception
            self.waiting_label.configure(text="Something went wrong! Try again later.", text_color="#FF9632") # Update the label
            if not debug: time.sleep(5)
            else: time.sleep(3)
            self.__quit_app() # Close the app

    def __monitor_process(self, config: Config):
        """
        Check if the client is still running with given pid.
        :param config: The config object.
        :type config: Config
        :returns: None
        """
        while psutil.pid_exists(config.pid): # Check if the client is still running
            time.sleep(1)
        config.close_mem() # Close the memory object
        os.kill(os.getpid(), signal.SIGTERM) # Kill the app if the user closes the game client

    def __quit_app(self, popup: customtkinter.CTkToplevel = None) -> None:
        """
        Function to destroy the windows called from the confirmation window.
        :param popup: The popup to destroy.
        :type popup: customtkinter.CTKTopevel
        :returns: None
        """
        if popup is not None: # If the popup is not None, destroy it
            popup.grab_release()
            popup.destroy()
        # self.__main_thread.join() # Join the main thread
        os.kill(os.getpid(), signal.SIGTERM) # Kill the app

    def __quit_both_app(self, icon: Icon = None) -> None:
        """
        Function to destroy the window and the icon called from the icon menu.
        :param icon: The icon to destroy.
        :type icon: pystray.Icon
        :returns: None
        """
        if icon is not None: # If the icon is not None, destroy it
            icon.stop()
        # self.__main_thread.join() # Join the main thread
        os.kill(os.getpid(), signal.SIGTERM) # Kill the app

    def __show_app(self, icon = None) -> None:
        """
        Function to show the app window and destroy the icon if open.
        :param icon: The icon to destroy.
        :type icon: pystray.Icon
        :returns: None
        """
        if icon is not None: # If the icon is not None, destroy it
            icon.stop()
        self.after(0, self.deiconify) # Show the app window

    def __withdraw_app(self, popup: customtkinter.CTkToplevel = None) -> None:
        """
        Function to withdraw the app window, destroy popup, and create the icon in the system tray.
        :param popup: The popup to destroy.
        :type popup: customtkinter.CTKTopevel
        :returns: None
        """
        # Release the focus and destroy the popup
        popup.grab_release()
        popup.destroy()

        # Withdraw the app itself and send a notification
        self.withdraw()
        toaster = ToastNotifier()
        toaster.show_toast("Lotro Extractor",
                   "Lotro Extractor is running in the system tray.",
                   icon_path=self.icon_path,
                   duration=3, threaded=True)

        # Create a system tray icon and run the icon
        image = Image.open(self.icon_path)
        menu = (item('Show', action=self.__show_app), item('Quit', action=self.__quit_both_app))
        self.icon = Icon("Lotro Extractor", image, "Lotro Extractor", menu) # pylint: disable=attribute-defined-outside-init
        self.icon.run()

    def __custom_dialog(self) -> None:
        """
        Function to create a custom dialog window.
        :param None
        :returns: None
        """
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(self)

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((self.main_x+App.MAIN_WIDTH/2) - (App.EXIT_WIDTH/2))
        popout_y = int((self.main_y+App.MAIN_HEIGHT/2) - (App.EXIT_HEIGHT/2))
        popout.geometry(f"{App.EXIT_WIDTH}x{App.EXIT_HEIGHT}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Grab the focus in the dialog window
        popout.grab_set()

        # Set the title and the information
        popout.title("Confirmation")
        label = customtkinter.CTkLabel( popout, text="Proceed to close or minimize application?")
        label.pack(pady=(13, 30))
        # Create the buttons, bind them to the functions, and pack them
        minimize_button = customtkinter.CTkButton(
            master=popout,
            text="Minimize",
            command=lambda: self.__withdraw_app(popout)
        )
        minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)
        quit_button = customtkinter.CTkButton(
            master=popout,
            text="Quit",
            command=lambda: self.__quit_app(popup=popout),
            fg_color="#A52A2A",
            hover_color="#731d1d"
        )
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)
