import flet as ft
from loguru import logger

import ui
from storage import storage


logger.add("error.log", format="{time} {level} {message}", level="ERROR")


@logger.catch
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
        view=ft.WEB_BROWSER if settings.web_mode else ft.FLET_APP
    )
