import configparser
import os
import time
import customtkinter
from customtkinter import CTkCanvas
import shutil

from app.preference_view.pref_view import PreferenceView
from backend.common.config import Config
from backend.utils.common_utils import Utils

class PrefPage():
    PARENT_WINDOW_WIDTH = 780
    PARENT_WINDOW_HEIGHT = 520
    CONFIRM_WIDTH = 360
    CONFIRM_HEIGHT = 100

    def __init__(self, parent_frame, config: Config, parent_x, parent_y):
        self.parent_frame = parent_frame
        self.__config = config
        self.__search_string = ''
        self.__pref_view_list = []
        self.__parent_x = parent_x
        self.__parent_y = parent_y
        self.config_changes = {}
        self.__preferences_ini = configparser.ConfigParser()
        self.__preferences_path: str = ""

        self.__load_prefs()
        self.display_search_bar()
        self.display_pref_list()

    def __load_prefs(self):
        preferences_ini_offset = 0x00 if self.__config.is_64bits else 0x40
        main_client_data_addr = self.__config.mem.read_uint(int(self.__config.client_data_address, base=16))
        preferences_addr = self.__config.mem.read_uint(main_client_data_addr + preferences_ini_offset)
        self.__preferences_path = Utils.retrieve_string(self.__config.mem, preferences_addr)

        self.__preferences_ini.read(self.__preferences_path)


    def display_search_bar(self):
        self.search_bar = customtkinter.CTkFrame(master=self.parent_frame, fg_color=None)
        self.search_bar.grid(row=0, column=0, columnspan=2, rowspan=1, pady=10, sticky="nsew")

        self.search_label = customtkinter.CTkLabel(master=self.search_bar, text="Search: ")
        self.search_label.grid(row=0, column=0, columnspan=1, rowspan=1, sticky="e", padx=5, pady=5)

        self.search_str = customtkinter.StringVar()
        self.search_entry = customtkinter.CTkEntry(master=self.search_bar, width=270, placeholder_text="Search preferences", textvariable=self.search_str)
        self.search_entry.grid(row=0, column=1, columnspan=1, rowspan=1, sticky="w", padx=5, pady=5)
        self.search_entry.bind('<Return>', self.search_parser)

        self.save_button = customtkinter.CTkButton(master=self.search_bar, width=90, state="disabled", text="Save All", command=self._save_preference_popup)
        self.save_button.grid(row=0, column=2, padx=20, pady=5)

        self.canvas_frame = customtkinter.CTkFrame(master=self.parent_frame)
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_propagate(False)

        self.canvas = CTkCanvas(master=self.canvas_frame, highlightthickness=0, bd=-2, bg='#2a2d2e')

        self.origX = self.canvas.xview()[0]
        self.origY = self.canvas.yview()[0]

        vsb = customtkinter.CTkScrollbar(self.canvas_frame, orientation="vertical", command=self.canvas.yview)
        vsb.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=vsb.set)


    def display_pref_list(self):
        self.__pref_view_list = []
        self.list_frame = customtkinter.CTkFrame(self.canvas)

        self.list_frame.bind('<Configure>', self._configure_window)
        self.list_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.list_frame.bind('<Leave>', self._unbound_to_mousewheel)
        self.list_frame.columnconfigure(0, weight=1)


        row_num = 0
        for key, value in self.__preferences_ini.items():
            if list(value.keys()):
                pref_view = PreferenceView(parent=self.list_frame, save_button=self.save_button, name=key, items=value, config_changes=self.config_changes)
                pref_view.grid(row=row_num, column=0, columnspan=2, rowspan=1, sticky='nw')
                self.__pref_view_list.append(pref_view)
                row_num += 1

        self.list_frame.update_idletasks()

        self.canvas_frame.config(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.interior_id = self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
        self.canvas_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky='nw')
        self.canvas.grid(row=0, column=0, sticky="news")


    def search_parser(self, event):
        self.__search_string = self.search_str.get().lower()

        if self.__search_string:
            self.list_frame.destroy()
            self.__pref_view_list = []

            self.list_frame = customtkinter.CTkFrame(self.canvas)
            self.canvas.xview_moveto(self.origX)
            self.canvas.yview_moveto(self.origY)

            self.list_frame.bind('<Configure>', self._configure_window)
            self.list_frame.bind('<Enter>', self._bound_to_mousewheel)
            self.list_frame.bind('<Leave>', self._unbound_to_mousewheel)
            
            self.list_frame.rowconfigure(0, weight=1)
            row_num = 0
            for key in self.__preferences_ini.keys():
                if list(self.__preferences_ini[key].keys()) and (self.__search_string in key.lower() or self.__search_string in f"{key.lower()} preference"):
                    pref_view = PreferenceView(parent=self.list_frame, save_button=self.save_button, name=key, items=self.__preferences_ini[key], config_changes=self.config_changes)
                    pref_view.grid(row=row_num, column=0, columnspan=2, rowspan=1, sticky='nw')
                    self.__pref_view_list.append(pref_view)
                    row_num += 1
                elif list(self.__preferences_ini[key].keys()):
                    for inner_key in self.__preferences_ini[key]:
                        if self.__search_string in inner_key.lower():
                            pref_view = PreferenceView(parent=self.list_frame, save_button=self.save_button, name=key, items=self.__preferences_ini[key], config_changes=self.config_changes)
                            pref_view.grid(row=row_num, column=0, columnspan=2, rowspan=1, sticky='nw')
                            row_num += 1

            self.list_frame.update_idletasks()

            self.canvas_frame.config(width=560, height=PrefPage.PARENT_WINDOW_HEIGHT-40-self.search_bar.winfo_reqheight()-20)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.interior_id = self.canvas.create_window((0,0), window=self.list_frame, anchor="nw")
            self.canvas_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky='nw')
            self.canvas.grid(row=0, column=0, sticky="news")
        else:
            self.list_frame.destroy()
            self.display_pref_list()

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/100)), "units") 

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.list_frame.winfo_reqwidth(), self.list_frame.winfo_reqheight())
        self.canvas.config(scrollregion='0 0 %s %s' % size)
        if self.list_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width = self.list_frame.winfo_reqwidth())
        if self.list_frame.winfo_reqheight() != self.canvas.winfo_height():
            # update the canvas's width to fit the inner frame
            self.canvas.config(height = self.list_frame.winfo_reqheight())

    def _configure_canvas(self, event):
            if self.list_frame.winfo_reqwidth() != self.canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def _save_preference_popup(self):
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(self.parent_frame)
        popout.attributes('-topmost', 'true')

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((self.__parent_x+PrefPage.PARENT_WINDOW_WIDTH/2) - (PrefPage.CONFIRM_WIDTH/2))
        popout_y = int((self.__parent_y+PrefPage.PARENT_WINDOW_HEIGHT/2) - (PrefPage.CONFIRM_HEIGHT/2))
        popout.geometry(f"{PrefPage.CONFIRM_WIDTH}x{PrefPage.CONFIRM_HEIGHT}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Grab the focus in the dialog window
        popout.grab_set()

        # Set the title and the information
        popout.title("Are you sure?")
        label = customtkinter.CTkLabel( popout, text="Warning: Do not save unless you know what you're doing.", text_color="#FF9632")
        label.pack(pady=(13, 30))
        minimize_button = customtkinter.CTkButton(master=popout, text="Save", command=lambda: self._save_preference(popout))
        minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)
        quit_button = customtkinter.CTkButton(master=popout, text="Cancel", command=popout.destroy(), fg_color="#A52A2A", hover_color="#731d1d")
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)

    def _save_preference(self, popout):
        popout.destroy()
        
        try:
            src_fpath = self.__preferences_path
            dest_fpath, file_name = os.path.split(os.path.abspath(src_fpath))
            file_name = file_name.replace('.ini', f'{int(time.time())}_bak.ini')

            dest_fpath = os.path.join(dest_fpath, 'backup')
            if os.path.isdir(dest_fpath):
                file_count = len([f for f in os.listdir(dest_fpath) if f.endswith('.ini') and os.path.isfile(os.path.join(dest_fpath, f))])
                if file_count >= 30:
                    oldest_file = sorted(os.listdir(dest_fpath), key=lambda x: os.path.getctime(os.path.join(dest_fpath,x)))[0]
                    os.remove(os.path.join(dest_fpath, oldest_file))

            dest_fpath = os.path.join(dest_fpath, file_name)
            os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
            shutil.copy(src_fpath, dest_fpath)
        except OSError:
            pass
        
        for section in self.config_changes:
            for option in self.config_changes[section]:
                self.__preferences_ini.set(section, option, self.config_changes[section][option])

        with open(src_fpath, 'w') as configfile:
            self.__preferences_ini.write(configfile, space_around_delimiters=False)
        
        for pref_view in self.__pref_view_list:
            pref_view.clear_fields()
        if self.save_button.state == customtkinter.NORMAL: 
                    self.save_button.configure(state=customtkinter.DISABLED)
