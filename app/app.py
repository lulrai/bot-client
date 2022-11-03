import os
import signal
import threading
import time

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
    MAIN_WIDTH = 300
    MAIN_HEIGHT = 100
    EXIT_WIDTH = 320
    EXIT_HEIGHT = 100

    """
    Init method to initialize the application.
    :param None
    :return None
    """
    def __init__(self, debug: bool = False) -> None:
        super().__init__()
        self.__debug = debug

        # =============== Define the main window and appearance ===============
        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
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
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        self.main_x = int((ws/2) - (App.MAIN_WIDTH/2))
        self.main_y = int((hs/2) - (App.MAIN_HEIGHT/2))
        self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}+{self.main_x}+{self.main_y}")

        # =============== 
        self.waiting_label = customtkinter.CTkLabel(master=self, text="Waiting for lotro client to start...")
        self.waiting_label.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
        
        # =============== Threaded wait for client ==============
        threading.Thread(target=self.__run_config, args=[self.__debug]).start()



    def __run_config(self, debug: bool = False) -> None:
        config = Config(debug=debug)
        try:
            if config.await_process():
                threading.Thread(target=self.__monitor_process, args=[config]).start()
                config.set_address()
                App.MAIN_WIDTH = App.MAIN_WIDTH+100
                self.geometry(f"{App.MAIN_WIDTH}x{App.MAIN_HEIGHT}")
                self.waiting_label.configure(text=f"Client found at {config.lotro_exe} with PID: {config.pid}! Retrieving info..")
                if not debug: time.sleep(10)
                ViewWindow(self, config, debug)
        except pymem.pymem.exception.CouldNotOpenProcess:
            self.waiting_label.configure(text=f"Client requires Administrator permission!\n\nPlease rerun Lotro Extractor as Administrator.", text_color="#FF9632")
            if not debug: time.sleep(5)
            else: time.sleep(3)
            self.__quit_app()
        except:
            self.waiting_label.configure(text=f"Something went wrong! Try again later.", text_color="#FF9632")
            if not debug: time.sleep(5)
            else: time.sleep(3)
            self.__quit_app()



    def __monitor_process(self, config: Config):
        """ Check if the client is still running with given pid. """
        while(psutil.pid_exists(config.pid)):
            time.sleep(1)
        config.close_mem()
        os.kill(os.getpid(), signal.SIGTERM)

    """
    Function to destroy the windows called from the confirmation window.
    :param popup: The popup to destroy.
    :type popup: customtkinter.CTKTopevel
    :return None
    """
    def __quit_app(self, popup: customtkinter.CTkToplevel = None) -> None:
        if popup is not None:
            popup.grab_release()
            popup.destroy()        
        os.kill(os.getpid(), signal.SIGTERM)



    """
    Function to destroy the window and the icon called from the icon menu.
    :param icon: The icon to destroy.
    :type icon: pystray.Icon
    :return None
    """
    def __quit_both_app(self, icon: Icon = None) -> None:
        if icon is not None:
            icon.stop()
        os.kill(os.getpid(), signal.SIGTERM)


    """
    Function to show the app window and destroy the icon if open.
    :param icon: The icon to destroy.
    :type icon: pystray.Icon
    :return None
    """
    def __show_app(self, icon) -> None:
        if icon is not None:
            icon.stop()
        self.after(0, self.deiconify)


    """
    Function to withdraw the app window, destroy popup, and create the icon in the system tray.
    :param popup: The popup to destroy.
    :type popup: customtkinter.CTKTopevel
    :return None
    """
    def __withdraw_app(self, popup: customtkinter.CTkToplevel = None) -> None:  
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
        self.icon = Icon("Lotro Extractor", image, "Lotro Extractor", menu)
        self.icon.run()


    """
    Function to create a custom dialog window.
    :param None
    :return None
    """
    def __custom_dialog(self) -> None:
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
        minimize_button = customtkinter.CTkButton(master=popout, text="Minimize", command=lambda: self.__withdraw_app(popout))
        minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)
        quit_button = customtkinter.CTkButton(master=popout, text="Quit", command=lambda: self.__quit_app(popup=popout), fg_color="#A52A2A", hover_color="#731d1d")
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)
