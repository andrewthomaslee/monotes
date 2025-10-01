from pathlib import Path

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings

BASE_DIR: Path = Path(__file__).parent

# Create Jinja2 templates
templates: Jinja2Templates = Jinja2Templates(directory=BASE_DIR / "style" / "templates")


class ConfigSettings(BaseSettings):
    DB_URI: str = "mongodb://localhost:27017"
    SECRET_KEY: str = "should-be-changed"
    FAKE_DATA: bool = True


CONFIG_SETTINGS: ConfigSettings = ConfigSettings()
