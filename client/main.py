import os
import ttkbootstrap as ttk 
import webbrowser
import sys
from httpx import get, post
from dao import *
from configparser import ConfigParser
from ttkbootstrap import utility
from tkinter import filedialog
from jinja2 import Environment, FileSystemLoader, select_autoescape
from forms import ticket_form, basket_form, drawing_form
from prefix_manager import prefix_manager
from api_cleaner import api_cleaner
from backup_restore import backup_form, backup, restore, ibackup

server = {}
BASE_URL = ""
prefs = {}
HIGH_DPI = "off"
api_key = ""
BAND_COLOR = ""
font_size = 10

if os.path.exists("config.ini"):
    config_path = "config.ini"
elif os.name == "nt":
    home_path = os.getenv("APPDATA")
    if not os.path.exists(f"{home_path}\\TAM"):
        os.mkdir(f"{home_path}\\TAM")
    config_path = f"{home_path}\\TAM\\config.ini"
else:
    home_path = os.path.expanduser("~")
    if not os.path.exists(f"{home_path}/.config/TAM"):
        os.mkdir(f"{home_path}/.config/TAM")
    config_path = f"{home_path}/.config/TAM/config.ini"

def save_report(report):
    save_to_path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("Web Page", "*.html")])
    with open(save_to_path, "w") as f:
        f.write(report)
    return save_to_path

def refresh_config():
    config = ConfigParser()
    global server
    global BASE_URL
    global prefs
    global api_key
    global HIGH_DPI
    try:
        config.read(config_path)
        server = config["server"]
        BASE_URL = server["BASE_URL"]
        prefs = config["prefs"]
        HIGH_DPI = prefs["high_dpi"]
    except:
        config["server"] = {
            "BASE_URL": ""
        }
        config["prefs"] = {
            "theme": "cyborg",
            "high_dpi": "off"
        }
        with open(config_path, 'w') as file:
            config.write(file)
        server = config["server"]
        BASE_URL = server["BASE_URL"]
        prefs = config["prefs"]
        HIGH_DPI = prefs["high_dpi"]

    try:
        api_key = server["api_key"]
    except:
        api_key = None

refresh_config()

