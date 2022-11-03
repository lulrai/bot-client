from configparser import SectionProxy

import customtkinter


class PreferenceView(customtkinter.CTkFrame):
    WINDOW_WIDTH = 780
    def __init__(self, parent: customtkinter.CTkFrame, save_button: customtkinter.CTkButton, name: str, items: SectionProxy, config_changes: dict):
        super().__init__(master=parent, width=560)
        self.__items = items
        self.__name = name
        self.__string_var = {}

        self.save_button = save_button
        self.config_changes = config_changes

        # self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        # self.grid_rowconfigure(len(self.__items.keys())+4, weight=2)
           
        self.text_label = customtkinter.CTkLabel(self, corner_radius=10, width=560, text=f"{self.__name} Preference", text_font=("Roboto Medium", -17), fg_color=("white", "gray45"))
        self.text_label.grid(row=0, column=0, columnspan=2, rowspan=1, sticky="nsew")

        self.sub_frame = customtkinter.CTkFrame(self, width=560)
        self.sub_frame.grid(row=1, column=0, columnspan=2, rowspan=1, sticky="nsew")

        # self.sub_frame.grid_rowconfigure(idx, weight=1)
        self.sub_frame.grid_columnconfigure(0, weight=1)
        self.sub_frame.grid_columnconfigure(1, weight=1)

        for idx, item in enumerate(self.__items.keys()):
            left_side = customtkinter.CTkLabel(master=self.sub_frame, text=item)
            left_side.grid(row=idx, column=0, columnspan=1, rowspan=1, sticky="ew", padx=5)
            sv = customtkinter.StringVar()
            self.__string_var[item] = {}
            self.__string_var[item]['stringvar'] = sv
            self.__string_var[item]['isbool'] = True if self.__items[item].lower() in ("true", "false") else False
            self.__string_var[item]['isnum'] = self.__items[item].replace('.','').isdigit()
            # self.sv.trace_add("write", lambda sv=self.sv: self.retrieve_changes(sv))
            self.__string_var[item]['entry'] = customtkinter.CTkEntry(master=self.sub_frame, width=225, placeholder_text=self.__items[item],
                    validate="focusout", textvariable=self.__string_var[item]['stringvar'],
                    validatecommand=lambda main_key=self.__name, sub_key=item: self.retrieve_changes(main_key, sub_key))
            self.__string_var[item]['entry'].grid(row=idx, column=1, columnspan=1, rowspan=1, sticky="e", padx=(0, 15))

    def retrieve_changes(self, main_key: str, sub_key: str):
        changed_val = self.__string_var[sub_key]['stringvar'].get()
        
        if changed_val:
            this_cell_type = ''
            if self.__string_var[sub_key]['isbool']:
                this_cell_type = 'bool'
            elif self.__string_var[sub_key]['isnum']:
                this_cell_type = 'num'
            else:
                this_cell_type = 'str'

            valid_bool_val = changed_val.lower() in ("true", "false") and self.__string_var[sub_key]['isbool']
            valid_num_val = changed_val.replace('.','',1).isdigit() and self.__string_var[sub_key]['isnum']

            if main_key not in self.config_changes:
                self.config_changes[main_key] = {}

            if this_cell_type == 'bool':
                if valid_bool_val:
                    self.__string_var[sub_key]['entry'].config(highlightthickness=0, highlightbackground=None)
                    self.config_changes[main_key][sub_key] = changed_val
                    if self.save_button.state == customtkinter.DISABLED: 
                        self.save_button.configure(state=customtkinter.NORMAL)
                else:
                    self.__string_var[sub_key]['entry'].config(highlightthickness=0.5, highlightbackground='#731d1d')
                    self.__string_var[sub_key]['entry'].delete(0, customtkinter.END)
            elif valid_num_val and this_cell_type == 'num':
                if valid_num_val:
                    self.__string_var[sub_key]['entry'].config(highlightthickness=0, highlightbackground=None)
                    self.config_changes[main_key][sub_key] = changed_val
                    if self.save_button.state == customtkinter.DISABLED: 
                        self.save_button.configure(state=customtkinter.NORMAL)
                else:
                    self.__string_var[sub_key]['entry'].config(highlightthickness=0.5, highlightbackground='#731d1d')
                    self.__string_var[sub_key]['entry'].delete(0, customtkinter.END)
            else:
                self.config_changes[main_key][sub_key] = changed_val
                if self.save_button.state == customtkinter.DISABLED: 
                    self.save_button.configure(state=customtkinter.NORMAL)
        if not changed_val and main_key in self.config_changes and sub_key in self.config_changes[main_key].keys():
            del self.config_changes[main_key][sub_key]
            if not list(self.config_changes[main_key].keys()):
                del self.config_changes[main_key]
            if not list(self.config_changes.keys()):
                if self.save_button.state == customtkinter.NORMAL: 
                    self.save_button.configure(state=customtkinter.DISABLED)
        return True

    def clear_fields(self):
        for sub_key in self.__string_var.keys():
            self.__string_var[sub_key]['entry'].config(highlightthickness=0, highlightbackground=None)
            self.__string_var[sub_key]['entry'].delete(0, customtkinter.END)