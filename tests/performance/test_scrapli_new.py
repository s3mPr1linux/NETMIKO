import functools
from datetime import datetime
import yaml
from rich import print

from scrapli.driver.core import IOSXEDriver
from scrapli.driver.core import NXOSDriver
from scrapli.driver.core import IOSXRDriver
from scrapli.driver.core import EOSDriver
from scrapli.driver.core import JunosDriver

netmiko_scrapli_platform = {
    "IOSXEDriver": "cisco_xe",
    "NXOSDriver": "cisco_nxos",
    "IOSXRDriver": "cisco_xr",
    "EOSDriver": "arista_eos",
    "JunosDriver": "juniper_junos",
}

def read_devices():
    f_name = "test_devices_scrapli.yml"
    with open(f_name) as f:
        return yaml.safe_load(f)



def commands(platform):
    """Parse the commands.yml file to get a commands dictionary."""
    test_platform = platform
    commands_yml = parse_yaml(PWD + "/../etc/commands.yml")
    return commands_yml[test_platform]



#
#
#
## --------------- HERE ------
#import os
#from os import path
#import yaml
#import time
#import functools
#from datetime import datetime
#import csv
#
#from netmiko import ConnectHandler, __version__
#from test_utils import parse_yaml
#
#import network_utilities
#
#PRINT_DEBUG = False
#
#PWD = path.dirname(path.realpath(__file__))
#
#
#def generate_csv_timestamp():
#    """yyyy-MM-dd HH:mm:ss"""
#    now = datetime.now()
#    t_stamp = f"{now.year}-{now.month}-{now.day} {now.hour}:{now.minute}:{now.second}"
#    return t_stamp
#
#
#def write_csv(device_name, netmiko_results):
#    results_file = "netmiko_performance.csv"
#    file_exists = os.path.isfile(results_file)
#    with open(results_file, "a") as csv_file:
#        field_names = ["date", "netmiko_version", "device_name"] + list(
#            netmiko_results.keys()
#        )
#        t_stamp = generate_csv_timestamp()
#        csv_write = csv.DictWriter(csv_file, fieldnames=field_names)
#
#        # Write the header only once
#        if not file_exists:
#            csv_write.writeheader()
#
#        entry = {
#            "date": t_stamp,
#            "netmiko_version": __version__,
#            "device_name": device_name,
#        }
#
#        for func_name, exec_time in netmiko_results.items():
#            entry[func_name] = exec_time
#        csv_write.writerow(entry)
#
#
#def f_exec_time(func):
#    @functools.wraps(func)
#    def wrapper_decorator(*args, **kwargs):
#        start_time = datetime.now()
#        result = func(*args, **kwargs)
#        end_time = datetime.now()
#        time_delta = end_time - start_time
#        print(f"{str(func)}: Elapsed time: {time_delta}")
#        return (time_delta, result)
#
#    return wrapper_decorator
#
#
#
#@f_exec_time
#def connect(device):
#    with ConnectHandler(**device) as conn:
#        prompt = conn.find_prompt()
#        PRINT_DEBUG and print(prompt)
#
#
#@f_exec_time
#def send_command_simple(device):
#    with ConnectHandler(**device) as conn:
#        platform = device["device_type"]
#        cmd = commands(platform)["basic"]
#        output = conn.send_command(cmd)
#        PRINT_DEBUG and print(output)
#
#
#@f_exec_time
#def save_config(device):
#    platform = device["device_type"]
#    if "cisco_xr" in platform or "juniper" in platform:
#        return
#    with ConnectHandler(**device) as conn:
#        platform = device["device_type"]
#        output = conn.save_config()
#        PRINT_DEBUG and print(output)
#
#
#@f_exec_time
#def send_config_simple(device):
#    with ConnectHandler(**device) as conn:
#        platform = device["device_type"]
#        cmd = commands(platform)["config"][0]
#        output = conn.send_config_set(cmd)
#        PRINT_DEBUG and print(output)
#
#
#@f_exec_time
#def send_config_large_acl(device):
#
#    # Results will be marginally distorted by generating the ACL here.
#    device_type = device["device_type"]
#    func_name = f"generate_{device_type}_acl"
#    func = getattr(network_utilities, func_name)
#
#    with ConnectHandler(**device) as conn:
#        cfg = func(entries=100)
#        output = conn.send_config_set(cfg)
#        PRINT_DEBUG and print(output)
#
#
#@f_exec_time
#def cleanup(device):
#
#    # Results will be marginally distorted by generating the ACL here.
#    platform = device["device_type"]
#    if "juniper_junos" in platform:
#        remove_acl_cmd = "rollback 0"
#    elif "hp_procurve" in platform:
#        remove_acl_cmd = None
#    elif "cisco_asa" in platform:
#        remove_acl_cmd = "clear configure access-list netmiko_test_large_acl"
#    else:
#        base_acl_cmd = commands(platform)["config_long_acl"]["base_cmd"]
#        remove_acl_cmd = f"no {base_acl_cmd}"
#    cleanup_generic(device, remove_acl_cmd)
#
#
#def cleanup_generic(device, command):
#    if command is None:
#        return
#    with ConnectHandler(**device) as conn:
#        output = conn.send_config_set(command)
#        PRINT_DEBUG and print(output)
#
#


