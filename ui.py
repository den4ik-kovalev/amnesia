import copy as cp
import time
import typing as t

import flet as ft
import pyperclip

import config
import service


class App(ft.UserControl):

    class UnlockPage(ft.UserControl):

        def __init__(self, on_unlock_click: callable) -> None:
            super(App.UnlockPage, self).__init__()
            self.on_unlock_click = on_unlock_click

        def build(self) -> ft.Column:

            def on_field_1_change(e: ft.ControlEvent):
                if field_1.value:
                    field_2.focus()

            def on_field_2_change(e: ft.ControlEvent):
                if field_2.value:
                    field_3.focus()

            def on_field_3_change(e: ft.ControlEvent):
                if field_3.value:
                    field_4.focus()

            def on_field_4_change(e: ft.ControlEvent):
                if (
                    field_1.value
                    and field_2.value
                    and field_3.value
                    and field_4.value
                ):
                    self._on_unlock_click(e)

                if field_4.value:
                    field_4.focus()

            field_1 = ft.TextField(
                width=50,
                focused_border_color="0xff9ecaff",
                cursor_color="0xff202429",
                text_style=ft.TextStyle(
                    color="0xff9ecaff",
                    font_family=config.font_family,
                    size=36,
                    weight=ft.FontWeight.BOLD
                ),
                border=ft.InputBorder.UNDERLINE,
                border_width=5,
                border_color="0xff9ecaff",
                bgcolor="0xff202429",
                text_align=ft.TextAlign.CENTER,
                max_length=1,
                on_change=on_field_1_change
            )

            field_2 = cp.deepcopy(field_1)
            field_3 = cp.deepcopy(field_1)
            field_4 = cp.deepcopy(field_1)

            field_1.autofocus = True
            field_1.on_change = on_field_1_change
            field_2.on_change = on_field_2_change
            field_3.on_change = on_field_3_change
            field_4.on_change = on_field_4_change

            return ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            field_1,
                            field_2,
                            field_3,
                            field_4
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY
                    ),
                    ft.ElevatedButton(
                        text="Unlock",
                        width=240,
                        on_click=self._on_unlock_click
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                animate_opacity=ft.animation.Animation(duration=100)
            )

        def reset(self) -> None:
            text_fields = self.controls[0].controls[0].controls[:4]  # type: t.List[ft.TextField]
            for field in text_fields:
                field.value = ""
            text_fields[0].focus()
            self.update()

        def _on_unlock_click(self, e: ft.ControlEvent) -> None:
            text_fields = self.controls[0].controls[0].controls[:4]  # type: t.List[ft.TextField]
            pin = "".join([field.value for field in text_fields])
            self.on_unlock_click(pin)


    class RecordListPage(ft.UserControl):

        def __init__(self) -> None:
            super(App.RecordListPage, self).__init__()
            self.filter_string = ""
            self._selected_container = None  # type: t.Optional[App.RecordListPage.RecordContainer]

        class RecordContainer(ft.UserControl):

            def __init__(self, record: service.Record, on_click: callable):
                super(App.RecordListPage.RecordContainer, self).__init__()
                self.record = record
                self.on_click = on_click

            def build(self) -> ft.Container:
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                value=self.record.name,
                                text_align=ft.TextAlign.CENTER,
                                size=18,
                                font_family=config.font_family,
                                color="white"
                            ),
                            ft.Text(
                                value=self.record.login,
                                text_align=ft.TextAlign.CENTER,
                                size=18,
                                font_family=config.font_family,
                                color="white"
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    width=250,
                    height=60,
                    border_radius=10,
                    border=ft.border.all(1, "black"),
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_left,
                        colors=config.gradient_1
                    ),
                    on_click=self._on_click
                )

            def _on_click(self, e: ft.ControlEvent):
                self.on_click(self)

        @property
        def selected_container(self) -> t.Optional[RecordContainer]:
            return self._selected_container

        def build(self) -> ft.Column:
            return ft.Column(
                controls=self._build_containers(),
                scroll=ft.ScrollMode.AUTO,
                animate_opacity=ft.animation.Animation(duration=100),
                height=480
            )

        def reset(self) -> None:
            self.controls[0].controls = self._build_containers()
            self.update()

        def _build_containers(self) -> t.List['App.RecordListPage.RecordContainer']:
            records = service.Service.get_data()
            if self.filter_string:
                records = [rec for rec in records if self.filter_string in rec.name]
            return [
                self.RecordContainer(
                    record=record,
                    on_click=self._on_container_click
                )
                for record in records
            ]

        def _on_container_click(self, container: 'App.RecordListPage.RecordContainer'):
            if self._selected_container:
                if self._selected_container is container:
                    self._selected_container.controls[0].gradient.colors = config.gradient_1
                    self._selected_container.update()
                    self._selected_container = None
                    return
                else:
                    self._selected_container.controls[0].gradient.colors = config.gradient_1
                    self._selected_container.update()
            self._selected_container = container
            self._selected_container.controls[0].gradient.colors = config.gradient_2
            self._selected_container.update()
            pyperclip.copy(self._selected_container.record.password)


    class SearchPage(ft.UserControl):

        def __init__(self, on_search_click: callable) -> None:
            super(App.SearchPage, self).__init__()
            self.on_search_click = on_search_click

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
                    ),
                    ft.ProgressBar(width=240, value=0),
                    ft.ElevatedButton(
                        text="Search",
                        width=240,
                        on_click=self._on_search_click
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                animate_opacity=ft.animation.Animation(duration=100)
            )

        def _on_search_click(self, e: ft.ControlEvent):
            text_field = self.controls[0].controls[0]
            progress_bar = self.controls[0].controls[1]
            for i in range(1, 51):
                progress_bar.value = 0.02 * i
                time.sleep(0.01)
                self.update()
            self.on_search_click(text_field.value)


    class AddRecordPage(ft.UserControl):

        def __init__(self, on_save_click: callable) -> None:
            super(App.AddRecordPage, self).__init__()
            self.on_save_click = on_save_click

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
                        width=240,
                        on_click=self._on_save_click
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                animate_opacity=ft.animation.Animation(duration=100)
            )

        def reset(self):
            text_fields = self.controls[0].controls[:3]  # type: t.List[ft.TextField]
            for field in text_fields:
                field.value = ""
                field.update()

        def _on_save_click(self, e: ft.ControlEvent):
            text_fields = self.controls[0].controls[:3]  # type: t.List[ft.TextField]
            name, login, password = [field.value for field in text_fields]
            record = service.Record(
                name=name,
                login=login,
                password=password
            )
            self.on_save_click(record)


    class Screen(ft.UserControl):

        def __init__(self,
                     unlock_page: 'App.UnlockPage',
                     add_record_page: 'App.AddRecordPage',
                     record_list_page: 'App.RecordListPage',
                     search_page: 'App.SearchPage',
                     ) -> None:

            super(App.Screen, self).__init__()
            self._unlock_page = unlock_page
            self._add_record_page = add_record_page
            self._record_list_page = record_list_page
            self._search_page = search_page

        @property
        def pages(self):
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
                width=270,
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

        def __init__(self, screen: 'App.Screen') -> None:
            super(App.Frame, self).__init__()
            self._screen = screen

        def build(self) -> ft.Container:
            return ft.Container(
                content=self._screen,
                width=290,
                height=560,
                border_radius=20,
                border=ft.border.all(1, "white"),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[
                        "0xff343434",
                        "0xff000000"
                    ]
                ),
                alignment=ft.alignment.center
            )


    class ButtonBar(ft.UserControl):

        def __init__(self,
                     on_list_click: callable,
                     on_add_click: callable,
                     on_filter_click: callable,
                     on_delete_click: callable
                     ) -> None:

            super(App.ButtonBar, self).__init__()
            self.on_list_click = on_list_click
            self.on_add_click = on_add_click
            self.on_filter_click = on_filter_click
            self.on_delete_click = on_delete_click

        def build(self) -> ft.Container:
            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=60
                        ),
                        ft.IconButton(
                            icon=ft.icons.LIST,
                            icon_color="0xff424242",
                            icon_size=20
                        ),
                        ft.IconButton(
                            icon=ft.icons.ADD,
                            icon_color="0xff424242",
                            icon_size=20
                        ),
                        ft.IconButton(
                            icon=ft.icons.SEARCH,
                            icon_color="0xff424242",
                            icon_size=20
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color="0xff424242",
                            icon_size=20
                        ),
                        ft.Container(
                            width=60
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY
                ),
                width=290,
                height=40,
                border_radius=ft.border_radius.only(
                    bottomLeft=20,
                    bottomRight=20
                ),
                alignment=ft.alignment.center,
                bottom=0
            )

        def enable(self):
            buttons = self.controls[0].content.controls[1:5]  # type: t.List[ft.IconButton]
            lb, ab, fb, db = buttons
            lb.disabled = False
            ab.disabled = False
            fb.disabled = False
            db.disabled = False
            lb.icon_color = "white"
            ab.icon_color = "white"
            fb.icon_color = "white"
            db.icon_color = "white"
            lb.on_click = self._on_list_click
            ab.on_click = self._on_add_click
            fb.on_click = self._on_filter_click
            db.on_click = self._on_delete_click
            self.update()

        def _on_list_click(self, e: ft.ControlEvent):
            self.on_list_click()

        def _on_add_click(self, e: ft.ControlEvent):
            self.on_add_click()

        def _on_filter_click(self, e: ft.ControlEvent):
            self.on_filter_click()

        def _on_delete_click(self, e: ft.ControlEvent):
            self.on_delete_click()


    class Lamp(ft.UserControl):

        OFF = 0
        RED = 1
        GREEN = 2

        red_gradient = [
            "0xffff0000",
            "0xfffe6e6e"
        ]

        green_gradient = [
            "0xff2eff00",
            "0xffa6f895"
        ]

        black_gradient = [
            "black",
            "black"
        ]

        def __init__(self) -> None:
            super(App.Lamp, self).__init__()
            self._state = self.OFF

        def build(self) -> ft.Container:
            return ft.Container(
                width=6,
                height=6,
                border_radius=3,
                gradient=ft.RadialGradient(colors=self.black_gradient),
                alignment=ft.alignment.center,
                right=0,
                margin=16,
                animate=ft.animation.Animation(duration=200),
                on_animation_end=self._on_animation_end
            )

        def blink_red(self) -> None:
            self._turn_red()

        def blink_green(self) -> None:
            self._turn_green()

        def _turn_red(self) -> None:
            self._state = self.RED
            self.controls[0].gradient.colors = self.red_gradient
            self.update()

        def _turn_green(self) -> None:
            self._state = self.GREEN
            self.controls[0].gradient.colors = self.green_gradient
            self.update()

        def _turn_off(self) -> None:
            self._state = self.OFF
            self.controls[0].gradient.colors = self.black_gradient
            self.update()

        def _on_animation_end(self, e: ft.ControlEvent):
            if self._state != self.OFF:
                self._turn_off()

    def __init__(self, page: ft.Page) -> None:
        super(App, self).__init__()
        self._page = page
        self._locked = True

        self._unlock_page = self.UnlockPage(on_unlock_click=self._on_unlock_click)
        self._add_record_page = self.AddRecordPage(on_save_click=self._on_save_click)
        self._record_list_page = self.RecordListPage()
        self._search_page = self.SearchPage(on_search_click=self._on_search_click)

        self._screen = self.Screen(
            unlock_page=self._unlock_page,
            add_record_page=self._add_record_page,
            record_list_page=self._record_list_page,
            search_page=self._search_page,
        )
        self._frame = self.Frame(screen=self._screen)
        self._button_bar = self.ButtonBar(
            on_list_click=self._on_list_click,
            on_add_click=self._on_add_click,
            on_filter_click=self._on_filter_click,
            on_delete_click=self._on_delete_click
        )
        self._lamp = self.Lamp()

    def build(self) -> ft.Container:
        return ft.Container(
            content=ft.Stack(
                controls=[
                    self._frame,
                    self._button_bar,
                    self._lamp
                ]
            ),
            width=290,
            height=560,
            border_radius=20
        )

    def setup(self) -> None:
        self._screen.show_unlock_page()

    def _unlock(self) -> None:
        self._locked = False

    def _on_unlock_click(self, password: str) -> None:
        settings = service.Service.get_settings()
        if password == settings.pin:
            self._unlock()
            self._button_bar.enable()
            self._screen.show_record_list_page()
            self._lamp.blink_green()
        else:
            self._unlock_page.reset()
            self._lamp.blink_red()

    def _on_save_click(self, record: service.Record) -> None:
        if not record.name:
            self._lamp.blink_red()
            return
        data = service.Service.get_data()
        data.append(record)
        service.Service.save_data(data)
        self._record_list_page.reset()
        self._lamp.blink_green()

    def _on_search_click(self, filter_string: str) -> None:
        self._record_list_page.filter_string = filter_string
        self._record_list_page.reset()
        self._screen.show_record_list_page()
        self._lamp.blink_green()

    def _on_list_click(self) -> None:
        if self._locked:
            return
        self._screen.show_record_list_page()

    def _on_add_click(self) -> None:
        if self._locked:
            return
        self._screen.show_add_record_page()

    def _on_filter_click(self) -> None:
        if self._locked:
            return
        self._screen.show_search_page()

    def _on_delete_click(self) -> None:

        if self._locked:
            return

        if not self._record_list_page.selected_container:
            self._lamp.blink_red()
            return
        record = self._record_list_page.selected_container.record

        def on_accept(e: ft.ControlEvent):
            service.Service.delete_record(record)
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
