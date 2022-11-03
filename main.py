import os
import signal
import threading
import time

import psutil

from app.app import App
from app.view_window import ViewWindow
from backend.common.config import Config

DEBUG_ENABLED = True

app = App(debug=DEBUG_ENABLED)

def monitor_process(config: Config):
    """ Check if the client is still running with given pid. """
    while(psutil.pid_exists(config.pid)):
        time.sleep(1)
    config.close_mem()
    os.kill(os.getpid(), signal.SIGTERM)

if __name__ == "__main__":
    try:
        app.mainloop()
    except KeyboardInterrupt:
        os.kill(os.getpid(), signal.SIGTERM)
    config = Config(debug=DEBUG_ENABLED)
    if config.await_process():
        config.set_address()
        app.update_text(config)
        ViewWindow(app, config, DEBUG_ENABLED)
        threading.Thread(target=monitor_process, args=[config]).start()


