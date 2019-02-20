import os
import atlite
import logging
logger = logging.getLogger(__name__)

class Config(object):
    _SEARCH_PATHS =[
        os.path.expanduser("~"),
        os.path.dirname(atlite.__file__),
    ]

    _FILE_NAME = ".atlite_config.yaml"
    _DEFAULT_NAME = ".atlite_config.default.yaml"

    def __init__(self, config_dict=None, config_path=None):
        """Create a config object using a dictionary or by specifying a config file path."""

        # Add the following attributes to the instance
        # Manual adding, since __set_attr__ was overwritten
        attrs = [
            "cutout_dir",
            "ncep_dir",
            "cordex_dir",
            "sarah_dir",
            "windturbine_dir",
            "solarpanel_dir",
            "gebco_path",
        ]
        for a in attrs:
            self.__dict__[a] = None

        
        # Try to find a working config
        if config_dict and config_path:
            raise TypeError("Only one of {config_dict, config_path} "
                            "may be specified at a time")
        elif config_dict is not None:
            self.update(self, config_dict)
        elif config_path is not None:
            self.read(config_path)
        else:
            # Try to load configuration from standard paths
            paths = [os.path.join(sp, Config._FILE_NAME) for sp in Config._SEARCH_PATHS]
            for path in paths:
                if os.path.isfile(path):
                    self.read(path)
                    # Either successfully read or invalid file
                    break

            
            # Last attempt: fallback to default configuration
            path = os.path.join(os.path.dirname(atlite.__file__), Config._DEFAULT_NAME)
            if os.path.isfile(path):
                self.read(path)
    
    def read(self, path):
        """Read and set the configuration based on the file in 'path'."""
        import os
        import yaml

        if not os.path.isfile(path):
            raise TypeError("Invalid configuration file path.")
        
        with open(path, "r") as config_file:
            config_dict = yaml.safe_load(config_file)
            self.update(config_dict)

        logger.info("Configuration from {p} successfully read.".format(p=path))

    def update(self, config_dict):
        """Update the existing config based on the config_dict dictionary"""

        for key, val in config_dict.items():
            self.__setattr__(key, val)

    def __setattr__(self, key, value):
        """Only allow existing parameters to be set."""

        if hasattr(self, key):
            super().__setattr__(key, value)
        else:
            raise TypeError("Unknown configuration key {k}".format(k=key))
    
