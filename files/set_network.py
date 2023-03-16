#!/usr/bin/env python3

import time
import yaml
import re
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


def set_ip(config, interfaces):
    print("set_ip")
    ip = config["ip"]
    mac = config["mac"]

    if ip is None or mac is None:
        print("Can not configure networking, no configuration")
        return

    mac = mac.lower()

    # build the configuration file
    data = dict()
    data["network"] = dict()
    data["network"]["version"] = 2
    data["network"]["ethernets"] = dict()

    for interface in interfaces:
        if_config = dict()
        name = interface["name"]
        if interface["mac"].lower() == mac.lower():
            if_config["gateway4"] = "10.100.24.1"
            if_config["addresses"] = [f"{ip}/22"]
            if_config["nameservers"] = dict()
            if_config["nameservers"]["search"] = ["tme.nebulon.com"]
            if_config["nameservers"]["addresses"] = [
                "10.100.24.11", "10.100.24.21"]
        else:
            if_config["dhcp4"] = False
            if_config["optional"] = True

        data["network"]["ethernets"][name] = if_config

    with open("/etc/netplan/99-config.yaml", "w+") as fh:
        content = yaml.dump(data)
        print("writing network config to /etc/netplan/99-config.yaml:")
        print(content)
        fh.write("# This content was written by 'nebulon'\n")
        fh.write(content)

    run_cmd(["/usr/sbin/netplan", "apply"])
    print("Done")


def get_interfaces():
    print("get_interfaces")

    result = []

    lines = run_cmd(["ip", "link"]).split("\n")
    counter = 0
    while counter < len(lines) - 1:
        parts = lines[counter].split(": ")
        if len(parts) == 3:
            interface = dict()
            interface["id"] = parts[0].strip()
            interface["name"] = parts[1].strip()

            # check interface state
            if "state UP" in parts[2]:
                interface["state"] = "UP"
            elif "state DOWN" in parts[2]:
                interface["state"] = "DOWN"
            else:
                interface["state"] = "UNKNOWN"

            # get the MAC address
            counter = counter + 1
            mac_parts = re.split("[ ]+", lines[counter])

            if len(mac_parts) == 5:
                interface["mac"] = mac_parts[2].strip().lower()
            else:
                interface["mac"] = "00:00:00:00:00:00"

        counter = counter + 1
        result.append(interface)

    return result


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

    # get the hosts interfaces
    interfaces = get_interfaces()

    # set the hostname from the configuration
    set_ip(server_config, interfaces)


if __name__ == "__main__":
    main()
