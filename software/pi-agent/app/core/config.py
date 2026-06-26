from pathlib import Path
import yaml

# software/pi-agent/config/config.yaml
CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "config"
    / "config.yaml"
)


class Config:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            self.data = yaml.safe_load(file)

    @property
    def app_name(self):
        return self.data["app"]["name"]

    @property
    def version(self):
        return self.data["app"]["version"]

    @property
    def environment(self):
        return self.data["app"]["environment"]

    @property
    def host(self):
        return self.data["server"]["host"]

    @property
    def port(self):
        return self.data["server"]["port"]

    @property
    def device_name(self):
        return self.data["device"]["name"]


config = Config()
