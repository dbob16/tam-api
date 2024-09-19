import time
import json
import os
from datetime import datetime
from httpx import get, post
from configparser import ConfigParser
from getpass import getpass

config = ConfigParser()
config.read('config.ini')

try:
    BASE_URL = config["server"]["base_url"]
except:
    BASE_URL = "http://localhost:8000/"

try:
    api_key = config["server"]["api_key"]
except:
    api_key = None

def backup():
    s_d = {}
    response = get(f"{BASE_URL}prefixes/", params={"api_key": api_key}, verify=False)
    if response.status_code == 200:
        if response.json():
            s_d["prefixes"] = response.json()
    if s_d["prefixes"]:
        for p in s_d["prefixes"]:
            response = get(f"{BASE_URL}tickets/{p["prefix"]}/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                if response.json():
                    s_d[f"{p["prefix"]}_tickets"] = response.json()
            response = get(f"{BASE_URL}baskets/{p["prefix"]}/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                if response.json():
                    s_d[f"{p["prefix"]}_baskets"] = response.json()
    if not os.path.exists("backup"):
        os.makedirs("backup")
    now = datetime.now()
    folder = now.strftime("%Y-%m-%d")
    if not os.path.exists(f"backup/{folder}"):
        os.makedirs(f"backup/{folder}")
    filename = now.strftime("%H-%M")
    with open(f"backup/{folder}/{filename}.json", "w") as file:
        json.dump(s_d, file)
    print(f"Backup successfully made for {now.strftime("%Y-%m-%d %H:%M")}")

def interval_backup(int_minutes:int=None):
    if not int_minutes:
        int_minutes = input("How many minutes to wait between backups? ")
    try:
        int_minutes = int(int_minutes)
    except:
        print("Please input a number next time.")
        quit()
    int_seconds = int_minutes * 60
    print(f"I will start making backups every {int_minutes} minutes")
    while True:
        backup()
        time.sleep(int_seconds)

def restore(filepath:str=None):
    if not filepath:
        filepath = input("Please enter the file path to the file you want to restore: ")
    if not os.path.exists(filepath):
        print(f"No file found at: {filepath}")
        quit()
    with open(filepath, "r") as file:
        r_d = json.load(file)
    if not r_d["prefixes"]:
        quit()
    for p in r_d["prefixes"]:
        prefix = p["prefix"]
        response = post(f"{BASE_URL}prefix/", json=p, params={"api_key": api_key}, verify=False)
        if response.status_code != 200:
            print(f"Error: Status Code <{response.status_code}>")
            quit()
        if r_d[f"{prefix}_tickets"]:
            for t in r_d[f"{prefix}_tickets"]:
                response = post(f"{BASE_URL}ticket/{prefix}/", json=t, params={"api_key": api_key}, verify=False)
                if response.status_code != 200:
                    print(f"Error: Status Code <{response.status_code}>")
                    quit()
        if r_d[f"{prefix}_baskets"]:
            for b in r_d[f"{prefix}_baskets"]:
                response = post(f"{BASE_URL}basket/{prefix}/", json=b, params={"api_key": api_key}, verify=False)
                if response.status_code != 200:
                    print(f"Error: Status Code <{response.status_code}>")
                    quit()
    print("Backup restored completely.")

def settings():
    print("We will go on to generate a settings file with a couple of questions:")
    n_base_url = input("Enter the base url for the TAM server instance: (for example: 'http://localhost:8000/', 'q' to quit) ")
    if n_base_url == "q" or n_base_url == "quit":
        quit()
    ask_api = input("Do you need to generate an API key? (y or n) ")
    if ask_api == "y" or ask_api == "yes":
        inp_pw = getpass("Please enter your API password: ")
        pc_name = input("Please enter the name for this instance: ")
        response = post(f"{n_base_url}genapi/", json={"inp_pw": inp_pw, "pc_name": pc_name}, verify=False)
        if response.status_code != 200:
            print(f"Error {response.status_code}: try again")
            quit()
        r_j = response.json()
        if "api_key" in r_j:
            config["server"] = {"base_url": n_base_url, "api_key": r_j["api_key"]}
            with open("settings.ini", "w") as file:
                config.write(file)
            print("Wrote to config file. Please quit and restart.")
        else:
            print("API key not generated successfully.")
            quit()
    else:
        config["server"] = {"base_url": n_base_url}
        with open("settings.ini", "w") as file:
            config.write(file)
        print("Wrote to config file. Please quit and restart.")
    

if __name__ == "__main__":
    while True:
        print("Welcome to the Ticket Auction Manager backup and restore utility. Please enter what you want to do.")
        print("backup - Makes a timestamped backup right now.")
        print("interval - Makes a backup on a regular basis depending on how many minutes you put in.")
        print("restore - Restores a previous backup. You have to specify path.")
        print("settings - For setting up an ini file so the rest of this will work.")
        print("quit - Exits this program.")
        command = input("Make a selection: ['backup', 'interval', 'restore', 'quit'] ")
        match command.split():
            case ["backup"]:
                backup()
            case ["interval"]:
                interval_backup()
            case ["interval", minutes]:
                interval_backup(minutes)
            case ["restore"]:
                restore()
            case ["restore", filepath]:
                restore(filepath)
            case ["settings"]:
                settings()
            case ["quit"]:
                quit()
            case _:
                print("Invalid Command, please try again.")