import re
import os
import time
import logging
import argparse
import yaml
import secrets
from collections import namedtuple
from flask import (Flask, abort, request, render_template, make_response,
                   redirect, escape)

from nslogin.utils.misc import safeget
from .utils.reverse_proxied import ReverseProxied
from nslogin.storage import get_user_table, UserTable

LoginTokenRecord = namedtuple('LoginTokenRecord', ['user', 'token', 'login_at'])

app = Flask(__name__)

config = {}
user_table: UserTable
login_token_record = {}

logger = logging.getLogger("login")


def get_login_record():
    token = ""

    if 'token' in request.cookies:
        token = request.cookies['token']
    else:
        if 'X-Original-URI' in request.headers:
            match = re.findall("token=(.*)&?", request.headers['X-Original-URI'])
            if not match:
                return None
            token = match[0]
        else:
            return None

    if token not in login_token_record:
        return None

    login = login_token_record[token]

    if not (time.time() - login.login_at <
            config.get('login_life_time', 24 * 3600)):
        del login_token_record[request.cookies['token']]
        return None
    return login


@app.route('/auth', defaults={'privileges': "default"})
@app.route('/auth/<path:privileges>')
def auth(privileges):
    login = get_login_record()
    if not login:
        logger.info(f"Unsuccessful auth request from {request.remote_addr}.")
        abort(401)

    if not user_table.verify_user_privileges(login.user, privileges.split("/")):
        logger.info(f"Rejected {login.user}'s access request to privileged area {privileges}.")
        return render_template("403.template.html",
                               site_name=config.get("site_name", "Restricted Area")
                               ), 403

    return '', 200


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET'])
@app.route('/login/', methods=['GET'])
def login_page():
    login = get_login_record()
    if login:
        return render_template("post-login.template.html",
                               site_name=config.get("site_name", "Restricted Area"),
                               post_login_title=config.get("post_login_page_title",
                                                           "User Area"),
                               post_login_message=config.get("post_login_message",
                                                             "Welcome"),

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
                               register=safeget(config, 'register', 'enabled'),
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

            login_at = int(time.time())
            token = secrets.token_hex(16)
            login_token_record[token] = LoginTokenRecord(user, token, login_at)

            resp = make_response('', 200)
            resp.set_cookie('token', token,
                            expires=time.time() + config.get('login_life_time', 24 * 3600))
            return resp

        logger.info(f"Failed login attempt for {user} from {request.remote_addr}.")
    abort(403)


@app.route('/changepassword', methods=['POST'])
def change_password():
    login = get_login_record()
    if not login:
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
    login = get_login_record()
    if not login:
        abort(401)

    return render_template("change-password.template.html",
                           site_name=config.get("site_name", "Restricted Area"),
                           user=login.user
                           ), 200


@app.route('/register', methods=['POST'])
def register():
    login = get_login_record()
    if login:
        return redirect('./')

    if 'user' in request.form and 'password' in request.form and \
            'invitation' in request.form:
        user = str(escape(request.form['user']))
        invitation = request.form['invitation']
        password = request.form['password']

        if not safeget(config, 'register', 'enabled'):
            return 'disabled', 400

        if safeget(config, 'register', 'use_invitation_code'):
            code_file = safeget(config, 'register', 'invitation_code_file')
            if not code_file or not os.path.exists(code_file):
                logger.error(f'Cannot read invitation code file {code_file}')
                return abort(500)

            with open(code_file, "r") as f:
                codes = yaml.safe_load(f)

            if not invitation or invitation not in codes:
                return 'invitation', 400

            if user_table.has_user(user):
                return 'duplicated', 400

            user_table.add_user(user, password)

            if safeget(config, 'register', 'dispose_used_invitation_code'):
                codes.remove(invitation)
                with open(code_file, "w") as f:
                    yaml.dump(codes, f)
        else:
            if user_table.has_user(user):
                return 'duplicated', 400

            user_table.add_user(user, password)

        return '', 200


@app.route('/register', methods=['GET'])
def register_page():
    if not safeget(config, 'register', 'enabled'):
        return redirect('./')

    return render_template("register.template.html",
                           site_name=config.get("site_name", "Restricted Area"),
                           invitation=safeget(config, 'register', 'use_invitation_code')
                           ), 200


@app.route('/logout', methods=['GET'])
def logout():
    login = get_login_record()
    if login:
        del login_token_record[login.token]

    return '', 200


@app.route('/403', methods=['GET'])
def forbidden():
    return render_template("403.template.html",
                           site_name=config.get("site_name", "Restricted Area")
                           ), 403


def main():
    global user_table, app, config, logger

    parser = argparse.ArgumentParser(
        description="a web service that provides authentication together with "
                    "Nginx's auth_request module")

    parser.add_argument("--config", "-c", dest="config_path",
                        help="path to the configuration file")
    args = parser.parse_args()

    if not args.config_path or not os.path.exists(args.config_path):
        if os.path.exists('config.yaml'):
            args.config_path = 'config.yaml'
        else:
            print("ERROR: config file doesn't exist.")
            exit(1)

    with open(args.config_path, "r") as f:
        config = yaml.safe_load(f)

    logger.setLevel(logging.INFO)
    if 'logfile' in config and config['logfile']:
        handler = logging.FileHandler(config['logfile'])
    else:
        handler = logging.StreamHandler()

    user_table = get_user_table(config)

    formatter = logging.Formatter(
        '[%(asctime)s %(levelname)s] %(message)s', "%b %d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)

    app.wsgi_app = ReverseProxied(app.wsgi_app)

    app.run(port=config.get('port', 8222), host=config.get('host', '127.0.0.1'))


if __name__ == "__main__":
    main()

