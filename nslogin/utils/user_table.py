import os
import re
import yaml
import secrets
import hashlib
from datetime import datetime

from nslogin.utils.format import TableFormatter


class UserInfo:
    def __init__(self, name, password_hash, password_salt,
                 last_login_timestamp, last_login_ip, privilege):
        self.name = name
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.last_login_timestamp = last_login_timestamp
        self.last_login_ip = last_login_ip
        self.privilege = privilege


class UserTable:
    def __init__(self, user_info_file=None):
        self.user_dict = {}
        self.user_info_file = user_info_file
        self.load_from_file()

    def has_user(self, user):
        if user in self.user_dict:
            return True
        else:
            return False

    def add_user(self, user, password, privilege=None):
        if user in self.user_dict:
            raise ValueError(f"User '{user}' exists.")

        salt, hash_ = self.get_salted_hash(password)

        if not privilege:
            privilege = ['default']

        self.user_dict[user] = UserInfo(
            name=user,
            password_hash=hash_,
            password_salt=salt.hex(),
            last_login_timestamp=datetime.fromtimestamp(0).isoformat(),
            last_login_ip="",
            privilege=privilege
        )
        self.save_to_file()

    def delete_user(self, user):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")
        del self.user_dict[user]
        self.save_to_file()

    def list_users(self, name="", regex=""):
        if name:
            if name not in self.user_dict:
                raise ValueError(f"User '{name}' doesn't exist.")
            user_info_list = [self.user_dict[name]]
        elif regex:
            user_info_list = list(
                filter(lambda user: re.fullmatch(regex, user.name),
                       self.user_dict.values()))
        else:
            user_info_list = self.user_dict.values()

        table = TableFormatter()
        table.add_column("User name", "name", 20)
        table.add_column("Last login time", "last_login_timestamp")
        table.add_column("Last login ip", "last_login_ip")
        table.add_column("Privileges", "privilege", 20, None, lambda l: ", ".join(l))

        table.add_rows(user_info_list)
        table.print_formatted()
        print(f"{len(self.user_dict)} users in total")

    def change_user_password(self, user, new_password):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        salt, hash_ = self.get_salted_hash(new_password)

        self.user_dict[user].password_hash = hash_
        self.user_dict[user].password_salt = salt.hex()

        self.save_to_file()

    def verify_user_password(self, user, password_provided):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        _, hash_ = self.get_salted_hash(password_provided,
                                        bytes.fromhex(
                                            self.user_dict[user].password_salt))

        if self.user_dict[user].password_hash == hash_:
            return True
        else:
            return False

    def update_user_login_info(self, user, ip, timestamp):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        self.user_dict[user].last_login_timestamp = datetime.fromtimestamp(timestamp).isoformat()
        self.user_dict[user].last_login_ip = ip

        self.save_to_file()

    def verify_user_privileges(self, user, privileges):
        if not privileges:
            privileges = ['default']

        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv not in self.user_dict[user].privilege:
                return False

        return True

    def change_user_privileges(self, user, privileges):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        self.user_dict[user].privilege = []
        for priv in privileges:
            priv = priv.lower()
            self.user_dict[user].privilege.append(priv)

        self.save_to_file()

    def add_user_privileges(self, user, privileges):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv not in self.user_dict[user].privilege:
                self.user_dict[user].privilege.append(priv)

        self.save_to_file()

    def remove_user_privileges(self, user, privileges):
        if user not in self.user_dict:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv in self.user_dict[user].privilege:
                self.user_dict[user].privilege.remove(priv)

        self.save_to_file()

    @staticmethod
    def get_salted_hash(password, salt=None):
        password_bytes = password.encode("utf-8")
        salt = secrets.token_bytes(16) if not salt else salt
        hash_ = hashlib.sha256(password_bytes + salt).hexdigest()
        return salt, hash_

    def load_from_file(self):
        if os.path.exists(self.user_info_file):
            with open(self.user_info_file, "r") as f:
                user_dict = yaml.safe_load(f)

                for user, info in user_dict.items():
                    self.user_dict[user] = UserInfo(
                        user,
                        info['password_hash'],
                        info['password_salt'],
                        info['last_login_timestamp'],
                        info['last_login_ip'],
                        info['privilege']
                    )

    def save_to_file(self):
        with open(self.user_info_file, "w") as f:
            user_dict = {}
            for user, info in self.user_dict.items():
                user_dict[user] = {
                    'password_hash': info.password_hash,
                    'password_salt': info.password_salt,
                    'last_login_timestamp': info.last_login_timestamp,
                    'last_login_ip': info.last_login_ip,
                    'privilege': info.privilege
                }
            yaml.dump(user_dict, f)
