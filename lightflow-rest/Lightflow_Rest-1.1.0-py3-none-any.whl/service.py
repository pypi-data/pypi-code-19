from lightflow.config import Config
from lightflow_rest.core.app import create_app


config = Config()
config.load_from_file()

app = create_app(config)
