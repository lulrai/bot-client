"""
Main file containing the main function.
"""
import os
import signal
import logging

from app.app import App

DEBUG_ENABLED = True # Set to True to enable debug mode

app = App(debug=DEBUG_ENABLED) # Create the main application window

# Set up logging
logging.basicConfig(filename='app.log',
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filemode='w',
    force=True)

# Main loop
if __name__ == "__main__":
    try:
        app.mainloop() # Start the main loop
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGTERM) # Kill the process if the user presses Ctrl+C
