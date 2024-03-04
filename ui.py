from __future__ import annotations

import copy
import os
import time
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Callable

import flet as ft
import pyperclip

from storage import storage, Record


FONT_FAMILY = "Consolas"


class UnlockPage(ft.UserControl):

    def __init__(self, cb_unlock: Callable) -> None:
        super(UnlockPage, self).__init__()
        self.cb_unlock = cb_unlock
        self._field_1: ft.TextField = ...
        self._field_2: ft.TextField = ...
        self._field_3: ft.TextField = ...
        self._field_4: ft.TextField = ...

    @property
    def fields(self) -> list[ft.TextField]:
        return [self._field_1, self._field_2, self._field_3, self._field_4]

    @property
    def pin(self) -> str:
        symbols = [f.value or "" for f in self.fields]
        return "".join(symbols)

    def is_filled(self) -> bool:
        return all([f.value for f in self.fields])

    def build(self) -> ft.Column:

        def on_field_change(e: ft.ControlEvent):
            if self.is_filled():
                self.cb_unlock(self.pin)
                return
            field = e.control
            if (field is self._field_1) and self._field_1.value:
                self._field_2.focus()
            elif (field is self._field_2) and self._field_2.value:
                self._field_3.focus()
            elif (field is self._field_3) and self._field_3.value:
                self._field_4.focus()
            elif (field is self._field_4) and self._field_4.value:
                self._field_1.focus()

        self._field_1 = ft.TextField(
            width=75,
            focused_border_color="0xff9ecaff",
            cursor_color="0xff202429",
            text_style=ft.TextStyle(
                color="0xff9ecaff",
                font_family=FONT_FAMILY,
                size=36,
                weight=ft.FontWeight.BOLD
            ),
            border=ft.InputBorder.UNDERLINE,
            border_width=5,
            border_color="0xff9ecaff",
            bgcolor="0xff202429",
            text_align=ft.TextAlign.CENTER,
            max_length=1,
            on_change=on_field_change
        )
        self._field_2 = copy.deepcopy(self._field_1)
        self._field_3 = copy.deepcopy(self._field_1)
        self._field_4 = copy.deepcopy(self._field_1)
        self._field_1.autofocus = True

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._field_1,
                        self._field_2,
                        self._field_3,
                        self._field_4
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            animate_opacity=ft.animation.Animation(duration=100)
        )

    def reset(self) -> None:
        for field in self.fields:
            field.value = ""
        self._field_1.focus()
        self.update()


class RecordCard(ft.UserControl):

    gradient_1 = ["0xff38824f", "0xffab7717"]
    gradient_2 = ["0xff20997f", "0xff992057"]

    class State(Enum):
        DEFAULT = auto()
        SELECTED_LOGIN = auto()
        SELECTED_PASSWORD = auto()

    def __init__(self, record: Record, cb_click: Callable):
        super(RecordCard, self).__init__()
        self._record = record
        self._text_1: ft.Text = ...
        self._text_2: ft.Text = ...
        self._container: ft.Container = ...
        self._state: RecordCard.State = ...
        self.cb_click = cb_click

    @property
    def record(self) -> Record:
        return self._record

    @property
    def state(self) -> RecordCard.State:
        return self._state

    def build(self) -> ft.Container:
        self._text_1 = ft.Text(
            value=self._record.name,
            text_align=ft.TextAlign.CENTER,
            size=18,
            font_family=FONT_FAMILY,
            color="black",
        )
        self._text_2 = ft.Text(
            value=self._record.login,
            text_align=ft.TextAlign.CENTER,
            size=18,
            font_family=FONT_FAMILY,
            color="black"
        )
        self._container = ft.Container(
            content=ft.Column(
                controls=[self._text_1, self._text_2],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            width=350,
            height=60,
            border_radius=10,
            border=ft.border.all(1, "black"),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_left,
                colors=self.gradient_1
            ),
            on_click=self._on_click,
            opacity=0.7
        )
        return self._container

    def set_state(self, state: RecordCard.State) -> None:
        if state == self.State.DEFAULT:
            self._text_1.value = self._record.name
            self._text_2.value = self._record.login
            self._container.gradient.colors = self.gradient_1
        elif state == self.State.SELECTED_LOGIN:
            self._text_1.value = self._record.name
            self._text_2.value = self._record.login
            self._container.gradient.colors = self.gradient_2
        elif state == self.State.SELECTED_PASSWORD:
            self._text_1.value = self._record.name
            self._text_2.value = self._record.password
            self._container.gradient.colors = self.gradient_2
        self._state = state
        self.update()

    def _on_click(self, e: ft.ControlEvent):
        self.cb_click(self)


