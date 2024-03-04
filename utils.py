from datetime import datetime
from pathlib import Path

import yaml


class DatetimeFormatter:

    def __init__(self, fmt: str = "%Y-%m-%d %H:%M:%S"):
        self.fmt = fmt

    def dt_2_str(self, dt: datetime) -> str:
        return dt.strftime(self.fmt)

    def str_2_dt(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, self.fmt)


class YAMLFile:

    def __init__(self, path: Path) -> None:
        if path.suffix != ".yml":
            raise Exception("The file extension must be .yml")
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def read(self) -> dict:
        with open(self._path, "r") as file:
            return yaml.safe_load(file)

    def write(self, data: dict) -> None:
        with open(self._path, "w") as file:
            yaml.safe_dump(data, file)
