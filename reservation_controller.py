from reservation_model import Reservation, ReservationDB, User


class reservation_controller:

    def __init__(self):
        self.db = ReservationDB()
        self.current_user: User | None = None   


    def login(self, username: str, password: str):
        """Returns (ok: bool, message: str, user: User|None)."""
        if not username.strip() or not password:
            return False, "Username and password are required.", None
        user = self.db.authenticate(username.strip(), password)
        if user is None:
            return False, "Invalid username or password.", None
        self.current_user = user
        return True, f"Welcome, {user.full_name or user.username}!", user

    def logout(self):
        self.current_user = None

    def is_admin(self) -> bool:
        return self.current_user is not None and self.current_user.role == "admin"


    def get_all_users(self) -> list:
        return self.db.get_all_users()

    def add_user(self, username: str, password: str, role: str, full_name: str):
        """Returns (ok: bool, message: str)."""
        errors = self._validate_user(username, password, role)
        if errors:
            return False, "\n".join(errors)
        if self.db.username_exists(username):
            return False, f"Username '{username}' is already taken."
        user = User(
            username=username.strip(),
            password_hash=User.hash_password(password),
            role=role,
            full_name=full_name.strip(),
            is_active=True,
        )
        self.db.add_user(user)
        return True, f"User '{username}' created successfully."

    def update_user(self, uid: int, username: str, role: str,
                    full_name: str, is_active: bool):
        """Returns (ok: bool, message: str)."""
        u = self.db.get_user_by_id(uid)
        if u is None:
            return False, f"User #{uid} not found."
        if not username.strip():
            return False, "Username is required."
        if role not in ("admin", "staff"):
            return False, "Role must be 'admin' or 'staff'."
        if self.db.username_exists(username.strip(), exclude_id=uid):
            return False, f"Username '{username}' is already taken."
        if u.role == "admin" and role != "admin":
            admins = [x for x in self.db.get_all_users() if x.role == "admin"]
            if len(admins) <= 1:
                return False, "Cannot demote the last administrator."
        u.username  = username.strip()
        u.role      = role
        u.full_name = full_name.strip()
        u.is_active = is_active
        self.db.update_user(u)
        return True, f"User '{username}' updated."

    def reset_user_password(self, uid: int, new_password: str):
        """Returns (ok: bool, message: str)."""
        if len(new_password) < 6:
            return False, "Password must be at least 6 characters."
        new_hash = User.hash_password(new_password)
        self.db.update_user_password(uid, new_hash)
        return True, "Password reset successfully."

    def delete_user(self, uid: int):
        """Returns (ok: bool, message: str)."""
        if self.current_user and self.current_user.id == uid:
            return False, "You cannot delete your own account."
        u = self.db.get_user_by_id(uid)
        if u is None:
            return False, f"User #{uid} not found."
        if u.role == "admin":
            admins = [x for x in self.db.get_all_users() if x.role == "admin"]
            if len(admins) <= 1:
                return False, "Cannot delete the last administrator."
        self.db.delete_user(uid)
        return True, f"User '{u.username}' deleted."

    def change_own_password(self, old_password: str, new_password: str):
        """Returns (ok: bool, message: str)."""
        if self.current_user is None:
            return False, "Not logged in."
        check = self.db.authenticate(self.current_user.username, old_password)
        if check is None:
            return False, "Current password is incorrect."
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."
        new_hash = User.hash_password(new_password)
        self.db.update_user_password(self.current_user.id, new_hash)
        return True, "Password changed successfully."


    def add_reservation(self, **kwargs):
        """Returns (ok: bool, message: str, new_id: int)."""
        try:
            r = Reservation(**kwargs)
            errors = self._validate(r)
            if errors:
                return False, "\n".join(errors), -1
            new_id = self.db.add(r)
            return True, "Reservation added successfully.", new_id
        except Exception as exc:
            return False, str(exc), -1

    def update_reservation(self, rid: int, **kwargs):
        try:
            r = self.db.get_by_id(rid)
            if r is None:
                return False, f"Reservation #{rid} not found."
            for key, val in kwargs.items():
                setattr(r, key, val)
            errors = self._validate(r)
            if errors:
                return False, "\n".join(errors)
            self.db.update(r)
            return True, "Reservation updated successfully."
        except Exception as exc:
            return False, str(exc)

    def delete_reservation(self, rid: int):
        try:
            if self.db.get_by_id(rid) is None:
                return False, f"Reservation #{rid} not found."
            self.db.delete(rid)
            return True, f"Reservation #{rid} deleted."
        except Exception as exc:
            return False, str(exc)

    def get_all(self) -> list:
        return self.db.get_all()

    def get_by_id(self, rid: int):
        return self.db.get_by_id(rid)


    def search(self, query: str) -> list:
        query = query.strip()
        if not query:
            return self.get_all()
        return self.db.search(query)

    def binary_search_by_name(self, name: str):
        name = name.strip()
        if not name:
            return [], "Enter a guest name to run binary search."
        results = self.db.binary_search_by_name(name)
        if results:
            msg = f"Binary Search: {len(results)} record(s) found for '{name}'."
        else:
            msg = f"Binary Search: No exact match for '{name}'."
        return results, msg

    def import_csv(self, filepath: str):
        count, errors = self.db.import_csv(filepath)
        if count == 0 and errors:
            return False, "Import failed:\n" + "\n".join(errors)
        msg = f"Imported {count} reservation(s)."
        if errors:
            msg += f"\n{len(errors)} row(s) skipped:\n" + "\n".join(errors[:5])
        return True, msg

    def export_excel(self, filepath: str, reservations=None):
        try:
            self.db.export_excel(filepath, reservations)
            return True, f"Saved to: {filepath}"
        except RuntimeError as exc:
            return False, str(exc)

    def get_stats(self) -> dict:
        all_r = self.get_all()
        by_status = {}
        for r in all_r:
            by_status[r.status] = by_status.get(r.status, 0) + 1
        return {
            "total":      len(all_r),
            "revenue":    sum(r.total_price for r in all_r),
            "confirmed":  by_status.get("Confirmed", 0),
            "checked_in": by_status.get("Checked In", 0),
            "by_status":  by_status,
        }

    def _validate(self, r: Reservation) -> list:
        errors = []
        if not r.guest_name.strip():
            errors.append("Guest name is required.")
        if not r.room_number.strip():
            errors.append("Room number is required.")
        if not r.room_type.strip():
            errors.append("Room type is required.")
        if not r.check_in.strip():
            errors.append("Check-in date is required.")
        if not r.check_out.strip():
            errors.append("Check-out date is required.")
        if r.guests < 1:
            errors.append("Number of guests must be at least 1.")
        if r.total_price < 0:
            errors.append("Total price cannot be negative.")
        return errors

    def _validate_user(self, username: str, password: str, role: str) -> list:
        errors = []
        if not username.strip():
            errors.append("Username is required.")
        elif len(username.strip()) < 3:
            errors.append("Username must be at least 3 characters.")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if role not in ("admin", "staff"):
            errors.append("Role must be 'admin' or 'staff'.")
        return errors