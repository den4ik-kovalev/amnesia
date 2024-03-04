import flet
import flet as ft

import ui
from storage import storage


def main(page: ft.Page):
    page.title = "Amnesia"
    page.theme_mode = "dark"
    page.padding = 10
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 460
    page.window_height = 640
    page.window_resizable = False

    device = ui.Device(page=page)
    page.add(device)
    device.setup()

    page.update()


if __name__ == '__main__':
    settings = storage.get_settings()
    ft.app(
        target=main,
        view=flet.WEB_BROWSER if settings.web_mode else flet.FLET_APP
    )