class RecordListPage(ft.UserControl):

    def __init__(self) -> None:
        super(RecordListPage, self).__init__()
        self.filter_string = ""
        self._selected_card = None

    @property
    def selected_card(self) -> Optional[RecordCard]:
        return self._selected_card

    def build(self) -> ft.Column:
        return ft.Column(
            controls=self._build_cards(),
            scroll=ft.ScrollMode.AUTO,
            animate_opacity=ft.animation.Animation(duration=100),
            height=480
        )

    def reset(self) -> None:
        self.controls[0].controls = self._build_cards()
        self.update()

    def _build_cards(self) -> list[RecordCard]:
        records = storage.get_records()
        if self.filter_string:
            records = [
                rec for rec in records
                if (self.filter_string.lower() in rec.name.lower())
                or (self.filter_string.lower() in rec.login.lower())
            ]
        return [
            RecordCard(
                record=record,
                cb_click=self._on_card_click
            )
            for record in records
        ]

    def _on_card_click(self, card: RecordCard):

        if card is self._selected_card:
            if card.state == RecordCard.State.SELECTED_LOGIN:
                card.set_state(RecordCard.State.SELECTED_PASSWORD)
                pyperclip.copy(card.record.password)
                storage.update_use_time(card.record)
            elif card.state == RecordCard.State.SELECTED_PASSWORD:
                card.set_state(RecordCard.State.DEFAULT)
                pyperclip.copy("")
                self._selected_card = None
            return

        if self._selected_card:
            self._selected_card.set_state(RecordCard.State.DEFAULT)
            self._selected_card = None

        card.set_state(RecordCard.State.SELECTED_LOGIN)
        pyperclip.copy(card.record.login)
        self._selected_card = card


