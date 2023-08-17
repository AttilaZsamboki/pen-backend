from ..config_development import base_path as dev
from ..config_production import base_path as prod
from dotenv import load_dotenv
import os
load_dotenv()

base_path = dev if os.environ.get("ENVIRONMENT") == "development" else prod