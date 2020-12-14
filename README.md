# nginx-simple-login

A lightweight authentication service backend designed to work
with nginx's auth_request.

![Screenshot](screenshots/login.jpg)

## Features

- auth_request handler,
- Authentication page,
- Local user database.


## Usage

1. Clone this repo.

2. Install this package by `pip install .` (recommended to
 install in a `virtualenv`).
 
3. Create `config.yaml`, follows `config.example.yaml`. A minimal version:
```yaml
user_table: users.yaml
session_secret_key: deadbeef
site_name: Restrict Area
logfile: /var/log/nslogin.py
```

4. Add user with `nslogin-user` command, e.g.
```bash
nslogin-user --config config.yaml --add --name terry
```

5. Run `nslogind --config config.yaml`.

6. Edit `nginx.conf`, 
```nginx
    location / {
        auth_request /nslogin/auth;  # <<< insert auth_request at locations that require auth
        root   /srv/http;
        index  index.html index.htm;
    }

    location ^~ /nslogin {
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        location /nslogin/auth {
            proxy_pass http://127.0.0.1:8222/auth;
            proxy_pass_request_body off;
            proxy_set_header Content-Length "";
        }

        location /nslogin {
            rewrite /nslogin/(.*) /$1  break;
            proxy_pass http://127.0.0.1:8222;
        }
    }

    error_page 401 = @error401;
    error_page 403 = @error403;

    location @error401 {
        return 302 http://$http_host/nslogin/?redirect=http://$http_host$request_uri;
    }
    location @error403 {
        return 302 http://$http_host/nslogin/403;
    }
```

7. Reload nginx and enjoy.
