"""
File containing the popup classes
"""
from typing import Any
from settings import ConstSettings
import customtkinter

class Popups():
    """This class is used to create popups for the application"""
    @staticmethod
    def two_button_popup(parent_frame,
                         parent_dim: tuple[int, int], popup_dim: tuple[int, int],
                         popup_title: str, popup_desc: str,
                         first_button_text: str, second_button_text: str,
                         popup_desc_color: str = ConstSettings.DEFAULT_DESC_COLOR,
                         first_button_text_color: str = ConstSettings.NORMAL_BUTTON_TEXT,
                         first_button_fg_color: str = ConstSettings.NORMAL_BUTTON_COLOR,
                         first_button_hover_color: str = ConstSettings.NORMAL_BUTTON_HOVER,
                         first_button_command = None, first_button_args: dict[str, Any] = None,
                         second_button_text_color: str = ConstSettings.ACTION_BUTTON_TEXT,
                         second_button_fg_color: str = ConstSettings.ACTION_BUTTON_COLOR,
                         second_button_hover_color: str = ConstSettings.ACTION_BUTTON_HOVER,
                         second_button_command = None, second_button_args: dict[str, Any] = None):
        """
        Creates a popup with two buttons.

        Parameters
        ----------
        parent_frame : tkinter.Frame
            The parent frame of the popup.
        parent_dim : tuple[int, int]
            The dimensions of the parent frame.
        popup_dim : tuple[int, int]
            The dimensions of the popup.
        popup_title : str
            The title of the popup.
        popup_desc : str
            The description of the popup.
        first_button_text : str
            The text of the first button.
        second_button_text : str
            The text of the second button.
        popup_desc_color : str, optional
            The color of the description, by default (light: "#000000", dark: "#FFFFFF")
        first_button_text_color : str, optional
            The text color of the first button, by default (light: "#000000", dark: "#FFFFFF")
        first_button_fg_color : str, optional
            The foreground color of the first button, by default (light: "#64B5F6", dark: "#1565C0")
        first_button_hover_color : str, optional
            The hover color of the first button, by default (light: "#42A5F5", dark: "#0D47A1")
        second_button_text_color : str, optional
            The text color of the second button, by default (light: "#000000", dark: "#FFFFFF")
        second_button_fg_color : str, optional
            The foreground color of the second button, by default (light: "#E57373", dark: "#C62828")
        second_button_hover_color : str, optional
            The hover color of the second button, by default (light: "#EF5350", dark: "#B71C1C")
        first_button_command : function, optional
            The command of the first button.
        first_button_args : tuple, optional
            The arguments of the first button command.
        second_button_command : function, optional
            The command of the second button, by default None
        second_button_args : tuple, optional
            The arguments of the second button command, by default None
        """
        # Create a top level dialog
        popout = customtkinter.CTkToplevel(parent_frame)
        popout.attributes('-topmost', 'true')

        # Placement of the dialog
        # calculate x and y coordinates for the dialog window
        popout_x = int((parent_frame.winfo_x()+parent_dim[0]/2) - (popup_dim[0]/2))
        popout_y = int((parent_frame.winfo_y()+parent_dim[1]/2) - (popup_dim[1]/2))
        popout.geometry(f"{popup_dim[0]}x{popup_dim[1]}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Set the title and the information
        popout.title(popup_title)
        label = customtkinter.CTkLabel(master=popout,
                                       text=popup_desc,
                                       text_color=popup_desc_color)
        label.pack(pady=(13, 30))

        first_button_args = first_button_args if first_button_args else {'popup': popout}
        minimize_button = customtkinter.CTkButton(master=popout,
                                                  text=first_button_text,
                                                  command=lambda:
                                                      first_button_command(**first_button_args),
                                                  text_color=first_button_text_color,
                                                  fg_color=first_button_fg_color,
                                                  hover_color=first_button_hover_color)
        minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)

        second_button_args = second_button_args if second_button_args else {'popup': popout}
        quit_button = customtkinter.CTkButton(master=popout,
                                              text=second_button_text,
                                              command=lambda:
                                                  second_button_command(**second_button_args) if second_button_command else popout.destroy(),
                                              text_color=second_button_text_color,
                                              fg_color=second_button_fg_color,
                                              hover_color=second_button_hover_color)
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)

        # Grab the focus in the dialog window
        popout.grab_set()
        popout.focus_set()