def main():
    real_path = os.path.realpath(__file__)
    if os.name == "nt":
        icon_path = os.path.join(real_path.rsplit("\\", maxsplit=1)[0], "icon.png")
        template_dir = os.path.join(real_path.rsplit("\\", maxsplit=1)[0], "templates")
    else:
        icon_path = os.path.join(real_path.rsplit("/", maxsplit=1)[0], "icon.png")
        template_dir = os.path.join(real_path.rsplit("/", maxsplit=1)[0], "templates")
    if HIGH_DPI == "on" and os.name == "nt":
        global font_size
        global high_dpi_obj
        font_size = 12
        high_dpi_obj = utility.enable_high_dpi_awareness(scaling=1.75)
    j2_env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape())
    report_template = j2_env.get_template("report.html")
    window = ttk.Window(title="Ticket Auction Manager Main Menu", themename=prefs['theme'], iconphoto=icon_path)
    v_status = ttk.StringVar(window)
    style = ttk.Style()
    def reconfig_style():
        style.configure('.', font=("", font_size))
        if HIGH_DPI == "on":
            style.configure('Treeview', rowheight=42)
        else:
            style.configure('Treeview', rowheight=35)
        window.option_add('*TCombobox*Listbox.font', ('', font_size))
        window.option_add('*TCombobox.font', ('', font_size))
        window.option_add('*TEntry.font', ('', font_size))
        window.option_add('*TSpinbox.font', ('', font_size))
        window.option_add('*Treeview.font', ('', font_size))
    def linux_hidipi():
        if HIGH_DPI == "on" and os.name != "nt":
            global font_size
            global high_dpi_obj
            font_size = 12
            high_dpi_obj = utility.enable_high_dpi_awareness(root=window, scaling=1.75)

    linux_hidipi()
    reconfig_style()

    def set_band():
        global BAND_COLOR
        if window.style.theme.type == "dark":
            BAND_COLOR = "#202020"
        elif window.style.theme.type == "light":
            BAND_COLOR = "#DDDDDD"

    def cmd_check_cfg():
        try:
            result = get(f"{BASE_URL}", params={"api_key": api_key}, verify=False)
            if result.status_code == 200:
                v_status.set(f"Connected")
                lbl_status.config(bootstyle="success")
            else:
                v_status.set(f"Error: HTTP Response <{result.status}>")
                lbl_status.config(bootstyle="danger")
        except:
            if len(BASE_URL) == 0:
                v_status.set("Offline Mode")
                lbl_status.config(bootstyle="warning")
            else:
                v_status.set(f"Unable to connect, check conf")
                lbl_status.config(bootstyle="danger")

    def cmd_get_prefixes():
        l_pr = []
        l_di = {}
        try:
            repo = PrefixRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.get_all()
            if results:
                for r in results:
                    l_pr.append(r.prefix.capitalize())
                    l_di[r.prefix] = {"bootstyle": r.bootstyle, "sort_order": r.sort_order}
                cmb_prefix.config(values=l_pr)
                prefixes.clear()
                prefixes.update(**l_di)
        except:
            return {"prefix": "No Connection", "bootstyle": "secondary"}

    def cmd_set_style(_=None):
        if len(cmb_prefix.get()) > 0:
            result = prefixes[cmb_prefix.get().lower()]
            btn_tickets.config(bootstyle=result["bootstyle"], state="normal")
            btn_baskets.config(bootstyle=result["bootstyle"], state="normal")
            btn_drawing.config(bootstyle=result["bootstyle"], state="normal")
            btn_byname_text.config(bootstyle=result["bootstyle"], state="normal")
            btn_byname_call.config(bootstyle=result["bootstyle"], state="normal")
            btn_byname_both.config(bootstyle=result["bootstyle"], state="normal")
            btn_bybasket_text.config(bootstyle=result["bootstyle"], state="normal")
            btn_bybasket_call.config(bootstyle=result["bootstyle"], state="normal")
            btn_bybasket_both.config(bootstyle=result["bootstyle"], state="normal")

    def cmd_settings_window():
        window = ttk.Toplevel(title="TAM Settings")
        v_base_url = ttk.StringVar(window)
        v_base_url.set(server["BASE_URL"])
        v_api = ttk.StringVar(window)
        if api_key:
            v_api.set(api_key)
        v_api_name = ttk.StringVar(window)
        v_api_sts = ttk.StringVar(window)
        v_high_dpi = ttk.StringVar(window)
        if 'high_dpi' in prefs:
            v_high_dpi.set(prefs['high_dpi'])

        def save():
            config = ConfigParser()
            config["server"] = {
                "BASE_URL": v_base_url.get()
            }
            if v_api.get():
                config["server"]["api_key"] = v_api.get()
            config["prefs"] = {
                "theme": cmb_theme.get(),
                "high_dpi": v_high_dpi.get()
            }
            with open(config_path, 'w') as file:
                config.write(file)
            window.destroy()
            refresh_config()
            style.theme_use(themename=prefs['theme'])
            cmd_check_cfg(), set_band()
        
        def cancel():
            window.destroy()

        def gen_api_key():
            response = post(f"{v_base_url.get()}genapi/", json={"inp_pw": txt_api_pw.get(), "pc_name": txt_api_name.get()}, verify=False).json()
            try:
                set_api_key = response["api_key"]
                v_api.set(set_api_key)
                v_api_sts.set("API Key Generated and Appended to Save")
            except:
                v_api_sts.set("Password may not be correct, please try again.")

        def launch_prefix_manager():
            prefix_manager(BASE_URL, api_key)

        def launch_api_cleaner():
            api_cleaner(BASE_URL, api_key)

        frm_server = ttk.LabelFrame(window, text="Server Settings")
        frm_server.pack(padx=4, pady=4, fill="x")

        lbl_base_url = ttk.Label(frm_server, text="Base URL: ")
        lbl_base_url.grid(row=0, column=0, padx=4, pady=4)

        txt_base_url = ttk.Entry(frm_server, textvariable=v_base_url)
        txt_base_url.grid(row=0, column=1, padx=4, pady=4)

        lbl_secure_mode = ttk.Label(frm_server, text="If your server is in secure mode (API_PW env var is set), enter the API_PW and click Generate API Key")
        lbl_secure_mode.grid(row=1, column=0, columnspan=2, padx=4, pady=4)

        lbl_api_pw = ttk.Label(frm_server, text="API_PW")
        lbl_api_pw.grid(row=2, column=0, padx=4, pady=4)

        txt_api_pw = ttk.Entry(frm_server, show="*", width=20)
        txt_api_pw.grid(row=2, column=1, padx=4, pady=4)

        lbl_api_name = ttk.Label(frm_server, text="Computer Name")
        lbl_api_name.grid(row=3, column=0, padx=4, pady=4)

        txt_api_name = ttk.Entry(frm_server)
        txt_api_name.grid(row=3, column=1, padx=4, pady=4)

        btn_gen_api = ttk.Button(frm_server, text="Generate API Key", command=gen_api_key)
        btn_gen_api.grid(row=4, column=0, columnspan=2, padx=4, pady=4)

        lbl_gen_key_status = ttk.Label(frm_server, textvariable=v_api_sts)
        lbl_gen_key_status.grid(row=5, column=0, columnspan=2, padx=4, pady=4)

        frm_prefs = ttk.LabelFrame(window, text="Preferences")
        frm_prefs.pack(padx=4, pady=4, fill="x")

        lbl_theme = ttk.Label(frm_prefs, text="Theme: ")
        lbl_theme.grid(row=0, column=0, padx=4, pady=4)

        cmb_theme = ttk.Combobox(frm_prefs, state="readonly", values=("cyborg", "cosmo"))
        cmb_theme.grid(row=0, column=1, padx=4, pady=4)
        cmb_theme.set(prefs["theme"])

        lbl_high_dpi = ttk.Label(frm_prefs, text="High DPI")
        lbl_high_dpi.grid(row=1, column=0, padx=4, pady=4)

        chk_high_dpi = ttk.Checkbutton(frm_prefs, variable=v_high_dpi, onvalue="on", offvalue="off", textvariable=v_high_dpi, bootstyle="toolbutton")
        chk_high_dpi.grid(row=1, column=1, padx=4, pady=4)

        lbl_caution = ttk.Label(window, text="Settings take effect once you hit save.", anchor="center")
        lbl_caution.pack(padx=4, pady=4, fill="x")

        frm_btn = ttk.Frame(window)
        frm_btn.pack(padx=4, pady=4)

        btn_save = ttk.Button(frm_btn, text="Save", command=save)
        btn_save.pack(side="left", padx=4, pady=4)

        btn_cancel = ttk.Button(frm_btn, text="Cancel", bootstyle="secondary", command=cancel)
        btn_cancel.pack(side="left", padx=4, pady=4)

        frm_other_tools = ttk.LabelFrame(window, text="Other Tools")
        frm_other_tools.pack(padx=4, pady=4, fill="x")

        btn_prefix_manager = ttk.Button(frm_other_tools, text="Prefix Manager", command=launch_prefix_manager)
        btn_prefix_manager.pack(side="left", padx=4, pady=4)

        btn_api_cleaner = ttk.Button(frm_other_tools, text="Manage API Keys", command=launch_api_cleaner)
        btn_api_cleaner.pack(side="left", padx=4, pady=4)

    def cmd_ticket_form():
        ticket_form(BASE_URL, BAND_COLOR, api_key, cmb_prefix.get(), prefixes)

    def cmd_basket_form():
        basket_form(BASE_URL, BAND_COLOR, api_key, cmb_prefix.get(), prefixes)

    def cmd_drawing_form():
        drawing_form(BASE_URL, BAND_COLOR, api_key, cmb_prefix.get(), prefixes)

    def cmd_byname_text():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=text")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Name"
            title = "Winners Preferring Texts"
            headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_byname(prefix=cmb_prefix.get().lower(), preference="TEXT")
            records = [(r.winner_name, r.phone_number, r.basket_id, r.winning_ticket, r.description) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_byname_call():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=call")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Name"
            title = "Winners Preferring Calls"
            headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_byname(prefix=cmb_prefix.get().lower(), preference="CALL")
            records = [(r.winner_name, r.phone_number, r.basket_id, r.winning_ticket, r.description) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_byname_both():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Name"
            title = "All Preferences"
            headers = ("Winner Name", "Phone Number", "Basket #", "Ticket #", "Description")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_byname(prefix=cmb_prefix.get().lower())
            records = [(r.winner_name, r.phone_number, r.basket_id, r.winning_ticket, r.description) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_bybasket_text():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=text")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Basket #"
            title = "Winners Preferring Texts"
            headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_bybasket(prefix=cmb_prefix.get().lower(), preference="TEXT")
            records = [(r.basket_id, r.description, r.winning_ticket, r.winner_name, r.phone_number) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_bybasket_call():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=call")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Basket #"
            title = "Winners Preferring Calls"
            headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_bybasket(prefix=cmb_prefix.get().lower(), preference="CALL")
            records = [(r.basket_id, r.description, r.winning_ticket, r.winner_name, r.phone_number) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_bybasket_both():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}")
        else:
            maintitle = f"{cmb_prefix.get()} Basket Winners by Basket #"
            title = "All Preferences"
            headers = ("Basket #", "Basket Description", "Ticket #", "Winner Name", "Phone Number")
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            results = repo.report_bybasket(prefix=cmb_prefix.get().lower())
            records = [(r.basket_id, r.description, r.winning_ticket, r.winner_name, r.phone_number) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_view_counts():
        if len(BASE_URL) > 0:
            webbrowser.open(f"{BASE_URL}reports/counts/?api_key={api_key}")
        else:
            maintitle = "Ticket Counts"
            title = "Lists ticket counts"
            headers = ("Prefix", "All Ticket Lines", "Unique Buyers")
            repo = CountsRepo()
            results = repo.get_counts()
            records = [(r.prefix.capitalize(), r.total, r.unique) for r in results]
            out_file = report_template.render(maintitle=maintitle, title=title, headers=headers, records=records)
            report_path = save_report(out_file)
            webbrowser.open(report_path)

    def cmd_backup_form(_=None):
        backup_form(BASE_URL, api_key)

    frm_all_prefixes = ttk.LabelFrame(window, text="All Prefixes")
    frm_all_prefixes.pack(padx=4, pady=4, fill="x")

    btn_counts = ttk.Button(frm_all_prefixes, text="View Counts", command=cmd_view_counts, bootstyle="secondary")
    btn_counts.pack(side="left", padx=4, pady=4)
    
    frm_prefixes = ttk.LabelFrame(window, text="Prefix Selection")
    frm_prefixes.pack(padx=4, pady=4, fill="x")

    lbl_prefix = ttk.Label(frm_prefixes, text="Current Prefix: ")
    lbl_prefix.pack(side="left", padx=4, pady=4)

    cmb_prefix = ttk.Combobox(frm_prefixes, state="readonly")
    cmb_prefix.pack(side="left", padx=4, pady=4)

    btn_update_prefixes = ttk.Button(frm_prefixes, text="Update Prefixes", command=cmd_get_prefixes, bootstyle="secondary")
    btn_update_prefixes.pack(side="left", padx=4, pady=4)

    frm_forms = ttk.LabelFrame(window, text="Forms")
    frm_forms.pack(padx=4, pady=4, fill="x")

    btn_tickets = ttk.Button(frm_forms, text="Tickets", command=cmd_ticket_form, state="disabled")
    btn_tickets.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

    btn_baskets = ttk.Button(frm_forms, text="Baskets", command=cmd_basket_form, state="disabled")
    btn_baskets.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

    btn_drawing = ttk.Button(frm_forms, text="Drawing", command=cmd_drawing_form, state="disabled", width=50)
    btn_drawing.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

    frm_reports = ttk.LabelFrame(window, text="Reports")
    frm_reports.pack(padx=4, pady=4, fill="x")

    frm_byname = ttk.LabelFrame(frm_reports, text="By Name")
    frm_byname.pack(padx=4, pady=4, fill="x")

    btn_byname_text = ttk.Button(frm_byname, text="Text", command=cmd_byname_text, state="disabled")
    btn_byname_text.grid(row=0, column=0, padx=4, pady=4, sticky="nsew")

    btn_byname_call = ttk.Button(frm_byname, text="Call", command=cmd_byname_call, state="disabled")
    btn_byname_call.grid(row=0, column=1, padx=4, pady=4, sticky="nsew")

    btn_byname_both = ttk.Button(frm_byname, text="Both", command=cmd_byname_both, state="disabled", width=50)
    btn_byname_both.grid(row=1, column=0, columnspan=2, padx=4, pady=4)

    frm_bybasket = ttk.LabelFrame(frm_reports, text="By Basket")
    frm_bybasket.pack(padx=4, pady=4, fill="x")

    btn_bybasket_both = ttk.Button(frm_bybasket, text="Both", command=cmd_bybasket_both, state="disabled", width=50)
    btn_bybasket_both.grid(row=0, column=0, columnspan=2, padx=4, pady=4)

    btn_bybasket_text = ttk.Button(frm_bybasket, text="Text", command=cmd_bybasket_text, state="disabled")
    btn_bybasket_text.grid(row=1, column=0, padx=4, pady=4, sticky="nsew")

    btn_bybasket_call = ttk.Button(frm_bybasket, text="Call", command=cmd_bybasket_call, state="disabled")
    btn_bybasket_call.grid(row=1, column=1, padx=4, pady=4, sticky="nsew")

    frm_statusbar = ttk.Frame(window)
    frm_statusbar.pack(side="bottom", padx=4, pady=4, fill="x")

    lbl_status = ttk.Label(frm_statusbar, textvariable=v_status)
    lbl_status.pack(side="left", padx=4, pady=4)

    btn_settings = ttk.Button(frm_statusbar, text="Settings", command=cmd_settings_window)
    btn_settings.pack(side="left", padx=4, pady=4)

    lbl_attribution = ttk.Label(frm_statusbar, text="TAM by Dilan Gilluly")
    lbl_attribution.pack(side="right", padx=4, pady=4)

    cmd_check_cfg()
    prefixes = {}
    cmd_get_prefixes()
    set_band()

    cmb_prefix.bind("<<ComboboxSelected>>", cmd_set_style)

    window.bind("<Control-b>", cmd_backup_form)
    window.bind("<Control-B>", cmd_backup_form)

    window.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "backup":
            print(backup(BASE_URL, api_key, sys.argv[2]))
        elif sys.argv[1] == "ibackup":
            try:
                minutes = int(sys.argv[3])
            except:
                print("Please enter a number for how many minutes between backups after path.")
            ibackup(BASE_URL, api_key, sys.argv[2], minutes)
        elif sys.argv[1] == "restore":
            print(restore(BASE_URL, api_key, sys.argv[2]))
        elif sys.argv[1] == "makeportable":
            open("config.ini", "a").close()
            open("data.db", "a").close()
        else:
            main()
    else:
        main()