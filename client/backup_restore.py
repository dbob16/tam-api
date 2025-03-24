import ttkbootstrap as ttk 
import gzip
import json
import os
import time
import asyncio
from httpx import get, post
from datetime import datetime 
from tkinter import filedialog
from dao import PrefixRepo, TicketRepo, BasketRepo

interval_started = False

def backup(BASE_URL:str, api_key:str, backup_folder:str):
    out_file = {}
    response = get(f"{BASE_URL}prefixes/", params={"api_key": api_key}, verify=False)
    prefix_list = response.json()
    out_file["prefixes"] = prefix_list
    for prefix in prefix_list:
        response = get(f"{BASE_URL}tickets/{prefix['prefix']}/", params={"api_key": api_key}, verify=False)
        out_file[f"{prefix['prefix']}_tickets"] = response.json()
        response = get(f"{BASE_URL}baskets/{prefix['prefix']}/", params={"api_key": api_key}, verify=False)
        out_file[f"{prefix['prefix']}_baskets"] = response.json()
    now = datetime.now().isoformat(timespec="seconds")
    j = json.dumps(out_file).encode('utf-8')
    with gzip.open(os.path.join(backup_folder, f"{now}.json.gz"), "w") as file:
        file.write(j)
    return f"Backup successfully completed at {now}!"

def ibackup(BASE_URL:str, api_key:str, backup_folder:str, minutes:int):
    seconds = minutes * 60
    print(f"Thanks, I will start backing up every {minutes} minutes, starting now...")
    print("Press Ctrl+C to cancel")
    while True:
        print(backup(BASE_URL, api_key, backup_folder))
        time.sleep(seconds)

def restore(BASE_URL:str, api_key:str, restore_file:str):
    with gzip.open(restore_file, "r") as file:
        in_file = file.read().decode("utf-8")
        in_dict = json.loads(in_file)
    for prefix in in_dict["prefixes"]:
        response = post(f"{BASE_URL}prefix/", params={"api_key": api_key}, json=prefix)
        if response.status_code != 200:
            return response.json()
        response = post(f"{BASE_URL}tickets/", params={"api_key": api_key}, json=in_dict[f"{prefix['prefix']}_tickets"])
        if response.status_code != 200:
            return response.json()
        response = post(f"{BASE_URL}baskets/", params={"api_key": api_key}, json=in_dict[f"{prefix['prefix']}_baskets"])
        if response.status_code != 200:
            return response.json()
    if os.name == "nt":
        if "\\" in restore_file:
            filename = restore_file.split("\\")[-1]
        else:
            filename = restore_file
    else:
        if "/" in restore_file:
            filename = restore_file.split("/")[-1]
        else:
            filename = restore_file
    return f"Backup {filename} restored at {datetime.now().isoformat(timespec='seconds')}"

