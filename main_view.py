import flet as ft
from reservation_controller import reservation_controller
from reservation_model import Reservation

BG       = "#1a202c"
SURFACE  = "#2d3748"
CARD     = "#252d3d"
ACCENT   = "#90cdf4"
TEXT     = "#f7fafc"
MUTED    = "#a0aec0"
BORDER   = "#4a5568"
SUCCESS  = "#48bb78"
WARNING  = "#f6ad55"
DANGER   = "#fc8181"
INFO     = "#63b3ed"

STATUS_COLOR = {
    "Confirmed":   SUCCESS,
    "Checked In":  INFO,
    "Checked Out": "#7f8c8d",
    "Cancelled":   DANGER,
    "Pending":     WARNING,
}

ROOM_TYPES = [
    "Standard", "Deluxe", "Suite", "Presidential Suite",
    "Single", "Double", "Twin", "Family Room",
]
STATUSES = ["Confirmed", "Pending", "Checked In", "Checked Out", "Cancelled"]


def _btn_content(text, icon, color):
    children = []
    if icon:
        children.append(ft.Icon(icon, size=16, color=color))
    children.append(ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=color))
    return ft.Row(children, spacing=6, tight=True)


def _btn(text, on_click, icon=None, bgcolor=ACCENT, fgcolor="#1a202c"):
    return ft.ElevatedButton(
        content=_btn_content(text, icon, fgcolor),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=18, vertical=10),
        ),
    )


def _ghost(text, on_click, icon=None):
    return ft.OutlinedButton(
        content=_btn_content(text, icon, MUTED),
        on_click=on_click,
        style=ft.ButtonStyle(
            side=ft.BorderSide(1, BORDER),
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        ),
    )


def _field(label, value="", hint="", expand=True, multiline=False,
           keyboard=ft.KeyboardType.TEXT, width=None, read_only=False,
           password=False):
    return ft.TextField(
        label=label,
        value=str(value),
        hint_text=hint,
        expand=expand,
        multiline=multiline,
        min_lines=2 if multiline else 1,
        max_lines=4 if multiline else 1,
        keyboard_type=keyboard,
        width=width,
        read_only=read_only,
        password=password,
        can_reveal_password=password,
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        label_style=ft.TextStyle(color=MUTED, size=12),
        text_style=ft.TextStyle(color=TEXT, size=13),
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=12),
    )


def _dropdown(label, options, value=None, expand=True, width=None):
    chosen = value if value in options else options[0]
    return ft.Dropdown(
        label=label,
        value=chosen,
        options=[ft.dropdown.Option(key=o, content=ft.Text(o, color=TEXT, size=13)) for o in options],
        expand=expand,
        width=width,
        bgcolor=SURFACE,
        border_color=BORDER,
        focused_border_color=ACCENT,
        color=TEXT,
        label_style=ft.TextStyle(color=MUTED, size=12),
        text_style=ft.TextStyle(color=TEXT, size=13),
        border_radius=8,
        content_padding=ft.padding.symmetric(horizontal=14, vertical=4),
    )


def _stat_card(title, value, icon_name, color=ACCENT):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon_name, color=color, size=20),
                ft.Text(title, color=MUTED, size=12, weight=ft.FontWeight.W_500),
            ], spacing=6),
            ft.Text(str(value), color=TEXT, size=26, weight=ft.FontWeight.W_700),
        ], spacing=8),
        bgcolor=CARD,
        border=ft.border.all(1, BORDER),
        border_radius=12,
        padding=ft.padding.all(20),
        expand=True,
    )


