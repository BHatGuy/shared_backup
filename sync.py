#!/usr/bin/env python3
import os
import subprocess as sp
import yaml
import logging as log
import sys

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S %d-%m-%Y",
)

PREFIX = "/data/"
config = None


def mount():
    log.info("Mounting...")

    cmd_key = ["ecryptfs-add-passphrase"]
    log.debug(f"Executing {cmd_key}")
    r = sp.run(cmd_key, input=config["ecryptfs_passphrase"].encode(), stdout=sp.DEVNULL)
    if r.returncode != 0:
        log.error("Error while mounting!")
        quit(-1)

    cmd_mount = [
        "mount",
        "-i",
        os.path.join(PREFIX, config["username"], config["dec_dir"]),
    ]
    log.debug(f"Executing {cmd_mount}")
    r = sp.run(cmd_mount, stdout=sp.DEVNULL)
    if r.returncode != 0:
        log.error("Error while mounting!")
        quit(-1)

    log.info("Mounting successfull")


def unmount():
    log.info("Unmounting...")

    cmd = ["umount", os.path.join(PREFIX, config["username"], config["dec_dir"])]
    log.debug(f"Executing {cmd}")
    r = sp.run(cmd, stdout=sp.DEVNULL)
    if r.returncode != 0:
        log.error("Error while unmounting!")
        quit(-1)

    log.info("Unmounting successfull")


def sync_local():
    log.info("Updating local copy")
    for dir in config["dirs"]:
        log.info(f"Updating {dir} locally")
        path = os.path.join(PREFIX, config["username"], config["dirs"][dir]["path"])
        dest = os.path.join(PREFIX, config["username"], config["dec_dir"])
        cmd = ["rsync", "-a"]  # TODO other parameters

        if config["dirs"][dir]["exclude"] is not None:
            for e in config["dirs"][dir]["exclude"]:
                cmd.append("--exclude=" + e)

        cmd += [path, dest]
        log.debug(f"Executing {cmd}")
        r = sp.run(cmd, stdout=sp.DEVNULL)
        if r.returncode != 0:
            log.error(f"Error while Updating {dir} locally")
            quit(-1)


def sync_remote():
    log.info("Syncing to peers")
    for peer in config["peers"]:
        ip = config["ip_prefix"] + str(peer)
        log.info(f"Syncing to {ip}")
        path = os.path.join(PREFIX, config["username"], config["enc_dir"]) + "/"
        uname = config["username"]
        remote = f"{uname}@{ip}:{path}"
        cmd = ["rsync", "--timeout=15", "-az", path, remote]  # TODO other parameters
        log.debug(f"Executing {cmd}")
        r = sp.run(cmd, stdout=sp.DEVNULL)
        if r.returncode == 30:
            log.warning(f"Connection timed out, trying next peer")
        elif r.returncode != 0:
            log.error(f"Error syncing to peer {ip}")
            quit(-1)
        log.info(f"Syncing to {ip} done")


def load_config(path="config.yml"):
    with open(path, "r") as config_file:
        config = yaml.safe_load(config_file)
    if config is None:
        log.error("Could not load config")
        quit(-1)
    if config["debug"]:
        log.getLogger().setLevel(log.DEBUG)
    log.info("Loaded config")
    log.debug(f"Config: {config}")
    return config


if __name__ == "__main__":
    if len(sys.argv) > 1:    
        config = load_config(sys.argv[1])
    else:
        config = load_config()
    mount()
    sync_local()
    unmount()
    sync_remote()
