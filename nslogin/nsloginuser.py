import os
import re
import time
import logging
import argparse
import yaml

from .utils.user_table import UserTable

config = {}
user_table: UserTable


def add_user(args):
    user = args.user_name
    password = args.password
    privileges = args.privileges

    if not user:
        print("ERROR: user name must be specified.")
        exit(1)

    if not re.fullmatch("[a-zA-Z]\w*", user):
        print("ERROR: user name must be composed with alphabets and digits only."
              "The first character must be a alphabet.")
        exit(1)

    if user_table.has_user(user):
        print(f"ERROR: user {user} exists.")
        exit(1)

    if not password:
        from getpass import getpass
        while True:
            password = getpass("Input password: ")
            if not password == getpass("Confirm password: "):
                print("ERROR: password not matched.")
                continue
            break

    if not privileges:
        privileges_list = ['default']
    else:
        privileges_list = [s.strip() for s in privileges.split(",")]
        if not privileges_list:
            privileges_list = ['default']

    user_table.add_user(user, password, privileges_list)

    print(f"User {user} has been added with privileges "
          f"{', '.join(privileges_list)}.")


def delete_user(args):
    user = args.user_name

    if not user_table.has_user(user):
        print(f"ERROR: user {user} doesn't exist.")
        exit(1)

    user_table.delete_user(user)
    print(f"User {user} has been deleted.")


def modify_user(args):
    user = args.user_name
    password = args.password
    privileges = args.privileges
    privileges_append = args.privileges_append
    privileges_remove = args.privileges_remove

    if not user_table.has_user(user):
        print(f"ERROR: user {user} doesn't exist.")
        exit(1)

    if password == (None,):
        # --password presents with no password given
        from getpass import getpass
        while True:
            password = getpass("Input password: ")
            if not password == getpass("Confirm password: "):
                print("ERROR: password not matched.")
                continue
            break

    if password:
        user_table.change_user_password(user, password)

    if privileges:
        privileges_list = [s.strip().lower() for s in privileges.split(",")]
        user_table.change_user_privileges(user, privileges_list)

    if privileges_append:
        old_privileges = user_table.get_user_privileges(user)
        privileges_list = [s.strip().lower() for s in privileges_append.split(",")]
        for priv in privileges_list:
            if priv not in old_privileges:
                old_privileges.append(priv)

        user_table.change_user_privileges(user, old_privileges)

    if privileges_remove:
        old_privileges = user_table.get_user_privileges(user)
        privileges_remove = [s.strip().lower() for s in privileges_remove.split(",")]
        for priv in privileges_remove:
            if priv in old_privileges:
                old_privileges.remove(priv)

        user_table.change_user_privileges(user, old_privileges)

    print(f"User {user} has been modified.")


def list_user(args):
    user = args.user_name

    if user:
        if not re.fullmatch("[a-zA-Z*][\w*]*", user):
            print(f"ERROR: wrong user name format.")
            exit(1)

        user_regex = ""
        if "*" in user:
            user_regex = user.replace("*", ".*")
            user = ""

        user_table.list_users(user, user_regex)
    else:
        user_table.list_users(user)


def main():
    global user_table, config

    parser = argparse.ArgumentParser(
        description="user management tool for nslogind")

    parser.add_argument("--config", "-c", dest="config_path",
                        help="path to the configuration file, "
                             "where the path to the user table can be fount")

    parser.add_argument("--user-table", "-u", dest="table_path",
                        help="path to the user table")

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--add", "-a", action="store_true",
                              help="add user")
    action_group.add_argument("--delete", "-d", action="store_true",
                              help="remove user")
    action_group.add_argument("--list", "-l", action="store_true",
                              help="list user's info")
    action_group.add_argument("--modify", "-m", action="store_true",
                              help="modify user's password and privileges")

    parser.add_argument("--name", "-n", dest="user_name",
                        help="specify the user name (for 'list' actions, wildcard "
                             "'*' can be used when querying)")
    parser.add_argument("--password", "-pw", dest="password", nargs='?',
                        const=(None,),
                        help="specify the password (for action add and modify, "
                             "if not specified, a prompt will appear to let you"
                             "type in the password)")
    parser.add_argument("--privileges", "-pr", dest="privileges",
                        help="specify the privileges, separated by ',' (for "
                             "action 'add', 'modify', and 'list')")
    parser.add_argument("--privileges--append", "-pra", dest="privileges_append",
                        help="append privileges, separated by ',' (for "
                             "action 'modify')")
    parser.add_argument("--privileges--revoke", "-prr", dest="privileges_remove",
                        help="revoke privileges, separated by ',' (for "
                             "action 'modify')")

    args = parser.parse_args()

    if args.table_path:
        user_table_path = args.table_path
    else:
        if not args.config_path or not os.path.exists(args.config_path):
            if os.path.exists('config.yaml'):
                args.config_path = 'config.yaml'
            else:
                print("ERROR: config file doesn't exist.")
                exit(1)

        with open(args.config_path, "r") as f:
            config = yaml.safe_load(f)
            user_table_path = config.get('user_table', 'user_table.yaml')

    user_table = UserTable(user_table_path)

    if not os.path.exists(user_table_path):
        print("WARNING: user table doesn't exist. A new one will be created.")

    if args.add:
        add_user(args)
    elif args.delete:
        delete_user(args)
    elif args.modify:
        modify_user(args)
    elif args.list:
        list_user(args)


if __name__ == "__main__":
    main()

