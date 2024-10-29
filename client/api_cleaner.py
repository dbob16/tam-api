import os
import ttkbootstrap as ttk 
from httpx import get, delete
from configparser import ConfigParser

if os.name == "nt":
    home_path = os.getenv("APPDATA")
    if not os.path.exists(f"{home_path}\\TAM"):
        os.mkdir(f"{home_path}\\TAM")
    config_path = f"{home_path}\\TAM\\config.ini"
else:
    home_path = os.path.expanduser("~")
    if not os.path.exists(f"{home_path}/.config/TAM"):
        os.mkdir(f"{home_path}/.config/TAM")
    config_path = f"{home_path}/.config/TAM/config.ini"

config = ConfigParser()
config.read(config_path)

try:
    BASE_URL = config["server"]["base_url"]
except:
    BASE_URL = "http://localhost:8000/"

try:
    api_key = config["server"]["api_key"]
except:
    api_key = None

def api_cleaner():
    window = ttk.Toplevel(title="TAM API cleaner")

    def get_api_keys():
        tv_api.delete(*tv_api.get_children())
        response = get(f"{BASE_URL}api_keys/", params={"api_key": api_key}, verify=False)
        if response.status_code == 200:
            index = 1
            for v in response.json():
                tv_api.insert("", "end", iid=index, values=(v["api_key"], v["pc_name"], v["ip_addr"]))
                index += 1
            lbl_status.config(text="Got API keys successfully", bootstyle="success")
        else:
            lbl_status.config(text=f"Error getting API keys, status returned <{response.status_code}>", bootstyle="danger")

    def del_api_key():
        if tv_api.selection():
            for s in tv_api.selection():
                del_key = tv_api.item(s)["values"][0]
                response = delete(f"{BASE_URL}delapi/", params={"auth_key": api_key, "api_key": del_key}, verify=False)
                if response.status_code == 200:
                    lbl_status.config(text="API Key Deleted Successfully", bootstyle="success")
                else:
                    lbl_status.config(text="Couldn't Delete Key", bootstyle="danger")
            get_api_keys()


    frm_tv = ttk.LabelFrame(window, text="API Keys")
    frm_tv.pack(padx=4, pady=4, fill="x")

    sb_tv = ttk.Scrollbar(frm_tv, orient="vertical")
    sb_tv.pack(side="right", fill="y")

    tv_api = ttk.Treeview(frm_tv, show="headings", columns=("api", "pc", "ip"), yscrollcommand=sb_tv.set)
    tv_api.heading("api", text="API Key", anchor="w"), tv_api.heading("pc", text="PC Name", anchor="w")
    tv_api.heading("ip", text="IP Address", anchor="w")
    tv_api.pack(padx=4, pady=4, fill="both", expand="yes")

    sb_tv.config(command=tv_api.yview)

    frm_buttons = ttk.LabelFrame(window, text="Commands")
    frm_buttons.pack(padx=4, pady=4, fill="x")

    btn_delete = ttk.Button(frm_buttons, text="Delete", bootstyle="danger", command=del_api_key)
    btn_delete.pack(side="left", padx=4, pady=4)

    frm_statusbar = ttk.Frame(window)
    frm_statusbar.pack(side="bottom", padx=4, pady=4, fill="x")

    lbl_status = ttk.Label(frm_statusbar)
    lbl_status.pack(side="left", padx=4, pady=4)

    get_api_keys()