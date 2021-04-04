import os
import re
import secrets
import hashlib
import logging
from datetime import datetime

import mariadb

from nslogin.storage.user_info import UserInfo
from nslogin.storage.user_table import UserTable
from nslogin.utils.misc import get

logger = logging.getLogger('login')


def get_user_table(config):
    try:
        host = get(config, 'mysql', 'host')
        port = get(config, 'mysql', 'port')
        user = get(config, 'mysql', 'user')
        password = get(config, 'mysql', 'password')
        database = get(config, 'mysql', 'database')
        table = get(config, 'mysql', 'table')

        return MysqlUserTable(user, password, database, table, host, port)

    except KeyError:
        raise KeyError("Invalid MySQL configuration!")


class MysqlUserTable(UserTable):
    def __init__(self, user, password, database, table, host, port):
        self.user_db_access = {
            'user': user,
            'password': password,
            'database': database,
            'host': host,
            'port': port
        }
        self.table = table

    def create_table_if_not_exist(self):
        if self.query(f'SHOW TABLES LIKE {self.table}'):
            return

        logger.warning(f"Mysql: Table `{self.table}` doesn't exist. Create one.")
        conn = mariadb.connect(**self.user_db_access)
        cursor = conn.cursor()
        cursor.execute(f"""
        CREATE TABLE `{self.table}` (
              `id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
              `username` varchar(255) NOT NULL,
              `realname` varchar(255) NOT NULL,
              `password` varchar(255) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
              `salt` varchar(255) DEFAULT NULL,
              `ip` varchar(40) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL,
              `lastlogin` bigint(20) DEFAULT NULL,
              `web_privileges` varchar(255) DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `username` (`username`)
            ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
        """)

        conn.commit()
        cursor.close()
        conn.close()

    def query(self, sql_template, filler):
        conn = mariadb.connect(**self.user_db_access)
        cursor = conn.cursor()
        cursor.execute(sql_template, filler)

        ret = cursor.fetchall()

        cursor.close()
        conn.close()

        return ret

    def execute(self, sql_template, filler):
        conn = mariadb.connect(**self.user_db_access)
        cursor = conn.cursor()
        cursor.execute(sql_template, filler)

        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def pack_user_info(user_info_array):
        timestamp = user_info_array[3] if user_info_array[3] else 0

        return UserInfo(
            name=user_info_array[0],
            password_hash=user_info_array[1],
            password_salt=user_info_array[2],
            last_login_timestamp=datetime.fromtimestamp(timestamp).isoformat(),
            last_login_ip=user_info_array[4],
            privilege=user_info_array[5].split(",")
        )

    def query_user(self, user):
        user = user.lower()
        ret = self.query("SELECT username, password, salt, lastlogin, ip, "
                         f"web_privileges FROM `{self.table}` "
                         "WHERE username=?", (user,))

        if not ret:
            return None

        return self.pack_user_info(ret[0])

    def query_all_users(self):
        ret = self.query("SELECT username, password, salt, lastlogin, ip, "
                         f"web_privileges FROM `{self.table}`")

        if not ret:
            return None

        return [self.pack_user_info(user) for user in ret]

    def query_users_regex(self, regex):
        ret = self.query("SELECT username, password, salt, lastlogin, ip, "
                         f"web_privileges FROM `{self.table}` "
                         f"REGEXP {regex}")

        if not ret:
            return None

        return [self.pack_user_info(user) for user in ret]

    def has_user(self, user):
        user = user.lower()
        if self.query(f'SELECT id FROM `{self.table}` WHERE username=?', (user,)):
            return True
        else:
            return False

    def add_user(self, user, password, privilege=None):
        if self.has_user(user):
            return False

        salt, hash_ = self.get_salted_hash(password)

        if not privilege:
            privilege = ['default']

        self.execute(f"INSERT INTO `{self.table}` "
                     "(username, realname, password, salt, web_privileges) "
                     "VALUES (?, ?, ?, ?, ?)",
                     (user.lower(), user, hash_, salt, ",".join(privilege)))

        return True

    def delete_user(self, user):
        user = user.lower()
        if not self.has_user(user):
            raise ValueError(f"User '{user}' doesn't exist.")
        self.execute(f"DELETE FROM `{self.table}` WHERE username=?", (user,))

    def list_users(self, name="", regex=""):
        name = name.lower()
        if name:
            user_info = self.query_user(name)
            if not user_info:
                raise ValueError(f"User '{name}' doesn't exist.")
            user_info_list = [user_info]
        elif regex:
            user_info_list = self.query_users_regex(regex)
        else:
            user_info_list = self.query_all_users()

        return user_info_list

    def change_user_password(self, user, new_password):
        user = user.lower()
        if not self.has_user(user):
            raise ValueError(f"User '{user}' doesn't exist.")

        salt, hash_ = self.get_salted_hash(new_password)

        self.execute(f"UPDATE `{self.table}` SET password=?, salt=? WHERE username=?",
                     (hash_, salt, user))

    def verify_user_password(self, user, password_provided):
        user_info = self.query_user(user)

        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        _, hash_ = self.get_salted_hash(password_provided,
                                        user_info.password_salt)

        return user_info.password_hash == hash_

    def update_user_login_info(self, user, ip, timestamp):
        self.execute(f"UPDATE `{self.table}` SET lastlogin=?, ip=? WHERE username=?",
                     (timestamp, ip, user))

    def verify_user_privileges(self, user, privileges):
        if not privileges:
            privileges = ['default']

        user_info = self.query_user(user)
        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv not in user_info.privilege:
                return False

        return True

    def get_user_privileges(self, user):
        user_info = self.query_user(user)
        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        return user_info.privilege

    def change_user_privileges(self, user, privileges):
        user_info = self.query_user(user)
        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        privilege = []
        for priv in privileges:
            priv = priv.lower()
            privilege.append(priv)

        self.execute(f"UPDATE `{self.table}` SET web_privilege=? WHERE username=?",
                     (",".join(privilege), user))

    def add_user_privileges(self, user, privileges):
        user_info = self.query_user(user)
        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv not in user_info.privilege:
                user_info.privilege.append(priv)

        self.execute(f"UPDATE `{self.table}` SET web_privilege=? WHERE username=?",
                     (",".join(user_info.privilege), user))

    def remove_user_privileges(self, user, privileges):
        user_info = self.query_user(user)
        if not user_info:
            raise ValueError(f"User '{user}' doesn't exist.")

        for priv in privileges:
            priv = priv.lower()
            if priv in user_info.privilege:
                user_info.privilege.remove(priv)

        self.execute(f"UPDATE `{self.table}` SET web_privilege=? WHERE username=?",
                     (",".join(user_info.privilege), user))

    @staticmethod
    def get_salted_hash(password, salt=None):
        salt = secrets.token_hex(16) if not salt else salt
        hash_ = hashlib.sha512((password + salt).encode('utf-8')).hexdigest()
        return salt, hash_