def backup_form(BASE_URL:str, api_key:str):
    window = ttk.Toplevel(title="TAM Backup and Restore")
    v_backup_folder = ttk.StringVar(window)
    v_restore_file = ttk.StringVar(window)
    lst_backup_results = []
    lst_restore_results = []

    # Functions
    def cmd_backup(_=None):
        if len(lst_backup_results) > 0:
            for result in lst_backup_results:
                result.pack_forget()
        message = backup(BASE_URL, api_key, v_backup_folder.get())
        status_label = ttk.Label(cnt_backup_results, text=message)
        lst_backup_results.append(status_label)
        if len(lst_backup_results) > 3:
            lst_backup_results.pop(0)
        for result in lst_backup_results:
            result.pack(padx=4, pady=4)

    def cmd_restore(_=None):
        if len(lst_restore_results) > 0:
            for result in lst_restore_results:
                result.pack_forget()
        message = restore(BASE_URL, api_key, v_restore_file.get())
        status_label = ttk.Label(cnt_restore_results, text=message)
        lst_restore_results.append(status_label)
        if len(lst_restore_results) > 3:
            lst_restore_results.pop(0)
        for result in lst_restore_results:
            result.pack(padx=4, pady=4)

    def cmd_push_prefixes(_=None):
        repo = PrefixRepo(BASE_URL=BASE_URL, api_key=api_key)
        repo.push()
    
    def cmd_push_tickets(_=None):
        repo = TicketRepo(BASE_URL=BASE_URL, api_key=api_key)
        repo.push()

    def cmd_push_baskets(_=None):
        repo = BasketRepo(BASE_URL=BASE_URL, api_key=api_key)
        repo.push()

    def cmd_pull_prefixes(_=None):
        repo = PrefixRepo(BASE_URL=BASE_URL, api_key=api_key)
        repo.pull()

    # Label Frames
    frm_backup = ttk.Labelframe(window, text="Backup")
    frm_backup.pack(padx=4, pady=4, fill="x")

    frm_backop = ttk.Labelframe(window, text="Backup Operations")
    frm_backop.pack(padx=4, pady=4, fill="x")

    frm_restore = ttk.Labelframe(window, text="Restore")
    frm_restore.pack(padx=4, pady=4, fill="x")

    frm_restoreops = ttk.Labelframe(window, text="Restore Operations")
    frm_restoreops.pack(padx=4, pady=4, fill="x")

    frm_push = ttk.Labelframe(window, text="Push (from local to server)")
    frm_push.pack(padx=4, pady=4, fill="x")

    frm_pull = ttk.Labelframe(window, text="Pull (from server to local)")
    frm_pull.pack(padx=4, pady=4, fill="x")

    # Backup Frame
    txt_backup_folder = ttk.Entry(frm_backup, textvariable=v_backup_folder, width=40)
    txt_backup_folder.grid(column=0, row=0, padx=4, pady=4)

    btn_browse_backup = ttk.Button(frm_backup, text="Browse", command=lambda: v_backup_folder.set(filedialog.askdirectory()))
    btn_browse_backup.grid(column=1, row=0, padx=4, pady=4)

    # Backup Operations Frame
    btn_backup_now = ttk.Button(frm_backop, text="Backup Now", command=cmd_backup)
    btn_backup_now.grid(column=0, row=0, padx=4, pady=4)

    cnt_backup_results = ttk.Frame(frm_backop)
    cnt_backup_results.grid(column=0, row=1, columnspan=50)

    # Restore Frame
    txt_restore_file = ttk.Entry(frm_restore, textvariable=v_restore_file, width=40)
    txt_restore_file.grid(column=0, row=0, padx=4, pady=4)

    btn_browse_restore = ttk.Button(frm_restore, text="Browse", command=lambda: v_restore_file.set(filedialog.askopenfilename()))
    btn_browse_restore.grid(column=1, row=0, padx=4, pady=4)

    # Restore Operations Frame
    btn_restore_now = ttk.Button(frm_restoreops, text="Restore Now", command=cmd_restore)
    btn_restore_now.grid(column=0, row=0, padx=4, pady=4)

    cnt_restore_results = ttk.Frame(frm_restoreops)
    cnt_restore_results.grid(column=0, row=1, padx=4, pady=4, columnspan=50)

    # Push Operations Frame
    btn_push_prefixes = ttk.Button(frm_push, text="Push Prefixes", command=cmd_push_prefixes)
    btn_push_prefixes.grid(row=0, column=0, padx=4, pady=4)

    btn_push_tickets = ttk.Button(frm_push, text="Push Tickets", command=cmd_push_tickets)
    btn_push_tickets.grid(row=0, column=1, padx=4, pady=4)

    btn_push_baskets = ttk.Button(frm_push, text="Push Baskets", command=cmd_push_baskets)
    btn_push_baskets.grid(row=0, column=2, padx=4, pady=4)

    # Pull Operations Frame
    btn_pull_prefixes = ttk.Button(frm_pull, text="Pull Prefixes", command=cmd_pull_prefixes)
    btn_pull_prefixes.grid(row=0, column=0, padx=4, pady=4)