def main():
    PASSWORD = os.environ["NETMIKO_PASSWORD"]
    HP_PASSWORD = os.environ["HPE_PASSWORD"]

    devices = read_devices()
    print("\n\n")
    for dev_name, params in devices.items():
        dev_dict = params["device"]
        # if dev_name != "cisco_xr_azure":
        #    continue
        print("-" * 80)
        print(f"Device name: {dev_name}")
        print("-" * 12)

        dev_dict["password"] = PASSWORD
        if dev_name == "cisco_asa":
            dev_dict["secret"] = PASSWORD
        elif dev_name == "hp_procurve":
            dev_dict["password"] = HP_PASSWORD

        # Run tests
        operations = [
            "connect",
            "send_command_simple",
            # "save_config",
            "send_config_simple",
            "send_config_large_acl",
            "cleanup",
        ]
        results = {}
        platform = dev_dict["device_type"]
        for op in operations:
            func = globals()[op]
            time_delta, result = func(dev_dict)
            if op != "cleanup":
                results[op] = time_delta
            # Some platforms have an issue where the last test affects the
            # next test?
            if "procurve" in platform:
                print("Sleeping 30 seconds...")
                time.sleep(30)
                print("Done")
        print("-" * 80)
        print()

        write_csv(dev_name, results)

    print("\n\n")


#def test_performance():
#    main()
#
#
#if __name__ == "__main__":
#    main()
#
#def f_exec_time(func):
#    @functools.wraps(func)
#    def wrapper_decorator(*args, **kwargs):
#        start_time = datetime.now()
#        result = func(*args, **kwargs)
#        end_time = datetime.now()
#        time_delta = end_time - start_time
#        print(f"{str(func)}: Elapsed time: {time_delta}")
#        return (time_delta, result)
#
#    return wrapper_decorator
#
#
#@f_exec_time
#def simple_show_cmd(driver, device):
#    ScrapliClass = globals()[driver]
#    with ScrapliClass(**device) as conn:
#        conn.open()
#        return conn.send_command("show ip int brief")
#
#
if __name__ == "__main__":

    my_devices = read_devices()
    for device_name, device in my_devices.items():
        print("\n")
        driver = device.pop("driver")
        print(driver)
        platform = netmiko_scrapli_platform[str(driver)]
        print(platform)

#        device_type = device.pop("device_type")
#        (time_delta, response) = simple_show_cmd(driver, device)
#
#        print()
#        print(driver)
#        print("-" * 60)
#        print(response.result)
#        print("-" * 60)
#        print()
#        print("\n")
