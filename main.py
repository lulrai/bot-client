"""
Main file containing the main function.
"""
import os
import signal
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

from app.app import App
from backend.common.config import AppConfig

app_config = AppConfig() # Create the application config

if load_dotenv(): # Load the environment variables from the .env file
    logging.info('Loaded environment variables from .env file!')
else: # If the .env file is not found, disable syncing to the database
    logging.warning('Could not load environment variables from .env file!')
    logging.warning('Make sure you have a .env file in the root directory.')
    logging.warning('Disabled syncing to the database.')
    app_config.set_config(False, 'sync', 'enabled')

app = App(app_config=app_config) # Create the main application window

# Create a rotating log file
# Create the log folder if it doesn't exist
if not os.path.exists(app_config.get_config('log', 'folder')):
    os.makedirs(app_config.get_config('log', 'folder'))
handler = TimedRotatingFileHandler(filename=os.path.join(app_config.get_config('log', 'folder'), 'app.log'), 
                                   when='M',
                                   backupCount=app_config.get_config('log', 'backup_count'),
                                   encoding='utf-8', delay=False)

# Set up logging
logging.basicConfig(format='%(asctime)s %(name)s - %(levelname)s - %(message)s',
    level=app_config.get_config('log', 'level'),
    handlers=[handler],
    force=True)

# Main loop
if __name__ == "__main__":
    try:
        app.mainloop() # Start the main loop
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGTERM) # Kill the process if the user presses Ctrl+C