def _status_badge(status: str):
    color = STATUS_COLOR.get(status, "#888888")
    return ft.Container(
        content=ft.Text(status, color="white", size=10,
                        weight=ft.FontWeight.W_600),
        bgcolor=color,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def _role_badge(role: str):
    color = ACCENT if role == "admin" else INFO
    return ft.Container(
        content=ft.Text(role.upper(), color="#1a202c" if role == "admin" else "white",
                        size=9, weight=ft.FontWeight.W_700),
        bgcolor=color,
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )


class MainView:

    def __init__(self, page: ft.Page, controller: reservation_controller,
                 on_logout=None):
        self.page      = page
        self.ctrl      = controller
        self.on_logout = on_logout      # callable injected from main.py
        self._active   = "dashboard"

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )
        self._nav_btns: dict = {}


    def build(self):
        sidebar = self._sidebar()
        self.page.add(
            ft.Row(
                [
                    sidebar,
                    ft.VerticalDivider(width=1, color=BORDER),
                    ft.Container(
                        content=self.content,
                        expand=True,
                        padding=ft.padding.all(28),
                    ),
                ],
                expand=True,
                spacing=0,
            )
        )
        self._go("dashboard")

    def _sidebar(self):
        user = self.ctrl.current_user

        logo = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HOTEL, color=ACCENT, size=28),
                    ft.Text("AUREL", color=ACCENT, size=18,
                            weight=ft.FontWeight.W_800),
                ], spacing=8),
                ft.Text("Hotel Reservation System", color=MUTED, size=10),
            ], spacing=2),
            padding=ft.padding.only(left=20, top=24, bottom=20),
        )

        user_chip = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=MUTED, size=20),
                    ft.Column([
                        ft.Text(
                            user.full_name or user.username if user else "—",
                            color=TEXT, size=12, weight=ft.FontWeight.W_600,
                        ),
                        _role_badge(user.role if user else "staff"),
                    ], spacing=2, tight=True),
                ], spacing=8),
            ], spacing=0),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            margin=ft.margin.only(left=12, right=12, bottom=12),
        )

        NAV = [
            ("dashboard",       ft.Icons.SPACE_DASHBOARD,  "Dashboard"),
            ("reservations",    ft.Icons.TABLE_ROWS,        "Reservations"),
            ("register_guest",  ft.Icons.PERSON_ADD,        "Register Guest"),
            ("search",          ft.Icons.SEARCH,            "Search"),
            ("importexport",    ft.Icons.IMPORT_EXPORT,     "Import / Export"),
        ]
        if self.ctrl.is_admin():
            NAV.append(("admin", ft.Icons.ADMIN_PANEL_SETTINGS, "Admin Panel"))

        nav_col = ft.Column(spacing=2)
        for key, icon, label in NAV:
            btn = self._nav_item(key, icon, label)
            self._nav_btns[key] = btn
            nav_col.controls.append(btn)

        logout_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGOUT, size=16, color=DANGER),
                ft.Text("Logout", size=13, color=DANGER,
                        weight=ft.FontWeight.W_500),
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="transparent",
            border_radius=8,
            ink=True,
            on_click=self._do_logout,
        )

        return ft.Container(
            width=210,
            bgcolor=SURFACE,
            content=ft.Column(
                [
                    logo,
                    user_chip,
                    nav_col,
                    ft.Container(expand=True),
                    logout_btn,
                    ft.Container(
                        ft.Text("v3.0.0", color=MUTED, size=10),
                        padding=ft.padding.only(left=20, bottom=16),
                    ),
                ],
                expand=True,
                spacing=0,
            ),
        )

    def _do_logout(self, e):
        if self.on_logout:
            self.on_logout()

    def _nav_item(self, key, icon, label):
        active = (key == self._active)
        return ft.Container(
            key=key,
            content=ft.Row([
                ft.Icon(icon, size=18, color=ACCENT if active else MUTED),
                ft.Text(label, size=13, color=TEXT if active else MUTED,
                        weight=ft.FontWeight.W_500),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=CARD if active else "transparent",
            border=ft.border.only(
                left=ft.BorderSide(3, ACCENT if active else "transparent"),
            ),
            ink=True,
            on_click=lambda e, k=key: self._go(k),
        )

    def _go(self, key):
        self._active = key
        for k, btn in self._nav_btns.items():
            is_active = (k == key)
            btn.bgcolor = CARD if is_active else "transparent"
            btn.border = ft.border.only(
                left=ft.BorderSide(3, ACCENT if is_active else "transparent"),
            )
            row = btn.content
            row.controls[0].color = ACCENT if is_active else MUTED
            row.controls[1].color = TEXT   if is_active else MUTED

        dispatch = {
            "dashboard":      self._panel_dashboard,
            "reservations":   self._panel_reservations,
            "register_guest": self._panel_register_guest,
            "search":         self._panel_search,
            "importexport":   self._panel_importexport,
            "admin":          self._panel_admin,
        }
        panel_fn = dispatch.get(key)
        if panel_fn:
            self.content.controls = panel_fn()
        self.page.update()

    def _build_table(self, records: list, show_actions=True):
        columns = [
            ft.DataColumn(ft.Text("ID",         color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Guest Name", color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Room",       color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Type",       color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Check-In",   color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Check-Out",  color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Guests",     color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Price",      color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Status",     color=MUTED, size=11)),
        ]
        if show_actions:
            columns.append(ft.DataColumn(ft.Text("Actions", color=MUTED, size=11)))

        rows = []
        for r in records:
            cells = [
                ft.DataCell(ft.Text(str(r.id),        color=MUTED, size=12)),
                ft.DataCell(ft.Text(r.guest_name,     color=TEXT,  size=13,
                                    weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(r.room_number,    color=TEXT,  size=12)),
                ft.DataCell(ft.Text(r.room_type,      color=MUTED, size=12)),
                ft.DataCell(ft.Text(r.check_in,       color=MUTED, size=12)),
                ft.DataCell(ft.Text(r.check_out,      color=MUTED, size=12)),
                ft.DataCell(ft.Text(str(r.guests),    color=MUTED, size=12)),
                ft.DataCell(ft.Text(f"${r.total_price:,.2f}", color=ACCENT,
                                    size=12, weight=ft.FontWeight.W_600)),
                ft.DataCell(_status_badge(r.status)),
            ]
            if show_actions:
                cells.append(ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=INFO,
                            icon_size=18,
                            tooltip="Edit",
                            on_click=lambda e, rid=r.id: self._open_edit(rid),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_color=DANGER,
                            icon_size=18,
                            tooltip="Delete",
                            on_click=lambda e, rid=r.id: self._confirm_delete(rid),
                        ),
                    ], spacing=0)
                ))
            rows.append(ft.DataRow(cells=cells))

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, BORDER),
            border_radius=10,
            heading_row_color=SURFACE,
            heading_row_height=42,
            data_row_min_height=46,
            column_spacing=14,
            show_checkbox_column=False,
        )

    def _panel_dashboard(self):
        stats  = self.ctrl.get_stats()
        recent = self.ctrl.get_all()[:6]

        stat_row = ft.Row([
            _stat_card("Total Reservations", stats["total"],
                       ft.Icons.BOOK_ONLINE, ACCENT),
            _stat_card("Total Revenue",
                       f"${stats['revenue']:,.2f}",
                       ft.Icons.ATTACH_MONEY, SUCCESS),
            _stat_card("Confirmed", stats["confirmed"],
                       ft.Icons.CHECK_CIRCLE, SUCCESS),
            _stat_card("Checked In", stats["checked_in"],
                       ft.Icons.MEETING_ROOM, INFO),
        ], spacing=14)

        user = self.ctrl.current_user
        greeting = f"Welcome back, {user.full_name or user.username}!" if user else "Dashboard"

        return [
            ft.Text(greeting, color=TEXT, size=24,
                    weight=ft.FontWeight.W_700),
            ft.Text("Overview of your hotel reservations.",
                    color=MUTED, size=13),
            ft.Divider(color=BORDER, height=24),
            stat_row,
            ft.Container(height=24),
            ft.Text("Recent Reservations", color=TEXT, size=16,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=8),
            ft.Row([self._build_table(recent)], scroll=ft.ScrollMode.AUTO),
        ]

    def _panel_reservations(self, records=None):
        data = records if records is not None else self.ctrl.get_all()

        header = ft.Row([
            ft.Text(f"All Reservations  ({len(data)})", color=TEXT,
                    size=20, weight=ft.FontWeight.W_700, expand=True),
            _ghost("Refresh", lambda e: self._go("reservations"),
                   ft.Icons.REFRESH),
            ft.Container(width=8),
            _btn("Export Excel",
                 lambda e: self._do_quick_export(data),
                 ft.Icons.TABLE_CHART, SUCCESS, "#ffffff"),
        ])

        return [
            header,
            ft.Divider(color=BORDER, height=20),
            ft.Row([self._build_table(data)], scroll=ft.ScrollMode.AUTO),
        ]

    def _panel_add(self):
        return self._reservation_form(None)

    def _open_edit(self, rid: int):
        self._active = "reservations"
        self.content.controls = self._reservation_form(rid)
        self.page.update()


    def _reservation_form(self, rid=None):
        r = self.ctrl.get_by_id(rid) if rid is not None else None

        f_name   = _field("Guest Name *",  value=r.guest_name if r else "",  hint="Full name")
        f_room   = _dropdown("Room Number *",
                             ["101","102","103","104","105",
                              "106","107","108","109","110"],
                             value=r.room_number if r else None)
        f_type   = _dropdown("Room Type *", ROOM_TYPES, value=r.room_type if r else None)
        f_in     = _field("Check-In Date *",  value=r.check_in if r else "",  hint="YYYY-MM-DD")
        f_out    = _field("Check-Out Date *", value=r.check_out if r else "", hint="YYYY-MM-DD")
        f_guests = _field("Guests", value=str(r.guests) if r else "1",
                          keyboard=ft.KeyboardType.NUMBER)
        f_price  = _field("Total Price ($)", value=f"{r.total_price:.2f}" if r else "0.00",
                          keyboard=ft.KeyboardType.NUMBER)
        f_status = _dropdown("Status", STATUSES, value=r.status if r else None)
        f_notes  = _field("Notes", value=r.notes if r else "", multiline=True)

        msg_text = ft.Text("", size=12)

        def save(e):
            try:
                guests_val = int(f_guests.value or 1)
                price_val  = float(f_price.value or 0)
            except ValueError:
                msg_text.color = DANGER
                msg_text.value = "Guests must be a whole number; Price must be numeric."
                self.page.update()
                return

            kwargs = dict(
                guest_name  = f_name.value.strip(),
                room_number = f_room.value or "",
                room_type   = f_type.value or "",
                check_in    = f_in.value.strip(),
                check_out   = f_out.value.strip(),
                guests      = guests_val,
                total_price = price_val,
                status      = f_status.value or "Confirmed",
                notes       = f_notes.value.strip(),
            )

            if rid is None:
                ok, msg, _ = self.ctrl.add_reservation(**kwargs)
            else:
                ok, msg = self.ctrl.update_reservation(rid, **kwargs)

            msg_text.color = SUCCESS if ok else DANGER
            msg_text.value = msg
            self.page.update()
            if ok:
                self._go("reservations")

        title = f"Edit Reservation  #{rid}" if rid else "Add Reservation"

        form = ft.Container(
            content=ft.Column([
                ft.Text(title, color=ACCENT, size=20, weight=ft.FontWeight.W_700),
                ft.Divider(color=BORDER, height=16),
                ft.Row([f_name, f_room], spacing=14),
                ft.Row([f_type, f_status], spacing=14),
                ft.Row([f_in, f_out], spacing=14),
                ft.Row([f_guests, f_price], spacing=14),
                f_notes,
                ft.Container(height=4),
                ft.Row([
                    _btn("Save" if rid is None else "Update", save, ft.Icons.SAVE),
                    _ghost("Cancel", lambda e: self._go("reservations"), ft.Icons.CLOSE),
                ], spacing=12),
                msg_text,
            ], spacing=14),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.all(28),
            width=680,
        )

        crumb = "Reservations › Edit" if rid else "Reservations › Add"
        return [
            ft.Text(crumb, color=MUTED, size=12),
            ft.Container(height=12),
            form,
        ]

    def _confirm_delete(self, rid: int):
        def do_delete(e):
            dlg.open = False
            self.page.update()
            self.ctrl.delete_reservation(rid)
            self._go("reservations")

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete", color=DANGER,
                          weight=ft.FontWeight.W_700),
            content=ft.Text(
                f"Permanently delete reservation #{rid}?",
                color=MUTED,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", color=MUTED, size=13),
                    on_click=cancel,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Delete", color="white", size=13,
                                    weight=ft.FontWeight.W_600),
                    on_click=do_delete,
                    style=ft.ButtonStyle(
                        bgcolor=DANGER,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _panel_search(self):
        search_field = _field("Enter guest name…", expand=True)
        info_text  = ft.Text("", size=12, italic=True)
        result_col = ft.Column(controls=[], spacing=0)

        def run_search(e):
            q = search_field.value.strip()
            results, info = self.ctrl.binary_search_by_name(q)
            info_text.color = SUCCESS if results else WARNING
            info_text.value = info
            result_col.controls = [
                ft.Row([self._build_table(results)], scroll=ft.ScrollMode.AUTO),
            ]
            self.page.update()

        search_field.on_submit = run_search

        hint_box = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=MUTED, size=14),
                ft.Text(
                    "Binary Search does an exact case-insensitive match on Guest Name "
                    "using O(log n) binary search on a sorted array.",
                    color=MUTED, size=11, italic=True, expand=True,
                ),
            ], spacing=8),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=8,
            padding=ft.padding.all(12),
        )

        search_card = ft.Container(
            content=ft.Column([
                ft.Row([search_field,
                        _btn("Search", run_search, ft.Icons.SEARCH)],
                       spacing=12),
                ft.Container(height=4),
                info_text,
                hint_box,
            ], spacing=10),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.all(20),
        )

        return [
            ft.Text("Search Reservations", color=TEXT, size=20,
                    weight=ft.FontWeight.W_700),
            ft.Divider(color=BORDER, height=20),
            search_card,
            ft.Container(height=16),
            result_col,
        ]


    def _panel_importexport(self):
        csv_field  = _field("CSV File Path",
                            hint="e.g. C:\\data\\reservations.csv  or  /home/user/data.csv")
        xlsx_field = _field("Excel Output Path", value="hotel_export.xlsx")
        ie_msg     = ft.Text("", size=12)

        def set_msg(text, color):
            ie_msg.value = text
            ie_msg.color = color
            self.page.update()

        def browse_csv(e):
            """Open a native file dialog using tkinter (works on all platforms)."""
            import threading
            def _open():
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    path = filedialog.askopenfilename(
                        title="Select CSV file",
                        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    )
                    root.destroy()
                    if path:
                        csv_field.value = path
                        self.page.update()
                except Exception as ex:
                    set_msg(f"Could not open file dialog: {ex}", DANGER)
            threading.Thread(target=_open, daemon=True).start()

        def do_import(e):
            path = csv_field.value.strip()
            if not path:
                set_msg("Please enter or browse for the CSV file path.", DANGER)
                return
            set_msg("Importing...", MUTED)
            self.page.update()
            ok, msg = self.ctrl.import_csv(path)
            set_msg(msg, SUCCESS if ok else DANGER)
            if ok:
                self._go("reservations")

        def browse_save(e):
            """Open a native save dialog using tkinter."""
            import threading
            def _open():
                try:
                    import tkinter as tk
                    from tkinter import filedialog
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    path = filedialog.asksaveasfilename(
                        title="Save Excel file as",
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                        initialfile=xlsx_field.value.strip() or "hotel_export.xlsx",
                    )
                    root.destroy()
                    if path:
                        xlsx_field.value = path
                        self.page.update()
                except Exception as ex:
                    set_msg(f"Could not open save dialog: {ex}", DANGER)
            threading.Thread(target=_open, daemon=True).start()

        def do_export(e):
            path = xlsx_field.value.strip() or "hotel_export.xlsx"
            set_msg("Exporting...", MUTED)
            self.page.update()
            ok, msg = self.ctrl.export_excel(path)
            set_msg(msg, SUCCESS if ok else DANGER)

        how_to = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ACCENT, size=16),
                    ft.Text("How to import a CSV", color=ACCENT, size=13,
                            weight=ft.FontWeight.W_700),
                ], spacing=6),
                ft.Text("1.  Create a CSV file with these column headers:",
                        color=TEXT, size=12),
                ft.Container(
                    content=ft.Text(
                        "guest_name, room_number, room_type, check_in, check_out,\n"
                        "guests, total_price, status, notes",
                        color=ACCENT, size=11,
                        font_family="monospace",
                    ),
                    bgcolor=SURFACE,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ),
                ft.Text("2.  Dates must be in YYYY-MM-DD format  (e.g. 2025-06-15).",
                        color=MUTED, size=12),
                ft.Text("3.  room_number must be one of: 101 - 110.",
                        color=MUTED, size=12),
                ft.Text("4.  status can be: Confirmed, Pending, Checked In, "
                        "Checked Out, Cancelled.  Defaults to Confirmed if blank.",
                        color=MUTED, size=12),
                ft.Text("5.  Click Browse to pick the file, or paste the full path manually. "
                        "Then click Import CSV.",
                        color=MUTED, size=12),
            ], spacing=8),
            bgcolor=SURFACE,
            border=ft.border.all(1, BORDER),
            border_radius=10,
            padding=ft.padding.all(16),
        )

        import_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.UPLOAD_FILE, color=ACCENT, size=22),
                    ft.Text("CSV Import", color=TEXT, size=16,
                            weight=ft.FontWeight.W_600),
                ], spacing=8),
                how_to,
                ft.Divider(color=BORDER),
                ft.Row([
                    csv_field,
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=15, color=TEXT),
                            ft.Text("Browse", size=13, color=TEXT),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        on_click=browse_csv,
                        style=ft.ButtonStyle(
                            bgcolor=SURFACE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            side=ft.BorderSide(1, BORDER),
                            padding=ft.padding.symmetric(horizontal=16, vertical=14),
                        ),
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    _btn("Import CSV", do_import, ft.Icons.UPLOAD),
                ], spacing=12),
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.all(24),
        )

        export_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD, color=SUCCESS, size=22),
                    ft.Text("Excel Export", color=TEXT, size=16,
                            weight=ft.FontWeight.W_600),
                ], spacing=8),
                ft.Text(
                    "Export all reservations to a styled .xlsx file with "
                    "colour-coded statuses and a totals row.",
                    color=MUTED, size=12,
                ),
                ft.Divider(color=BORDER),
                ft.Row([
                    xlsx_field,
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN, size=15, color=TEXT),
                            ft.Text("Browse", size=13, color=TEXT),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        on_click=browse_save,
                        style=ft.ButtonStyle(
                            bgcolor=SURFACE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            side=ft.BorderSide(1, BORDER),
                            padding=ft.padding.symmetric(horizontal=16, vertical=14),
                        ),
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                _btn("Export to Excel", do_export,
                     ft.Icons.TABLE_CHART, SUCCESS, "#ffffff"),
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.all(24),
        )

        return [
            ft.Text("Import / Export", color=TEXT, size=20,
                    weight=ft.FontWeight.W_700),
            ft.Divider(color=BORDER, height=20),
            import_card,
            ft.Container(height=16),
            export_card,
            ft.Container(height=12),
            ie_msg,
        ]

    def _do_quick_export(self, records: list):
        path = "hotel_export.xlsx"
        ok, msg = self.ctrl.export_excel(path, records)
        snack = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=SUCCESS if ok else DANGER,
        )
        self.page.overlay.append(snack)
        snack.open = True
        self.page.update()

    

    def _panel_register_guest(self):
        """Quick guest info card + instant reservation booking form."""
        f_fname   = _field("Full Name *",     hint="Guest's full name", expand=True)
        f_phone   = _field("Phone Number",    hint="+63 9xx xxx xxxx",  expand=True,
                           keyboard=ft.KeyboardType.PHONE)
        f_email   = _field("Email Address",   hint="guest@example.com", expand=True,
                           keyboard=ft.KeyboardType.EMAIL)
        f_id_type = _dropdown("ID Type",
                              ["Passport", "Driver's License", "National ID",
                               "Voter's ID", "SSS / GSIS ID", "Other"],
                              expand=False, width=200)
        f_id_no   = _field("ID Number",       hint="Government-issued ID number", expand=True)
        f_address = _field("Home Address",    hint="City / Province", expand=True)
        f_notes   = _field("Special Requests / Notes", multiline=True, expand=True)

        f_room    = _dropdown("Room Number *",
                              ["101","102","103","104","105",
                               "106","107","108","109","110"],
                              expand=False, width=180)
        f_type    = _dropdown("Room Type *", ROOM_TYPES, expand=False, width=200)
        f_in      = _field("Check-In Date *",  hint="YYYY-MM-DD", expand=True)
        f_out     = _field("Check-Out Date *", hint="YYYY-MM-DD", expand=True)
        f_guests  = _field("Guests",           value="1",
                           keyboard=ft.KeyboardType.NUMBER, expand=False, width=120)
        f_price   = _field("Total Price ($)",  value="0.00",
                           keyboard=ft.KeyboardType.NUMBER, expand=True)
        f_status  = _dropdown("Status", STATUSES, expand=False, width=180)

        msg_text = ft.Text("", size=12)

        def register(e):
            # Validate guest name (required)
            if not f_fname.value.strip():
                msg_text.color = DANGER
                msg_text.value = "Guest full name is required."
                self.page.update()
                return
            try:
                guests_val = int(f_guests.value or 1)
                price_val  = float(f_price.value or 0)
            except ValueError:
                msg_text.color = DANGER
                msg_text.value = "Guests must be a whole number; Price must be numeric."
                self.page.update()
                return

            extra = []
            if f_phone.value.strip():
                extra.append(f"Phone: {f_phone.value.strip()}")
            if f_email.value.strip():
                extra.append(f"Email: {f_email.value.strip()}")
            if f_id_type.value and f_id_no.value.strip():
                extra.append(f"ID: {f_id_type.value} – {f_id_no.value.strip()}")
            if f_address.value.strip():
                extra.append(f"Address: {f_address.value.strip()}")
            if f_notes.value.strip():
                extra.append(f_notes.value.strip())
            combined_notes = " | ".join(extra)

            ok, msg, _ = self.ctrl.add_reservation(
                guest_name  = f_fname.value.strip(),
                room_number = f_room.value or "",
                room_type   = f_type.value or "",
                check_in    = f_in.value.strip(),
                check_out   = f_out.value.strip(),
                guests      = guests_val,
                total_price = price_val,
                status      = f_status.value or "Confirmed",
                notes       = combined_notes,
            )
            msg_text.color = SUCCESS if ok else DANGER
            msg_text.value = msg
            self.page.update()
            if ok:
                self._go("reservations")

        guest_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.PERSON_ADD, color=ACCENT, size=20),
                    ft.Text("Guest Information", color=ACCENT, size=15,
                            weight=ft.FontWeight.W_700),
                ], spacing=8),
                ft.Divider(color=BORDER, height=10),
                ft.Row([f_fname, f_phone], spacing=14),
                ft.Row([f_email, f_address], spacing=14),
                ft.Row([f_id_type, f_id_no], spacing=14),
                f_notes,
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.all(24),
        )

        reservation_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BOOK_ONLINE, color=INFO, size=20),
                    ft.Text("Reservation Details", color=INFO, size=15,
                            weight=ft.FontWeight.W_700),
                ], spacing=8),
                ft.Divider(color=BORDER, height=10),
                ft.Row([f_room, f_type, f_status], spacing=14),
                ft.Row([f_in, f_out], spacing=14),
                ft.Row([f_guests, f_price], spacing=14),
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=14,
            padding=ft.padding.all(24),
        )

        return [
            ft.Row([
                ft.Icon(ft.Icons.PERSON_ADD, color=ACCENT, size=22),
                ft.Text("Register Guest", color=TEXT, size=20,
                        weight=ft.FontWeight.W_700),
            ], spacing=10),
            ft.Text("Fill in guest details and create a reservation in one step.",
                    color=MUTED, size=13),
            ft.Divider(color=BORDER, height=20),
            guest_card,
            ft.Container(height=14),
            reservation_card,
            ft.Container(height=16),
            ft.Row([
                _btn("Register & Save", register, ft.Icons.HOW_TO_REG),
                _ghost("Cancel", lambda e: self._go("dashboard"), ft.Icons.CLOSE),
            ], spacing=12),
            ft.Container(height=8),
            msg_text,
        ]


    def _panel_admin(self):
        if not self.ctrl.is_admin():
            return [ft.Text("Access denied.", color=DANGER, size=16)]

        tab_ref = ft.Ref[ft.Tabs]()
        users_col = ft.Column(controls=[], spacing=0)
        msg_text  = ft.Text("", size=12)

        def refresh_users():
            users = self.ctrl.get_all_users()
            users_col.controls = [self._build_users_table(users, msg_text, refresh_users)]
            self.page.update()

        f_uname  = _field("Username *", hint="min 3 chars", expand=True)
        f_fname  = _field("Full Name",  hint="Display name", expand=True)
        f_pw     = _field("Password *", hint="min 6 chars", expand=True, password=True)
        f_role   = _dropdown("Role", ["staff", "admin"], expand=False, width=160)
        add_msg  = ft.Text("", size=12)

        def do_add_user(e):
            ok, msg = self.ctrl.add_user(
                username  = f_uname.value,
                password  = f_pw.value,
                role      = f_role.value or "staff",
                full_name = f_fname.value,
            )
            add_msg.color = SUCCESS if ok else DANGER
            add_msg.value = msg
            if ok:
                f_uname.value = ""
                f_fname.value = ""
                f_pw.value    = ""
                refresh_users()
            self.page.update()

        add_form = ft.Container(
            content=ft.Column([
                ft.Text("Add New User", color=ACCENT, size=15,
                        weight=ft.FontWeight.W_700),
                ft.Divider(color=BORDER, height=10),
                ft.Row([f_uname, f_fname], spacing=14),
                ft.Row([f_pw, f_role], spacing=14),
                ft.Row([
                    _btn("Create User", do_add_user, ft.Icons.PERSON_ADD),
                ], spacing=12),
                add_msg,
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.all(20),
        )

        f_old  = _field("Current Password",  password=True, expand=True)
        f_new1 = _field("New Password",      password=True, expand=True)
        f_new2 = _field("Confirm Password",  password=True, expand=True)
        pw_msg = ft.Text("", size=12)

        def do_change_pw(e):
            if f_new1.value != f_new2.value:
                pw_msg.color = DANGER
                pw_msg.value = "New passwords do not match."
                self.page.update()
                return
            ok, msg = self.ctrl.change_own_password(f_old.value, f_new1.value)
            pw_msg.color = SUCCESS if ok else DANGER
            pw_msg.value = msg
            if ok:
                f_old.value = f_new1.value = f_new2.value = ""
            self.page.update()

        pw_form = ft.Container(
            content=ft.Column([
                ft.Text("Change Your Password", color=ACCENT, size=15,
                        weight=ft.FontWeight.W_700),
                ft.Divider(color=BORDER, height=10),
                ft.Row([f_old, f_new1, f_new2], spacing=14),
                _btn("Update Password", do_change_pw, ft.Icons.LOCK_RESET),
                pw_msg,
            ], spacing=12),
            bgcolor=CARD,
            border=ft.border.all(1, BORDER),
            border_radius=12,
            padding=ft.padding.all(20),
        )

        refresh_users()

        return [
            ft.Row([
                ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, color=ACCENT, size=22),
                ft.Text("Admin Panel", color=TEXT, size=20,
                        weight=ft.FontWeight.W_700),
            ], spacing=10),
            ft.Divider(color=BORDER, height=20),

            ft.Text("System Users", color=TEXT, size=15,
                    weight=ft.FontWeight.W_600),
            ft.Container(height=8),
            users_col,
            ft.Container(height=20),
            msg_text,

            add_form,
            ft.Container(height=20),
            
            pw_form,
        ]


    def _build_users_table(self, users: list, msg_text: ft.Text, refresh_fn):
        columns = [
            ft.DataColumn(ft.Text("ID",        color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Username",  color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Full Name", color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Role",      color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Active",    color=MUTED, size=11)),
            ft.DataColumn(ft.Text("Actions",   color=MUTED, size=11)),
        ]

        rows = []
        for u in users:
            active_badge = ft.Container(
                content=ft.Text("Yes" if u.is_active else "No",
                                color="white", size=10,
                                weight=ft.FontWeight.W_600),
                bgcolor=SUCCESS if u.is_active else DANGER,
                border_radius=6,
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
            )
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(u.id),        color=MUTED, size=12)),
                ft.DataCell(ft.Text(u.username,       color=TEXT,  size=13,
                                    weight=ft.FontWeight.W_500)),
                ft.DataCell(ft.Text(u.full_name or "—", color=MUTED, size=12)),
                ft.DataCell(_role_badge(u.role)),
                ft.DataCell(active_badge),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color=INFO,
                        icon_size=18,
                        tooltip="Edit user",
                        on_click=lambda e, uid=u.id: self._open_edit_user(
                            uid, msg_text, refresh_fn),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LOCK_RESET,
                        icon_color=WARNING,
                        icon_size=18,
                        tooltip="Reset password",
                        on_click=lambda e, uid=u.id, uname=u.username:
                            self._reset_password_dialog(uid, uname, msg_text, refresh_fn),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=DANGER,
                        icon_size=18,
                        tooltip="Delete user",
                        on_click=lambda e, uid=u.id, uname=u.username:
                            self._confirm_delete_user(uid, uname, msg_text, refresh_fn),
                    ),
                ], spacing=0)),
            ]))

        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, BORDER),
            border_radius=10,
            heading_row_color=SURFACE,
            heading_row_height=42,
            data_row_min_height=46,
            column_spacing=14,
        )


    def _open_edit_user(self, uid: int, msg_text: ft.Text, refresh_fn):
        from reservation_model import User as UserModel
        u = self.ctrl.db.get_user_by_id(uid)
        if u is None:
            return

        f_uname  = _field("Username *",  value=u.username,  expand=True)
        f_fname  = _field("Full Name",   value=u.full_name, expand=True)
        f_role   = _dropdown("Role", ["staff", "admin"],
                             value=u.role, expand=False, width=160)
        active_cb = ft.Checkbox(
            label="Active",
            value=u.is_active,
            fill_color=ACCENT,
            check_color="#1a202c",
        )
        dlg_msg = ft.Text("", size=12)

        def do_save(e):
            ok, msg = self.ctrl.update_user(
                uid       = uid,
                username  = f_uname.value,
                role      = f_role.value or "staff",
                full_name = f_fname.value,
                is_active = active_cb.value,
            )
            dlg_msg.color = SUCCESS if ok else DANGER
            dlg_msg.value = msg
            self.page.update()
            if ok:
                dlg.open = False
                msg_text.color = SUCCESS
                msg_text.value = msg
                refresh_fn()

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Edit User  #{uid}", color=ACCENT,
                          weight=ft.FontWeight.W_700),
            content=ft.Column([
                ft.Row([f_uname, f_fname], spacing=14),
                ft.Row([f_role, active_cb], spacing=14),
                dlg_msg,
            ], spacing=12, width=480),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", color=MUTED, size=13),
                    on_click=cancel,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Save", color="#1a202c", size=13,
                                    weight=ft.FontWeight.W_600),
                    on_click=do_save,
                    style=ft.ButtonStyle(
                        bgcolor=ACCENT,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


    def _reset_password_dialog(self, uid: int, username: str,
                                msg_text: ft.Text, refresh_fn):
        f_pw1 = _field("New Password",     password=True, expand=True)
        f_pw2 = _field("Confirm Password", password=True, expand=True)
        dlg_msg = ft.Text("", size=12)

        def do_reset(e):
            if f_pw1.value != f_pw2.value:
                dlg_msg.color = DANGER
                dlg_msg.value = "Passwords do not match."
                self.page.update()
                return
            ok, msg = self.ctrl.reset_user_password(uid, f_pw1.value)
            dlg_msg.color = SUCCESS if ok else DANGER
            dlg_msg.value = msg
            self.page.update()
            if ok:
                dlg.open = False
                msg_text.color = SUCCESS
                msg_text.value = f"Password for '{username}' was reset."
                refresh_fn()

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Reset Password – {username}", color=WARNING,
                          weight=ft.FontWeight.W_700),
            content=ft.Column([
                ft.Row([f_pw1, f_pw2], spacing=14),
                dlg_msg,
            ], spacing=12, width=440),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", color=MUTED, size=13),
                    on_click=cancel,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Reset", color="white", size=13,
                                    weight=ft.FontWeight.W_600),
                    on_click=do_reset,
                    style=ft.ButtonStyle(
                        bgcolor=WARNING,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


    def _confirm_delete_user(self, uid: int, username: str,
                              msg_text: ft.Text, refresh_fn):
        def do_delete(e):
            dlg.open = False
            self.page.update()
            ok, msg = self.ctrl.delete_user(uid)
            msg_text.color = SUCCESS if ok else DANGER
            msg_text.value = msg
            if ok:
                refresh_fn()
            else:
                self.page.update()

        def cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete User", color=DANGER,
                          weight=ft.FontWeight.W_700),
            content=ft.Text(
                f"Permanently delete user '{username}'?",
                color=MUTED,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Cancel", color=MUTED, size=13),
                    on_click=cancel,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Delete", color="white", size=13,
                                    weight=ft.FontWeight.W_600),
                    on_click=do_delete,
                    style=ft.ButtonStyle(
                        bgcolor=DANGER,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            bgcolor=CARD,
            shape=ft.RoundedRectangleBorder(radius=12),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()