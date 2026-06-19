import flet as ft
from reservation_controller import reservation_controller

BG      = "#1a202c"
SURFACE = "#2d3748"
CARD    = "#252d3d"
ACCENT  = "#90cdf4"
TEXT    = "#f7fafc"
MUTED   = "#a0aec0"
BORDER  = "#4a5568"
SUCCESS = "#48bb78"
DANGER  = "#fc8181"
INFO    = "#63b3ed"


def _field(label, hint="", password=False, icon=None):
    return ft.TextField(
        label=label,
        hint_text=hint,
        prefix_icon=icon,
        password=password,
        can_reveal_password=password,
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        label_style=ft.TextStyle(color=MUTED, size=12),
        text_style=ft.TextStyle(color=TEXT, size=13),
        border_radius=10,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=14),
        width=320,
    )


class LoginView:

    def __init__(self, page: ft.Page, controller: reservation_controller,
                 on_success, on_logout=None):
        self.page       = page
        self.ctrl       = controller
        self.on_success = on_success
        self.on_logout  = on_logout

    def build(self):
        self.page.bgcolor = BG

        active_tab = {"value": "login"}   # "login" or "register"

        f_user = _field("Username", "Enter your username", icon=ft.Icons.PERSON_OUTLINE)
        f_pass = _field("Password", "Enter your password", password=True,
                        icon=ft.Icons.LOCK_OUTLINE)
        login_err  = ft.Text("", color=DANGER, size=12, text_align=ft.TextAlign.CENTER)
        login_ok   = ft.Text("", color=SUCCESS, size=12, text_align=ft.TextAlign.CENTER)
        loading    = ft.ProgressRing(width=20, height=20, stroke_width=2,
                                     color=ACCENT, visible=False)

        r_fname  = _field("Full Name",        "Your display name",   icon=ft.Icons.BADGE_OUTLINED)
        r_user   = _field("Username *",       "min 3 characters",    icon=ft.Icons.PERSON_OUTLINE)
        r_pass   = _field("Password *",       "min 6 characters",    password=True,
                          icon=ft.Icons.LOCK_OUTLINE)
        r_pass2  = _field("Confirm Password", "Re-enter password",   password=True,
                          icon=ft.Icons.LOCK_OUTLINE)

        reg_msg  = ft.Text("", size=12, text_align=ft.TextAlign.CENTER)

        login_panel = ft.Column([
            ft.Text("Sign in to your account", color=TEXT, size=16,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER),
            ft.Container(height=2),
            f_user,
            f_pass,
            ft.Container(height=2),
            login_err,
            login_ok,
            ft.Row([loading], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        register_panel = ft.Column([
            ft.Text("Create a new account", color=TEXT, size=16,
                    weight=ft.FontWeight.W_600,
                    text_align=ft.TextAlign.CENTER),
            ft.Container(height=2),
            r_fname,
            r_user,
            r_pass,
            r_pass2,
            ft.Container(height=2),
            reg_msg,
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           visible=False)

        tab_login_text = ft.Text("Sign In",  size=13, weight=ft.FontWeight.W_700,
                                  color="#1a202c")
        tab_reg_text   = ft.Text("Register", size=13, weight=ft.FontWeight.W_600,
                                  color=MUTED)

        tab_login = ft.Container(
            content=tab_login_text,
            bgcolor=ACCENT,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=28, vertical=10),
            ink=True,
        )
        tab_reg = ft.Container(
            content=tab_reg_text,
            bgcolor="transparent",
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=28, vertical=10),
            ink=True,
        )

        def switch_tab(tab: str):
            active_tab["value"] = tab
            if tab == "login":
                tab_login.bgcolor  = ACCENT
                tab_login_text.color = "#000000"
                tab_login_text.weight = ft.FontWeight.W_700
                tab_reg.bgcolor    = "transparent"
                tab_reg_text.color = MUTED
                tab_reg_text.weight = ft.FontWeight.W_600
                login_panel.visible    = True
                register_panel.visible = False
                action_btn.content = ft.Row([
                    ft.Icon(ft.Icons.LOGIN, size=16, color="#1a202c"),
                    ft.Text("Sign In", size=14, weight=ft.FontWeight.W_700, color="#1a202c"),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            else:
                tab_login.bgcolor  = "transparent"
                tab_login_text.color = MUTED
                tab_login_text.weight = ft.FontWeight.W_600
                tab_reg.bgcolor    = ACCENT
                tab_reg_text.color = "#000000"
                tab_reg_text.weight = ft.FontWeight.W_700
                login_panel.visible    = False
                register_panel.visible = True
                action_btn.content = ft.Row([
                    ft.Icon(ft.Icons.PERSON_ADD, size=16, color="#1a202c"),
                    ft.Text("Create Account", size=14, weight=ft.FontWeight.W_700,
                            color="#1a202c"),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
            self.page.update()

        tab_login.on_click = lambda e: switch_tab("login")
        tab_reg.on_click   = lambda e: switch_tab("register")

        tab_bar = ft.Container(
            content=ft.Row([tab_login, tab_reg], spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=SURFACE,
            border_radius=10,
            padding=ft.padding.all(4),
            border=ft.border.all(1, BORDER),
            width=320,
        )

        def do_login(e):
            login_err.value = ""
            login_ok.value  = ""
            loading.visible = True
            self.page.update()
            ok, msg, user = self.ctrl.login(f_user.value, f_pass.value)
            loading.visible = False
            if ok:
                self.on_success()
            else:
                login_err.value = msg
                f_pass.value    = ""
                self.page.update()

        def do_register(e):
            reg_msg.value = ""
            # client-side validation
            if r_pass.value != r_pass2.value:
                reg_msg.color = DANGER
                reg_msg.value = "Passwords do not match."
                self.page.update()
                return
            ok, msg = self.ctrl.add_user(
                username  = r_user.value,
                password  = r_pass.value,
                role      = "staff",
                full_name = r_fname.value,
            )
            reg_msg.color = SUCCESS if ok else DANGER
            reg_msg.value = msg
            if ok:
                reg_msg.value = f"{msg}  You can now sign in."
                # clear fields
                r_fname.value = r_user.value = r_pass.value = r_pass2.value = ""
            self.page.update()

        def on_action(e):
            if active_tab["value"] == "login":
                do_login(e)
            else:
                do_register(e)

        f_pass.on_submit  = do_login
        r_pass2.on_submit = do_register

        action_btn = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGIN, size=16, color="#1a202c"),
                ft.Text("Sign In", size=14, weight=ft.FontWeight.W_700, color="#1a202c"),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
            on_click=on_action,
            style=ft.ButtonStyle(
                bgcolor=ACCENT,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=24, vertical=14),
            ),
            width=320,
        )

        hint_box = ft.Container(
            content=ft.Column([
                ft.Text("Default credentials", color=MUTED, size=11,
                        weight=ft.FontWeight.W_600),
                ft.Text("Admin  →  admin / admin123", color=MUTED, size=11),
                ft.Text("Staff  →  staff / staff123",  color=MUTED, size=11),
            ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=8,
            padding=ft.padding.all(12),
            width=320,
        )

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.HOTEL, color=ACCENT, size=36),
                        ft.Column([
                            ft.Text("AUREL", color=ACCENT, size=24,
                                    weight=ft.FontWeight.W_800),
                            ft.Text("Hotel Reservation System",
                                    color=MUTED, size=11),
                        ], spacing=0),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),

                    ft.Divider(color=BORDER, height=24),

                    tab_bar,
                    ft.Container(height=4),
                    login_panel,
                    register_panel,
                    action_btn,
                    ft.Container(height=4),
                    hint_box,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=360,
            ),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=16,
            padding=ft.padding.all(36),
            width=460,
        )

        self.page.add(
            ft.Container(
                content=card,
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        self.page.update()
        f_user.focus()