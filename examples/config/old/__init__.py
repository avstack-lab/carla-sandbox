# -*- coding: utf-8 -*-
# @Author: Spencer H
# @Date:   2021-10-25
# @Last Modified by:   Spencer H
# @Last Modified date: 2022-10-22
# @Description:
"""

"""

import glob
import os

import yaml


def get_default_prefixes():
    default_config_glob = glob.glob(
        os.path.join(CURDIR, "./**/default_*.yml"), recursive=True
    )
    def_prefixes = []
    def_files = []
    for i, conf in enumerate(default_config_glob):
        def_prefixes.append(
            conf.split("/")[-1].replace("default_", "").replace(".yml", "")
        )
    return def_prefixes, default_config_glob


CURDIR = os.path.dirname(os.path.abspath(__file__))
def_prefixes, def_files = get_default_prefixes()
DEFAULTS = (def_prefixes, def_files)


def read_config(file_path):
    """Read file and figure out how to add in default fields"""
    if not os.path.exists(file_path):
        if os.path.exists(os.path.join(CURDIR, file_path)):
            file_path = os.path.join(CURDIR, file_path)
        else:
            raise Exception(f"Cannot find config file: {file_path}")

    with open(file_path, "r") as stream:
        try:
            cfg = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    cfg = recurse_replace_default_config_elements(cfg)
    return cfg


def recurse_replace_default_config_elements(cfg, verbose=False):
    """Take a config file, recurse through the fields,
    and see if any are defaults to be set

    This can get nasty because we may have both sub-lists and sub-dicts
    """

    if isinstance(cfg, dict):
        for field in cfg:
            # ---- now, recurse all subfields of cfg[field]
            if isinstance(cfg[field], dict):

                # ---- check to set defaults
                for def_pre, def_file in zip(DEFAULTS[0], DEFAULTS[1]):
                    if def_pre in field:
                        # ---- merge
                        if verbose:
                            print(f"Updating {field} with {def_pre} default")
                        # Load in default (will implicitly recurse each field
                        # for its own defaults)
                        cfg_default = read_config(def_file)

                        # Merge
                        cfg[field] = merge(cfg_default, cfg[field])
                    else:
                        if verbose:
                            print(f"NOT Updating {field} with {def_pre} default")

                # ---- handle subfields, since dict itself
                if verbose:
                    print(f"Recursing because {field} field of cfg is a dict!")
                cfg[field] = recurse_replace_default_config_elements(cfg[field])

            elif isinstance(cfg[field], list):
                # Recurse on each item of the list
                for item in cfg[field]:
                    if isinstance(item, dict):
                        item = recurse_replace_default_config_elements(item)
                    else:
                        if isinstance(item, (int, str)):
                            pass
                        else:
                            for subi in item:
                                assert not isinstance(subi, list)
                                assert not isinstance(subi, dict)

            elif cfg[field] is None:
                # give the option to replace if no values are set
                for def_pre, def_file in zip(DEFAULTS[0], DEFAULTS[1]):
                    if def_pre in field:
                        cfg_default = read_config(def_file)
                        cfg[field] = cfg_default
            else:
                pass

    return cfg


def merge(a, b, path=None):
    """merges dictionary a into dictionary b"""
    if path is None:
        path = []
    try:
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    a[key] = b[key]  # setting value with b's value
            else:
                a[key] = b[key]
    except (KeyboardInterrupt, Exception) as e:
        print("Exception with:", key)
        raise e
    return a