class SearchPage(ft.UserControl):

    def __init__(self, cb_search_click: Callable) -> None:
        super(SearchPage, self).__init__()
        self.cb_search_click = cb_search_click

    def build(self) -> ft.Column:
        return ft.Column(
            controls=[
                ft.TextField(
                    label="Filter",
                    color="black",
                    focused_border_color="black",
                    cursor_color="black",
                    label_style=ft.TextStyle(color="black"),
                    text_style=ft.TextStyle(color="black"),
                    autofocus=True
                ),
                ft.ProgressBar(width=340, value=0),
                ft.ElevatedButton(
                    text="Search",
                    width=340,
                    on_click=self._on_btn_search_click
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            animate_opacity=ft.animation.Animation(duration=100)
        )

    def _on_btn_search_click(self, e: ft.ControlEvent):
        text_field = self.controls[0].controls[0]
        progress_bar = self.controls[0].controls[1]
        for i in range(1, 51):
            progress_bar.value = 0.02 * i
            time.sleep(0.01)
            self.update()
        self.cb_search_click(text_field.value)


class AddRecordPage(ft.UserControl):

    def __init__(self, cb_save_click: Callable) -> None:
        super(AddRecordPage, self).__init__()
        self.cb_save_click = cb_save_click

    @property
    def text_fields(self) -> list[ft.TextField]:
        return self.controls[0].controls[:3]

    def build(self) -> ft.Column:
        return ft.Column(
            controls=[
                ft.TextField(
                    label="Name",
                    color="black",
                    focused_border_color="black",
                    cursor_color="black",
                    label_style=ft.TextStyle(color="black"),
                    text_style=ft.TextStyle(color="black")
                ),
                ft.TextField(
                    label="Login",
                    color="black",
                    focused_border_color="black",
                    cursor_color="black",
                    label_style=ft.TextStyle(color="black"),
                    text_style=ft.TextStyle(color="black")
                ),
                ft.TextField(
                    label="Password",
                    color="black",
                    focused_border_color="black",
                    cursor_color="black",
                    label_style=ft.TextStyle(color="black"),
                    text_style=ft.TextStyle(color="black")
                ),
                ft.ElevatedButton(
                    text="Save",
                    width=340,
                    on_click=self._on_btn_save_click
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            animate_opacity=ft.animation.Animation(duration=100)
        )

    def reset(self):
        for field in self.text_fields:
            field.value = ""
            field.update()

    def _on_btn_save_click(self, e: ft.ControlEvent):
        name, login, password = [field.value for field in self.text_fields]
        record = Record(
            name=name,
            login=login,
            password=password,
            use_time=datetime.now()
        )
        self.cb_save_click(record)


class Screen(ft.UserControl):

    def __init__(self,
                 unlock_page: UnlockPage,
                 record_list_page: RecordListPage,
                 search_page: SearchPage,
                 add_record_page: AddRecordPage
                 ) -> None:

        super(Screen, self).__init__()
        self._unlock_page = unlock_page
        self._record_list_page = record_list_page
        self._search_page = search_page
        self._add_record_page = add_record_page

    @property
    def pages(self) -> list[ft.UserControl]:
        return [
            self._unlock_page,
            self._add_record_page,
            self._record_list_page,
            self._search_page,
        ]

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Stack(
                controls=[
                    self._unlock_page,
                    self._add_record_page,
                    self._record_list_page,
                    self._search_page
                ]
            ),
            width=370,
            height=480,
            border_radius=4,
            bgcolor="0xffc1c4ca",
            alignment=ft.alignment.center,
            padding=10
        )

    def show_unlock_page(self) -> None:
        for page in self.pages:
            page.visible = False
        self._unlock_page.visible = True
        self.update()

    def show_add_record_page(self) -> None:
        for page in self.pages:
            page.visible = False
        self._add_record_page.visible = True
        self._add_record_page.reset()
        self.update()

    def show_record_list_page(self) -> None:
        for page in self.pages:
            page.visible = False
        self._record_list_page.visible = True
        self.update()

    def show_search_page(self) -> None:
        for page in self.pages:
            page.visible = False
        self._search_page.visible = True
        self.update()


class Frame(ft.UserControl):

    def __init__(self, screen: Screen) -> None:
        super(Frame, self).__init__()
        self._screen = screen

    def build(self) -> ft.Container:
        return ft.Container(
            content=self._screen,
            width=390,
            height=560,
            border_radius=20,
            border=ft.border.all(1, "white"),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["0xff343434", "0xff000000"]
            ),
            alignment=ft.alignment.center
        )


class ButtonBar(ft.UserControl):

    def __init__(self,
                 cb_list_click: Callable,
                 cb_add_click: Callable,
                 cb_filter_click: Callable,
                 cb_delete_click: Callable,
                 cb_file_click: Callable
                 ) -> None:

        super(ButtonBar, self).__init__()
        self.cb_list_click = cb_list_click
        self.cb_add_click = cb_add_click
        self.cb_filter_click = cb_filter_click
        self.cb_delete_click = cb_delete_click
        self.cb_file_click = cb_file_click

    @property
    def buttons(self) -> list[ft.IconButton]:
        return self.controls[0].content.controls[1:6]

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=110
                    ),
                    ft.IconButton(
                        icon=ft.icons.LIST,
                        icon_color="0xff424242",
                        icon_size=20
                    ),
                    ft.IconButton(
                        icon=ft.icons.SEARCH,
                        icon_color="0xff424242",
                        icon_size=20
                    ),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        icon_color="0xff424242",
                        icon_size=20
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color="0xff424242",
                        icon_size=20
                    ),
                    ft.IconButton(
                        icon=ft.icons.FILE_OPEN,
                        icon_color="0xff424242",
                        icon_size=20
                    ),
                    ft.Container(
                        width=110
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            ),
            width=390,
            height=40,
            border_radius=ft.border_radius.only(
                bottom_left=20,
                bottom_right=20
            ),
            alignment=ft.alignment.center,
            bottom=0
        )

    def enable(self) -> None:
        for button in self.buttons:
            button.disabled = False
            button.icon_color = "white"
        self.buttons[0].on_click = self._on_btn_list_click
        self.buttons[1].on_click = self._on_btn_filter_click
        self.buttons[2].on_click = self._on_btn_add_click
        self.buttons[3].on_click = self._on_btn_delete_click
        self.buttons[4].on_click = self._on_btn_file_click
        self.update()

    def _on_btn_list_click(self, e: ft.ControlEvent):
        self.cb_list_click()

    def _on_btn_add_click(self, e: ft.ControlEvent):
        self.cb_add_click()

    def _on_btn_filter_click(self, e: ft.ControlEvent):
        self.cb_filter_click()

    def _on_btn_delete_click(self, e: ft.ControlEvent):
        self.cb_delete_click()

    def _on_btn_file_click(self, e: ft.ControlEvent):
        self.cb_file_click()


