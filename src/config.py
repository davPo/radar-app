#!/usr/bin/env python

import logging
import os

from configparser import RawConfigParser


default_config = {
    # Start location for the map (until either a chase car position, or balloon position is available.)
    "default_lat": 46.1,
    "default_lon": 6.01,
    "default_alt": 0,
    # radar period
    "radar_period": 15,  # Update predictor every 15 seconds.
    # Range Rings
    "range_rings_enabled": False,
    "range_ring_quantity": 5,
    "range_ring_spacing": 1000,
    "range_ring_weight": 1.5,
    "range_ring_color": "red",
    "range_ring_custom_color": "#FF0000",
    # Radar points
    "points_size": 1.0,
    "points_color": "black",
}

def parse_config_file(filename):
    """ Parse a Configuration File """

    radar_config = default_config.copy()

    config = RawConfigParser()
    config.read(filename)

    # Map Defaults
    radar_config["flask_host"] = config.get("map", "flask_host")
    radar_config["flask_port"] = config.getint("map", "flask_port")
    radar_config["default_lat"] = config.getfloat("map", "default_lat")
    radar_config["default_lon"] = config.getfloat("map", "default_lon")

    # Range Ring Settings
    radar_config["range_rings_enabled"] = config.getboolean(
        "range_rings", "range_rings_enabled"
    )
    radar_config["range_ring_quantity"] = config.getint(
        "range_rings", "range_ring_quantity"
    )
    radar_config["range_ring_spacing"] = config.getint(
        "range_rings", "range_ring_spacing"
    )
    radar_config["range_ring_weight"] = config.getfloat(
        "range_rings", "range_ring_weight"
    )
    radar_config["range_ring_color"] = config.get("range_rings", "range_ring_color")
    radar_config["range_ring_custom_color"] = config.get(
        "range_rings", "range_ring_custom_color"
    )

    radar_config["radar_period"] = config.getint("radar", "radar_period")

    radar_config["points_size"] = config.getfloat("display", "points_size")
    radar_config["points_color"] = config.get("display", "points_color")
   
    # Offline Map Settings
    radar_config["tile_server_enabled"] = config.getboolean(
        "offline_maps", "tile_server_enabled"
    )
    radar_config["tile_server_path"] = config.get("offline_maps", "tile_server_path")

    # Determine valid offline map layers.
    radar_config["offline_tile_layers"] = []
    if radar_config["tile_server_enabled"]:
        for _dir in os.listdir(radar_config["tile_server_path"]):
            if os.path.isdir(os.path.join(radar_config["tile_server_path"], _dir)):
                radar_config["offline_tile_layers"].append(_dir)
        logging.info("Found Map Layers: %s" % str(radar_config["offline_tile_layers"]))

    return radar_config


def read_config(filename, default_cfg="radar.cfg.example"):
    """ Read in a Radar configuration file,and return as a dict. """

    try:
        config_dict = parse_config_file(filename)
    except Exception as e:
        logging.error("Could not parse %s, trying default: %s" % (filename, str(e)))
        try:
            config_dict = parse_config_file(default_cfg)
        except Exception as e:
            logging.critical("Could not parse config file! - %s" % str(e))
            config_dict = None

    return config_dict


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG,
    )
    print(read_config(sys.argv[1]))
