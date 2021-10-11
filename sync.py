#!/usr/bin/env python3
from os import path
import subprocess as sp
import yaml
import logging as log

log.basicConfig(
    level=log.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S %d-%m-%Y",
)

PREFIX = "/data/"


def mount():
    log.info("Mounting...")

    cmd_key = ["ecryptfs-add-passphrase"]
    log.debug(f"Executing {cmd_key}")
    r = sp.run(cmd_key, input=config["ecryptfs_passphrase"].encode(), stdout=sp.DEVNULL)  
    if r.returncode != 0:
        log.error("Error while mounting!")
        quit(-1)

    cmd_mount = ["mount", "-i", path.join(PREFIX, config["username"], config["dec_dir"])]
    log.debug(f"Executing {cmd_mount}")
    r = sp.run(cmd_mount, stdout=sp.DEVNULL)  
    if r.returncode != 0:
        log.error("Error while mounting!")
        quit(-1)

def unmount():
    pass


with open("config.yml", "r") as config_file:  #  TODO as parameter
    config = yaml.safe_load(config_file)
if config is None:
    log.error("Could not load config")
    quit(-1)
if config["debug"]:
    log.getLogger().setLevel(log.DEBUG)
log.info("Loaded config")
log.debug(f"Config: {config}")

mount()
unmount()
