from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from config import app_dir
from utils import YAMLFile, DatetimeFormatter


@dataclass
class Record:
    name: str
    login: str
    password: str
    use_time: datetime

    def __eq__(self, other: Record) -> bool:
        if (self.name, self.login, self.password) == (other.name, other.login, other.password):
            return True
        return False

    @classmethod
    def from_dict(cls, dct: dict) -> Record:
        df = DatetimeFormatter()
        return Record(
            name=dct["name"],
            login=dct["login"],
            password=dct["password"],
            use_time=df.str_2_dt(dct["use_time"])
        )

    def to_dict(self) -> dict:
        df = DatetimeFormatter()
        return {
            "name": self.name,
            "login": self.login,
            "password": self.password,
            "use_time": df.dt_2_str(self.use_time)
        }


@dataclass
class Settings:
    pin: str
    web_mode: bool

    @classmethod
    def from_dict(cls, dct: dict) -> Settings:
        return Settings(
            pin=dct["pin"],
            web_mode=dct["web_mode"]
        )

    def to_dict(self) -> dict:
        return {
            "pin": self.pin,
            "web_mode": self.web_mode
        }


class Storage:

    dir_path = Path.home() / app_dir
    file_path = dir_path / "data.yml"

    def __init__(self):
        self.dir_path.mkdir(exist_ok=True)
        self._file = YAMLFile(self.file_path)
        if not self._file.path.exists():
            self._file.write({
                "settings": {"pin": "0000", "web_mode": False},
                "records": []
            })

    def get_settings(self) -> Settings:
        return Settings.from_dict(self._file.read()["settings"])

    def get_records(self) -> list[Record]:
        records = [Record.from_dict(dct) for dct in self._file.read()["records"]]
        records.sort(key=lambda x: x.use_time, reverse=True)
        return records

    def set_records(self, records: list[Record]) -> None:
        data = self._file.read()
        data["records"] = [r.to_dict() for r in records]
        self._file.write(data)

    def add_record(self, record: Record):
        self.set_records(self.get_records() + [record])

    def delete_record(self, record: Record):
        records = self.get_records()
        records.remove(record)
        self.set_records(records)

    def update_use_time(self, record: Record):
        records = self.get_records()
        idx = records.index(record)
        record.use_time = datetime.now()
        records[idx] = record
        self.set_records(records)


storage = Storage()
