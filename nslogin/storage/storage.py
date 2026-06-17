import os
import sys
import pkgutil
import argparse
import yaml
import re

import importlib


def list_all_backends():
    backends_dict = {}

    dirname = os.path.join(os.path.dirname(__file__), "backends")
    for module_info in pkgutil.iter_modules([dirname]):
        package_name = module_info.name

        match = re.match("(.*)_backend", package_name)
        if not match:
            continue

        full_package_name = f"nslogin.storage.backends.{package_name}"
        backends_dict[match[1]] = full_package_name

    return backends_dict


def get_module(full_package_name):
    if full_package_name not in sys.modules:
        spec = importlib.util.find_spec(full_package_name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[full_package_name] = module
        spec.loader.exec_module(module)
    else:
        module = sys.modules[full_package_name]

    return module


def get_user_table(config):
    backends = list_all_backends()
    backend_name = config.get('db_backend', 'yaml')
    if backend_name not in backends:
        raise ValueError(f'Unsupported database backend: {backend_name}')

    backend = get_module(backends[backend_name])
    return backend.get_user_table(config)
