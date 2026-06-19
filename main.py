import flet as ft
from reservation_controller import reservation_controller
from main_view import MainView
from login_view import LoginView


def main(page: ft.Page):
    page.title         = "AUREL Hotel Reservation System"
    page.theme_mode    = ft.ThemeMode.DARK
    page.bgcolor       = "#1a202c"
    page.window_width  = 1200
    page.window_height = 800
    page.window_min_width  = 900
    page.window_min_height = 620
    page.padding       = 0

    controller = reservation_controller()

    def show_login():
        page.controls.clear()
        page.overlay.clear()

        def on_login_success():
            page.controls.clear()
            page.overlay.clear()
            view = MainView(page, controller, on_logout=show_login)
            view.build()
            page.update()

        login_view = LoginView(page, controller, on_login_success)
        login_view.build()

    show_login()


if __name__ == "__main__":
    ft.app(target=main)