#
# Copyright 2023, Metropolis Technologies, Inc.
#
"""
This script is called by 'run_single.sh' to create a specific video testing
configuration

Usage: 'python3 prepare_config.py -d <test_video_directory>  \
                -v <test_video_filename> \
                -i <configuration_template_directory> \
                -c <configuration_directory_for_orion> \
                -o <output_directory> (-e for early export on)'

Example usage: 'python3 scripts/prepare_config.py \
                        -d ./AB_TESTING_VIDEOS \
                        -v 771_entry-2022-02-02.mp4 \
                        -i ./config_template/camera_1_config \
                        -c ./orion-evaluation/config -e'

This will generate the proper configuration files in the defined
'configuration_directory_for_orion' directory
"""
import os
import argparse
import yaml
import jinja2
from jinja2 import Environment, FileSystemLoader
import shutil

from string import Template

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        type=str,
                        help='Video directory',
                        required=True)
    parser.add_argument('-v',
                        type=str,
                        help='Video filename',
                        required=True)
    parser.add_argument('-i',
                        type=str,
                        help='Config Template Dir',
                        required=True)
    parser.add_argument('-c',
                        type=str,
                        help='Config Dir',
                        required=True)
    parser.add_argument('-o',
                        type=str,
                        help='Output Dir',
                        required=True)
    parser.add_argument('-e',
                        action="store_true")
    args = parser.parse_args()

    video_dir = args.d
    video_file = args.v
    config_template_dir = args.i
    config_dir = args.c
    output_dir = args.o
    is_early_export = args.e

    if not os.path.isdir(config_template_dir):
        raise Exception(f"File does not exists : {config_template_dir}")

    files = os.listdir(config_template_dir)
    for file in files:
        if "global" in file:
            src = os.path.join(config_template_dir, file)
            try:
                os.removedirs(config_dir)
            except:
                print("Configuration directory not found, not removing.")
            os.makedirs(config_dir)
            shutil.copy(src, config_dir)

    config1 = os.path.join(config_template_dir, "camera_1.yaml")
    config_write_1 = os.path.join(config_dir, "camera_1.yaml")
    config2 = os.path.join(config_template_dir, "camera_2.yaml")
    config_write_2 = os.path.join(config_dir, "camera_2.yaml")
    global_file = os.path.join(config_template_dir, "global.yaml")
    global_write = os.path.join(config_dir, "global.yaml")

    if os.path.exists(global_file):
        with open(global_file, encoding="UTF-8") as global_yaml_file:
            context = {
                "orion_data_dir": (output_dir + "/orion_data")
            }
            global_tmpl = Template(global_yaml_file.read())
            substed = global_tmpl.substitute(context)
            with open(global_write, 'w') as file:
                file.write(substed)

    if os.path.exists(config1):
        with open(config1, encoding="UTF-8") as config_file:
            context = {
                "orion_data_dir": (output_dir + "/orion_data"),
                "camera_serial": "1",
                "video_filename": os.path.join(video_dir, video_file),
                "early_export": str(is_early_export).lower(),
            }
            config_tmpl = Template(config_file.read())
            substed = config_tmpl.substitute(context)
            with open(config_write_1, 'w') as file:
                file.write(substed)

    if os.path.exists(config2):
        with open(config2, encoding="UTF-8") as config_file:
            context = {
                "orion_data_dir": (output_dir + "/orion_data"),
                "camera_serial": "2",
                "video_filename": os.path.join(video_dir, "copy_" + video_file),
                "early_export": is_early_export,
            }
            config_tmpl = Template(config_file.read())
            substed = config_tmpl.substitute(context)
            with open(config_write_2, 'w') as file:
                file.write(substed)

