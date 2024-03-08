import logging
import os

import pandas as pd

from .get_crucial_states import CrucialState


def check_install(checkpoint_installed_ls, captured_dir):
    """
    function: check agent install task is success or not
    input: checkpoint_installed_ls: each element is a checkpoint object
           captured_dir: captured data dir
    output: True or False
    """
    captured_installed_fp = os.path.join(
        captured_dir, "captured_data", "installed_apps", "installed_apps.txt"
    )
    captured_installed_packages = []
    with open(captured_installed_fp, "r") as f:
        for line in f.readlines():
            captured_installed_packages.append(line.strip().lower())

    # checkpoint_installed_packages = []
    cnt = 0
    app_package = pd.read_csv(
        "/data/jxq/mobile-agent/comparison_algorithm/app_package_map.csv"
    )
    app_package_map = dict()
    for item in app_package.to_dict(orient="records"):
        app_package_map[item["app_name"]] = item["package_name"]

    for i in range(len(checkpoint_installed_ls)):
        if (
            app_package_map[checkpoint_installed_ls[i].node_id]
            in captured_installed_packages
        ):
            cnt += 1

    if cnt == len(checkpoint_installed_ls):
        logging.info(f"check install{str(checkpoint_installed_ls)} task success!")
        return True
    else:
        logging.info("check install task failed!")
        logging.info(f"checkpoint package:{str(checkpoint_installed_ls)}")
        return False


def check_uninstall(checkpoint_installed_ls, captured_dir):
    """
    function: check agent uninstall task is success or not
    input: checkpoint_installed_ls: each element is a checkpoint object
           captured_dir: captured data dir
    output: True or False
    """
    captured_installed_fp = os.path.join(
        captured_dir, "captured_data", "installed_apps", "installed_apps.txt"
    )
    captured_installed_packages = []
    with open(captured_installed_fp, "r") as f:
        for line in f.readlines():
            captured_installed_packages.append(line.strip().lower())

    app_package = pd.read_csv(
        "/data/jxq/mobile-agent/comparison_algorithm/app_package_map.csv"
    )
    app_package_map = dict()
    for item in app_package.to_dict(orient="records"):
        app_package_map[item["app_name"]] = item["package_name"]

    for i in range(len(checkpoint_installed_ls)):
        if (
            app_package_map[checkpoint_installed_ls[i].node_id]
            not in captured_installed_packages
        ):
            logging.info(f"check uninstall{str(checkpoint_installed_ls)} task success!")
            return True
        else:
            logging.info("check uninstall task failed!")
            logging.info(f"checkpoint package:{str(checkpoint_installed_ls)}")
            return False


if __name__ == "__main__":

    # app_package_map = pd.read_csv("/data/jxq/mobile-agent/comparison_algorithm/app_package_map.csv")
    # a = app_package_map.to_dict(orient='records')
    # print(a)
    # print(a[0]["app_name"])

    captured_dir = (
        "/data/jxq/mobile-agent/AgentEnv_copy/captured_data/84143002711104077"
    )
    ls = [
        CrucialState(
            1,
            "check_uninstall",
            "ebay",
        )
    ]
    status = check_uninstall(ls, captured_dir)
    if status:
        print("hello world")
