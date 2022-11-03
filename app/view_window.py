import os
import signal

import customtkinter
from PIL import Image
from pystray import Icon
from pystray import MenuItem as item
from win10toast_click import ToastNotifier

from app.preference_view.pref_page import PrefPage
from backend.common.config import Config
from backend.data_extractor import DataExtractor


class ViewWindow(customtkinter.CTkToplevel):
    WINDOW_WIDTH = 780
    WINDOW_HEIGHT = 520
    EXIT_WIDTH = 320
    EXIT_HEIGHT = 100

    def __init__(self, parent: customtkinter.CTk, config: Config, debug: bool = False) -> None:
        super().__init__(master=parent)
        self.__parent = parent
        self.__parent.withdraw()
        self.__config = config
        self.__data_extractor = DataExtractor(config)
        self.__pref_visible = False
        
        self.resizable(False, False)
        self.__data_extractor.sync()
        # self.__client_data = ClientData(config, debug)
        # self.__client_data.load_client_data()

        # Set icon path and icon for the application
        self.icon_path = os.path.join('extra', 'imgs', 'favicon.ico')
        self.iconbitmap(self.icon_path)

        # Setup the dimension and position
        ws = self.winfo_screenwidth() # width of the screen
        hs = self.winfo_screenheight() # height of the screen
        # calculate x and y coordinates for the Tk root window
        self.main_x = int((ws/2) - (ViewWindow.WINDOW_WIDTH/2))
        self.main_y = int((hs/2) - (ViewWindow.WINDOW_HEIGHT/2))
        self.geometry(f"{ViewWindow.WINDOW_WIDTH}x{ViewWindow.WINDOW_HEIGHT}+{self.main_x}+{self.main_y}")

        # Specify the delete window protocol with custom function/dialog
        self.protocol("WM_DELETE_WINDOW", self.__custom_dialog)

        # Title of the app
        self.title("Lotro Data")

        self.bind_all("<1>", lambda event: event.widget.focus_set() if not isinstance(event.widget, str) else None)

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self, width=ViewWindow.WINDOW_WIDTH, corner_radius=10)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, weight=1)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, weight=1)  # empty row with minsize as spacing

        self.frame_title = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Lotro Data\nExtractor",
                                              text_font=("Roboto Medium", -24))  # font name and size in px
        self.frame_title.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Edit Preferences",
                                                command=self.display_pref_page)
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Display Info",
                                                command=self.display_info)
        self.button_2.grid(row=3, column=0, pady=10, padx=20)

        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Send Info",
                                                fg_color="#A52A2A", 
                                                hover_color="#731d1d",
                                                command=self.send_info)
        self.button_3.grid(row=4, column=0, pady=10, padx=20)

        # ============ frame_right ============
        self.display_home_page()

    
    def display_home_page(self):
        self.display_page = customtkinter.CTkFrame(master=self.frame_right, fg_color=None)
        self.display_page.grid_rowconfigure(1, weight=1)
        self.display_page.grid_columnconfigure((0,1,2), weight=1)
        self.display_page.grid()
        
        self.display_title = customtkinter.CTkLabel(master=self.display_page,
                                              text="About",
                                              text_font=("Roboto Medium", -30))  # font name and size in px
        self.display_title.grid(row=0, column=0, columnspan=3, pady=10)

        first_par_text = """Lotro Extractor is an application that allows you to extract information and send the  \ninformation\nfrom the LotRO game client.\n
        It allows you to openly view the information from the client.\nAnd edit the preference file!"""
        self.first_par = customtkinter.CTkLabel(master=self.display_page,
                                              text=first_par_text,
                                              text_font=("Roboto Medium", -14))
        self.first_par.grid(row=1, column=0, columnspan=3, padx=(10,0), pady=10, sticky="ew")

        
    def remove_display_page(self):
        self.first_par.destroy()
        self.display_title.destroy()
        self.display_page.destroy()

    def remove_pref_page(self):
        self.pref_page.search_bar.destroy()
        self.pref_page.search_label.destroy()
        self.pref_page.search_entry.destroy()
        self.pref_page.canvas_frame.destroy()
        self.pref_page.canvas.destroy()
        self.pref_page.list_frame.destroy()
        del self.pref_page

    def display_pref_page(self):
        if self.__pref_visible:
            self.remove_pref_page()
            self.__pref_visible = False
            self.display_home_page()
        else:
            self.remove_display_page()
            self.pref_page = PrefPage(self.frame_right, self.__config, self.main_x, self.main_y)
            self.__pref_visible = True

    def display_info(self):
        print('Display info')

    def send_info(self):
        print('Send info')

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
        self.__config.close_mem() 
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
        self.__config.close_mem() 
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
        

    def __custom_dialog(self) -> None:
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(self)

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((self.main_x+ViewWindow.WINDOW_WIDTH/2) - (ViewWindow.EXIT_WIDTH/2))
        popout_y = int((self.main_y+ViewWindow.WINDOW_HEIGHT/2) - (ViewWindow.EXIT_HEIGHT/2))
        popout.geometry(f"{ViewWindow.EXIT_WIDTH}x{ViewWindow.EXIT_HEIGHT}+{popout_x}+{popout_y}")
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
        