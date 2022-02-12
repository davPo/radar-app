import json
import logging
import sys

import flask
from flask_socketio import SocketIO
import os
import time
from datetime import datetime, timedelta
#from dateutil.parser import parse
from math import sin, cos, radians, pi
import pyproj

from src.config import *
from src.daq import DAQ

# Define Flask Application, and allow automatic reloading of templates for dev work
app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True

# SocketIO instance
socketio = SocketIO(app,logger=True, engineio_logger=True)

# Global stores of data.

# These settings are shared between server and all clients, and are updated dynamically.
radar_config = {}

# Routes
#
#   Flask Routes
#

@app.route("/get_config")
def flask_get_config():
    return json.dumps(radar_config)

@app.route("/")
def home():
    #return app.send_static_file("index.html")
    return flask.render_template('index.html')

def flask_emit_event(event_name="none", data={}):
    """ Emit a socketio event to any clients. """
    socketio.emit(event_name, data, namespace="/radar")

@socketio.on("client_settings_update", namespace="/radar")
def client_settings_update(data):
    global radar_config, online_uploader

    # Overwrite local config data with data from the client.
    radar_config = data

    # Push settings back out to all clients.
    flask_emit_event("server_settings_update", radar_config)

class WebHandler(logging.Handler):
    """ Logging Handler for sending log messages via Socket.IO to a Web Client """

    def emit(self, record):
        """ Emit a log message via SocketIO """
        # Deal with log records with no content.
        if record.msg:
            if "socket.io" not in record.msg:
                # Convert log record into a dictionary
                log_data = {
                    "level": record.levelname,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "msg": record.msg,
                }
                # Emit to all socket.io clients
                socketio.emit("log_event", log_data, namespace="/radar")

def handle_new_data(data= [(34,4010), (129,1267)]):
    echoes = { "positions": [] }
    echoes['positions']=data   
    # Update the web client.
    flask_emit_event("data_event", echoes)
    logging.info("Push radar data : " + str(data) )

def new_data_callback(data):
    """ Handle a DAQ input message """
    output = []
    startLat = radar_config["default_lat"] # Home position
    startLon = radar_config["default_lon"]
    # data = [[0 , 5000], [90, 10000], [135, 20000]] # fixed points test
    for p in data:
        forwardAzimuth = p[0]
        distance = p[1]
        endLon,endLat,backAzimuth = (pyproj.Geod(ellps='WGS84').fwd(startLon,startLat,forwardAzimuth,distance))
        output.append([endLat, endLon])
    try:
        handle_new_data(output)
    except Exception as e:
        logging.error("Error Handling Radar Points - %s" % str(e))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="radar.cfg",
        help="Configuration file.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Verbose output."
    )
    parser.add_argument(
        "-l",
        "--log",
        type=str,
        default=None,
        help="Custom log file name. (Default: ./log_files/<timestamp>.log",
    )
    # parser.add_argument(
    #     "--nolog", action="store_true", default=False, help="Inhibit all logging."
    # )
    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        _log_level = logging.DEBUG
    else:
        _log_level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        stream=sys.stdout,
        level=_log_level,
    )
    # Make flask & socketio only output errors, not every damn GET request.
    logging.getLogger("requests").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("socketio").setLevel(logging.ERROR)
    logging.getLogger("engineio").setLevel(logging.ERROR)

  #  web_handler = WebHandler()
  #  logging.getLogger().addHandler(web_handler)

# create console handler and set level to debug

    # Read in config file.
    radar_config = read_config(args.config) #args.config
    # Quit if we cannot read a valid config file.
    if radar_config == None:
        logging.critical("Could not read configuration data. Exiting")
        sys.exit(1)

    # Add in version information.
    radar_config["version"] = 1.0

      # Copy out Offline Map Settings
    map_settings = {
        "tile_server_enabled": radar_config["tile_server_enabled"],
        "tile_server_path": radar_config["tile_server_path"],
    }

    daq_listener = DAQ(callback=new_data_callback)
    daq_listener.start()
    # Run the Flask app, which will block until CTRL-C'd.
    logging.info(
        "Starting Radar Server on: http://%s:%d/"
        % (radar_config["flask_host"], radar_config["flask_port"])
    )
    logging.debug(radar_config)
    socketio.run(
        app,
        host=radar_config["flask_host"],
        #port=radar_config["flask_port"] # local
        port = int(os.environ.get('PORT', 5000)) # heroku 
    )

    try:
        daq_listener.close()
    except Exception as e:
        logging.error("Error closing thread - %s" % str(e))




