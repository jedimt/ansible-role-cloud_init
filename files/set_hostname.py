#!/usr/bin/env python3

import time
import yaml
from subprocess import run


def get_config():
    with open("/etc/cloud/nebulon/scripts/configuration.yaml", "r") as fh:
        content = yaml.safe_load(fh)
        return content


def get_serial():
    lines = run_cmd(["dmidecode", "-t", "system"]).split("\n")

    for line in lines:
        if "Serial Number:" in line:
            serial = line.replace("Serial Number:", "").strip().lower()
            return serial

    return "UNKNOWN"


def get_server_config(serial, config):
    servers = config["servers"]

    for server in servers:
        if serial == server["serial"].lower():
            return server

    return None


def run_cmd(cmd, retry=False):
    for naptime in (1, 1, 2, 3, 5, 8, 13):
        print(f" running command: {' '.join(cmd)}")
        process = run(cmd, capture_output=True)

        if process.returncode != 0 and retry:
            print(f"  error: {process.stdout.decode()}")
            time.sleep(naptime)
            continue

        return process.stdout.decode()


def set_hostname(config):
    print("set_hostname")
    hostname = config["name"]

    if hostname is not None:
        print(f"Writing {hostname} to /etc/hostname")
        with open("/etc/hostname", "w+") as fh:
            fh.write(hostname)

        print(f"Setting {hostname} as the hostname")
        run_cmd(["hostnamectl", "set-hostname", hostname], True)

    print("Done")


def main():
    # get the serial number of the server
    serial = get_serial()

    # load configuration
    config = get_config()

    # get the server configuration for this node
    server_config = get_server_config(serial, config)

    if server_config is None:
        print("Can not load server configuration")
        exit(-1)
    else:
        print(f"Loaded configuration: {server_config}")

    # set the hostname from the configuration
    set_hostname(server_config)


if __name__ == "__main__":
    main()
