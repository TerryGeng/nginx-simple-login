from abc import ABC


class UserTable(ABC):
    def has_user(self, user):
        raise NotImplementedError

    def add_user(self, user, password, privilege=None):
        raise NotImplementedError

    def delete_user(self, user):
        raise NotImplementedError

    def list_users(self, name="", regex=""):
        raise NotImplementedError

    def change_user_password(self, user, new_password):
        raise NotImplementedError

    def verify_user_password(self, user, password_provided):
        raise NotImplementedError

    def update_user_login_info(self, user, ip, timestamp):
        raise NotImplementedError

    def verify_user_privileges(self, user, privileges):
        raise NotImplementedError

    def get_user_privileges(self, user):
        raise NotImplementedError

    def change_user_privileges(self, user, privileges):
        raise NotImplementedError

    def add_user_privileges(self, user, privileges):
        raise NotImplementedError

    def remove_user_privileges(self, user, privileges):
        raise NotImplementedError
