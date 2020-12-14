import os
import time
import logging
import argparse
import yaml
from flask import Flask, session, abort, request, render_template, redirect

from .utils.reverse_proxied import ReverseProxied
from .utils.user_table import UserTable

logger: logging.Logger
app = Flask(__name__)

config = {}
user_table: UserTable

log = logging.getLogger("login")


def if_login():
    if 'user' not in session or 'login_at' not in session:
        return False

    if not user_table.has_user(session['user']) or not (
            time.time() - session['login_at'] <
            config.get('login_life_time', 24 * 3600)):
        return False
    return True


@app.route('/auth', defaults={'privileges': "default"})
@app.route('/auth/<path:privileges>')
def auth(privileges):
    if 'user' not in session or 'login_at' not in session:
        logger.info(f"Unsuccessful auth request from {request.remote_addr}.")
        abort(401)
    else:
        if not if_login():
            logger.info(f"Unsuccessful auth request from {request.remote_addr}.")
            abort(401)

        if not user_table.verify_user_privileges(
                session['user'], privileges.split("/")):
            return render_template("403.template.html",
                                   site_name=config.get("site_name", "Restricted Area")
                                   ), 403

        return '', 200


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
@app.route('/login/', methods=['GET'])
def login_page():
    if if_login():
        return render_template("post-login.template.html",
                               site_name=config.get("site_name", "Restricted Area"),
                               post_login_title=config.get("post_login_page_title",
                                                           "User Area"),
                               post_login_message=config.get("post_login_page_title",
                                                             "Welcome")
                               ), 200
    else:
        redirect = ""
        if 'redirect' in request.args:
            redirect = request.args['redirect']

        logout = False
        if 'logout' in request.args:
            logout = True

        return render_template("login.template.html",
                               site_name=config.get("site_name", "Restricted Area"),
                               login_title=config.get("login_page_title",
                                                      "Authentication Needed"),
                               login_message=config.get("login_page_message",
                                                        ""),
                               redirect=redirect,
                               logout=logout), 200


@app.route('/', methods=['POST'])
@app.route('/login', methods=['POST'])
@app.route('/login/', methods=['POST'])
def verify_login():
    if 'user' in request.form and 'password' in request.form:
        user = request.form['user']
        password = request.form['password']

        if (user_table.has_user(user) and
                user_table.verify_user_password(user, password)):
            user_table.update_user_login_info(user, request.remote_addr,
                                              int(time.time()))

            logger.info(f"User {user} logged in from {request.remote_addr}.")

            session['user'] = user
            session['login_at'] = int(time.time())
            session.permanent = True
            return '', 200

        logger.info(f"Failed login attempt for {user} from {request.remote_addr}.")
    abort(403)


@app.route('/changepassword', methods=['POST'])
def change_password():
    if not if_login():
        abort(401)

    if 'user' in request.form and 'old-password' in request.form and \
            'new-password' in request.form:
        user = request.form['user']
        old_password = request.form['old-password']
        new_password = request.form['new-password']

        if (user_table.has_user(user) and
                user_table.verify_user_password(user, old_password)):
            user_table.change_user_password(user, new_password)
            return '', 200
        abort(403)


@app.route('/changepassword', methods=['GET'])
def change_password_page():
    if not if_login():
        abort(401)

    return render_template("change-password.template.html",
                           site_name=config.get("site_name", "Restricted Area"),
                           user=session['user']
                           ), 200


@app.route('/logout', methods=['GET'])
def logout():
    if 'user' not in session or 'login_at' not in session or not if_login():
        return redirect('./?logout=True', code=302)
    else:
        session.clear()
        return redirect('./?logout=True', code=302)


def main():
    global user_table, app, config, logger

    parser = argparse.ArgumentParser(
        description="a web service that provides authentication together with "
                    "Nginx's auth_request module")

    parser.add_argument("--config", "-c", dest="config_path",
                        help="path to the configuration file")
    args = parser.parse_args()

    if args.config_path:
        if not os.path.exists(args.config_path):
            print("ERROR: config file doesn't exist.")
            exit(1)
    else:
        print("ERROR: config file wasn't specified.")
        exit(1)

    with open(args.config_path, "r") as f:
        config = yaml.safe_load(f)

    if 'session_secret_key' not in config:
        print("ERROR: session_secret_key must be set in configuration file.")
    app.secret_key = config['session_secret_key']
    app.permanent_session_lifetime = config.get('login_life_time', 24*3600)
    user_table_path = config.get('user_table', 'user_table.yaml')
    if os.path.exists(user_table_path):
        user_table = UserTable(user_table_path)
    else:
        print("ERROR: user table doesn't exist.")
        exit(1)

    logger = logging.getLogger()
    if 'logfile' in config and config['logfile']:
        handler = logging.FileHandler(config['logfile'])
    else:
        handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '[%(asctime)s %(levelname)s] %(message)s', "%b %d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    app.wsgi_app = ReverseProxied(app.wsgi_app)

    app.run(port=config.get('port', 8222), host=config.get('host', '127.0.0.1'))


if __name__ == "__main__":
    main()

