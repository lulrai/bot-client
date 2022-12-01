"""
File containing the popup classes
"""
from typing import Any
import customtkinter

class Popups():
    """This class is used to create popups for the application"""
    @staticmethod
    def two_button_popup(parent_frame, parent_coords: tuple[int, int],
                         parent_dim: tuple[int, int], popup_dim: tuple[int, int],
                         popup_title: str, popup_desc: str,
                         first_button_text: str, second_button_text: str,
                         popup_desc_color: str = None,
                         first_button_text_color: str = None, first_button_hover_color: str = None, first_button_bg_color: str = None,
                         first_button_command = None, first_button_args: dict[str, Any] = None,
                         second_button_text_color: str = "#A52A2A", second_button_hover_color: str ="#731d1d", second_button_bg_color: str = None,
                         second_button_command = None, second_button_args: dict[str, Any] = None):
        """
        Creates a popup with two buttons.

        Parameters
        ----------
        parent_frame : tkinter.Frame
            The parent frame of the popup.
        parent_coords : tuple[int, int]
            The coordinates of the parent frame.
        parent_dim : tuple[int, int]
            The dimensions of the parent frame.
        popup_dim : tuple[int, int]
            The dimensions of the popup.
        popup_title : str
            The title of the popup.
        popup_desc : str
            The description of the popup.
        popup_desc_color : str, None
            The color of the description of the popup.
        first_button_text : str
            The text of the first button.
        second_button_text : str
            The text of the second button.
        first_button_text_color : str, optional
            The text color of the first button, by default None
        first_button_hover_color : str, optional
            The hover color of the first button, by default None
        first_button_bg_color : str, optional
            The background color of the first button, by default None
        second_button_text_color : str, optional
            The text color of the second button, by default "#A52A2A"
        second_button_hover_color : str, optional
            The hover color of the second button, by default "#731d1d"
        second_button_bg_color : str, optional
            The background color of the second button, by default None
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
        popout_x = int((parent_coords[0]+parent_dim[0]/2) - (popup_dim[0]/2))
        popout_y = int((parent_coords[1]+parent_dim[1]/2) - (popup_dim[1]/2))
        popout.geometry(f"{popup_dim[0]}x{popup_dim[1]}+{popout_x}+{popout_y}")
        # Disable resize
        popout.resizable(False, False)

        # Set the title and the information
        popout.title(popup_title)
        if popup_desc_color:
            label = customtkinter.CTkLabel(master=popout, text=popup_desc, text_color=popup_desc_color)
        else:
            label = customtkinter.CTkLabel(master=popout, text=popup_desc)
        label.pack(pady=(13, 30))
        first_button_args = first_button_args if first_button_args else {'popup': popout}
        if first_button_text_color:
            minimize_button = customtkinter.CTkButton(master=popout, text=first_button_text, command=lambda: first_button_command(**first_button_args), fg_color=first_button_text_color, hover_color=first_button_hover_color, bg_color=first_button_bg_color)
        else:
            minimize_button = customtkinter.CTkButton(master=popout, text=first_button_text, command=lambda: first_button_command(**first_button_args), hover_color=first_button_hover_color, bg_color=first_button_bg_color)
        minimize_button.place(relx=0.27, rely=0.68, anchor=customtkinter.CENTER)
        second_button_args = second_button_args if second_button_args else {'popup': popout}
        if second_button_text_color:
            quit_button = customtkinter.CTkButton(master=popout, text=second_button_text, command=lambda: second_button_command(**second_button_args) if second_button_command else popout.destroy(), fg_color=second_button_text_color, hover_color=second_button_hover_color, bg_color=second_button_bg_color)
        else:
            quit_button = customtkinter.CTkButton(master=popout, text=second_button_text, command=lambda: second_button_command(**second_button_args) if second_button_command else popout.destroy(), hover_color=second_button_hover_color, bg_color=second_button_bg_color)
        quit_button.place(relx=0.73, rely=0.68, anchor=customtkinter.CENTER)
        
        # Grab the focus in the dialog window
        popout.grab_set()