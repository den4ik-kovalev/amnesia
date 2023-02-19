import flet
import flet as ft

import config
import service
import ui


def main(page: ft.Page):
    page.title = config.page_title
    page.theme_mode = "dark"
    page.padding = 10
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window_width = 460
    page.window_height = 640

    app = ui.App(page=page)
    page.add(app)
    app.setup()

    page.update()


if __name__ == '__main__':
    service.Service.setup()
    settings = service.Service.get_settings()
    ft.app(
        target=main,
        view=flet.WEB_BROWSER if settings.web_mode else flet.FLET_APP
    )
