class UserInfo:
    def __init__(self, name, password_hash, password_salt,
                 last_login_timestamp, last_login_ip, privilege):
        self.name = name
        self.password_hash = password_hash
        self.password_salt = password_salt
        self.last_login_timestamp = last_login_timestamp
        self.last_login_ip = last_login_ip
        self.privilege = privilege
