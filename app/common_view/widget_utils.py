"""Utility functions for widgets."""
import customtkinter
from settings import ConstSettings

### Utility functions for widgets ###

def init_placeholder(widget: customtkinter.CTkEntry, placeholder_text: str) -> None:
    """
    Initialize the placeholder of the entry box.

    Parameters
    ----------
    widget : customtkinter.CTkEntry
        The entry box.
    placeholder_text : str
        The placeholder text.
    """
    # set the placeholder
    widget.placeholder = placeholder_text
    if widget.get() == "": # if the entry box is empty, set the placeholder
        widget.insert(customtkinter.END, placeholder_text)

    # set up a binding to remove placeholder text
    widget.bind("<FocusIn>", lambda args: __focus_in_entry_box(widget, placeholder_text))
    widget.bind("<FocusOut>", lambda args: __focus_out_entry_box(widget, placeholder_text))

### Helper functions for utility functions ###

def __focus_out_entry_box(widget: customtkinter.CTkEntry, widget_text: str) -> None:
    """
    Action to perform when focus out of the entry box.

    Parameters
    ----------
    widget : customtkinter.CTkEntry
        The entry box.
    widget_text : str
        The text of the entry box.
    """
    # if the entry box is empty or the same, set the placeholder
    if len(widget.get()) == 0 or widget.get() == widget_text:
        widget.delete(0, customtkinter.END)
        widget.insert(0, widget_text)

def __focus_in_entry_box(widget: customtkinter.CTkEntry, widget_text: str) -> None:
    """
    Action to perform when focus in the entry box.

    Parameters
    ----------
    widget : customtkinter.CTkEntry
        The entry box.
    widget_text : str
        The text of the entry box.
    remove_highlight : bool, optional
        Whether to remove the highlight of the entry box, by default False
    """
    # if the entry box is the same as the placeholder, clear the entry box
    if widget.get() == widget_text:
        widget.delete(0, customtkinter.END)
        widget.configure(border_color=ConstSettings.DEFAULT_ENTRY_BORDER_COLOR) # reset the border color