class Lamp(ft.UserControl):

    class State(Enum):
        OFF = auto()
        RED = auto()
        GREEN = auto()

    def __init__(self) -> None:
        super(Lamp, self).__init__()
        self._state = self.State.OFF

    @property
    def gradient_colors(self) -> dict[State, list[str]]:
        return {
            self.State.OFF: ["black", "black"],
            self.State.RED: ["0xffff0000", "0xfffe6e6e"],
            self.State.GREEN: ["0xff2eff00", "0xffa6f895"]
        }

    def build(self) -> ft.Container:
        return ft.Container(
            width=6,
            height=6,
            border_radius=3,
            gradient=ft.RadialGradient(colors=self.gradient_colors[self.State.OFF]),
            alignment=ft.alignment.center,
            right=0,
            margin=16,
            animate=ft.animation.Animation(duration=200),
            on_animation_end=self._on_animation_end
        )

    def blink_red(self) -> None:
        # Выключение лампы произойдет за счет функции _on_animation_end
        self._set_state(self.State.RED)

    def blink_green(self) -> None:
        # Выключение лампы произойдет за счет функции _on_animation_end
        self._set_state(self.State.GREEN)

    def _set_state(self, state: Lamp.State) -> None:
        self._state = state
        self.controls[0].gradient.colors = self.gradient_colors[state]
        self.update()

    def _on_animation_end(self, e: ft.ControlEvent):
        if self._state != self.State.OFF:
            self._set_state(self.State.OFF)


class Device(ft.UserControl):

    def __init__(self, page: ft.Page) -> None:
        super(Device, self).__init__()
        self._page = page
        self._is_locked = True

        self._unlock_page = UnlockPage(cb_unlock=self._on_unlock_click)
        self._record_list_page = RecordListPage()
        self._search_page = SearchPage(cb_search_click=self._on_search_click)
        self._add_record_page = AddRecordPage(cb_save_click=self._on_save_click)

        self._screen = Screen(
            unlock_page=self._unlock_page,
            record_list_page=self._record_list_page,
            search_page=self._search_page,
            add_record_page=self._add_record_page
        )
        self._frame = Frame(screen=self._screen)
        self._button_bar = ButtonBar(
            cb_list_click=self._on_list_click,
            cb_add_click=self._on_add_click,
            cb_filter_click=self._on_filter_click,
            cb_delete_click=self._on_delete_click,
            cb_file_click=self._on_file_click
        )
        self._lamp = Lamp()

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Stack(
                controls=[
                    self._frame,
                    self._button_bar,
                    self._lamp
                ]
            ),
            width=390,
            height=560,
            border_radius=20
        )

    def setup(self) -> None:
        self._screen.show_unlock_page()

    def _on_unlock_click(self, password: str) -> None:
        settings = storage.get_settings()
        if password == settings.pin:
            self._is_locked = False
            self._button_bar.enable()
            self._screen.show_record_list_page()
            self._lamp.blink_green()
        else:
            self._unlock_page.reset()
            self._lamp.blink_red()

    def _on_save_click(self, record: Record) -> None:
        if not record.name:
            self._lamp.blink_red()
            return
        storage.add_record(record)
        self._record_list_page.reset()
        self._lamp.blink_green()

    def _on_search_click(self, filter_string: str) -> None:
        self._record_list_page.filter_string = filter_string
        self._record_list_page.reset()
        self._screen.show_record_list_page()
        self._lamp.blink_green()

    def _on_list_click(self) -> None:
        if self._is_locked:
            return
        self._screen.show_record_list_page()

    def _on_add_click(self) -> None:
        if self._is_locked:
            return
        self._screen.show_add_record_page()

    def _on_filter_click(self) -> None:
        if self._is_locked:
            return
        self._screen.show_search_page()

    def _on_delete_click(self) -> None:

        if self._is_locked:
            return

        if not self._record_list_page.selected_card:
            self._lamp.blink_red()
            return
        record = self._record_list_page.selected_card.record

        def on_accept(e: ft.ControlEvent):
            storage.delete_record(record)
            dlg_modal.open = False
            self._page.update()
            self._record_list_page.reset()
            self._screen.show_record_list_page()
            self._lamp.blink_green()

        def on_reject(e: ft.ControlEvent):
            dlg_modal.open = False
            self._page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to delete this record?"),
            actions=[
                ft.TextButton("Yes", on_click=on_accept),
                ft.TextButton("No", on_click=on_reject),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self._page.dialog = dlg_modal
        dlg_modal.open = True
        self._page.update()

    def _on_file_click(self) -> None:
        os.startfile(storage.file_path)
