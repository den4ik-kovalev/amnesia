import dataclasses as dc
import json
import os
import typing as t

import config

__all__ = ['Record', 'Service']


@dc.dataclass
class Record:
    name: str
    login: str
    password: str


@dc.dataclass
class Settings:
    pin: str
    web_mode: bool


class Service:

    @classmethod
    def setup(cls):
        if not os.path.exists(cls.data_filepath()):
            cls.save_data(data=[])
        if not os.path.exists(cls.settings_filepath()):
            cls.save_settings(
                settings=Settings(
                    pin=config.pin,
                    web_mode=config.web_mode
                )
            )

    @classmethod
    def app_dir(cls) -> str:
        appdir = os.path.join(os.path.expanduser('~'), config.app_dir)
        if not os.path.exists(appdir):
            os.mkdir(appdir)
        return appdir

    @classmethod
    def data_filepath(cls) -> str:
        return os.path.join(cls.app_dir(), "data.txt")

    @classmethod
    def settings_filepath(cls) -> str:
        return os.path.join(cls.app_dir(), "settings.txt")

    @classmethod
    def save_settings(cls, settings: Settings) -> None:
        with open(cls.settings_filepath(), "w") as file:
            json.dump(dc.asdict(settings), file)

    @classmethod
    def get_settings(cls) -> Settings:
        with open(cls.settings_filepath()) as file:
            obj = json.load(file)
        return Settings(**obj)

    @classmethod
    def save_data(cls, data: t.List[Record]) -> None:
        data = [dc.asdict(obj) for obj in data]
        with open(cls.data_filepath(), "w") as file:
            json.dump(data, file)

    @classmethod
    def get_data(cls) -> t.List[Record]:
        with open(cls.data_filepath()) as file:
            data = json.load(file)
        return [Record(**obj) for obj in data]

    @classmethod
    def delete_record(cls, record: Record) -> None:
        records = cls.get_data()
        records = [rec for rec in records if rec != record]
        cls.save_data(records)
