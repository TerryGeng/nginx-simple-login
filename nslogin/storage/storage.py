import os
import sys
import pkgutil
import argparse
import yaml
import re

from importlib import import_module


def list_all_backends():
    backends_dict = {}

    dirname = os.path.join(os.path.dirname(__file__), "backends")
    for module_info in pkgutil.iter_modules([dirname]):
        package_name = module_info.name

        match = re.match("(.*)_backend", package_name)
        if not match:
            continue

        full_package_name = f"{dirname}.{package_name}"
        backends_dict[match[1]] = (full_package_name, module_info)

    return backends_dict


def get_module(module_description):
    full_package_name, module_info = module_description
    if full_package_name not in sys.modules:
        module = module_info.module_finder.find_module(
            module_info.name).load_module(module_info.name)
        sys.modules[full_package_name] = module
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
