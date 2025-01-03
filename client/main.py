import os
import ttkbootstrap as ttk 
import webbrowser
from httpx import get, post
from configparser import ConfigParser
from prefix_manager import prefix_manager
from api_cleaner import api_cleaner

try:
    import names
    def generate_name():
        return names.get_first_name(), names.get_last_name()
except:
    pass

try:
    import random
    def generate_phone_number():
        def d01():
            return f"{random.randint(0,1)}"
        def d():
            return f"{random.randint(0,9)}"
        return f"{d01()}{d()}{d()}-{d()}{d()}{d()}-{d()}{d()}{d()}{d()}"
    def generate_preference():
        choices = ("TEXT", "CALL")
        return random.choice(choices)
except:
    pass

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

def main():
    config = ConfigParser()
    try:
        config.read(config_path)
        server = config["server"]
        BASE_URL = server["BASE_URL"]
        prefs = config["prefs"]
    except:
        config["server"] = {
            "BASE_URL": "http://localhost:8000/"
        }
        config["prefs"] = {
            "theme": "cyborg"
        }
        with open(config_path, 'w') as file:
            config.write(file)
        server = config["server"]
        BASE_URL = server["BASE_URL"]
        prefs = config["prefs"]

    try:
        api_key = server["api_key"]
    except:
        api_key = None

    window = ttk.Window(title="Ticket Auction Manager Main Menu", themename=prefs["theme"], iconphoto='icon.png')
    v_status = ttk.StringVar(window)

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
            v_status.set(f"Unable to connect, check conf")
            lbl_status.config(bootstyle="danger")

    def cmd_get_prefixes():
        l_pr = []
        l_di = {}
        try:
            response = get(f"{BASE_URL}prefixes/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                for r in response.json():
                    l_pr.append(r["prefix"].capitalize())
                    l_di[r["prefix"]] = {"bootstyle": r["bootstyle"], "sort_order": r["sort_order"]}
                cmb_prefix.config(values=l_pr)
                return l_di
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

        def save():
            config["server"] = {
                "BASE_URL": v_base_url.get()
            }
            if v_api.get():
                config["server"]["api_key"] = v_api.get()
            config["prefs"] = {
                "theme": cmb_theme.get()
            }
            with open(config_path, 'w') as file:
                config.write(file)
            window.destroy()
        
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

        lbl_caution = ttk.Label(window, text="Settings won't take effect until you exit entire application and reopen.", anchor="center")
        lbl_caution.pack(padx=4, pady=4, fill="x")

        frm_btn = ttk.Frame(window)
        frm_btn.pack(padx=4, pady=4)

        btn_save = ttk.Button(frm_btn, text="Save", command=save)
        btn_save.pack(side="left", padx=4, pady=4)

        btn_cancel = ttk.Button(frm_btn, text="Cancel", bootstyle="secondary", command=cancel)
        btn_cancel.pack(side="left", padx=4, pady=4)

        frm_other_tools = ttk.LabelFrame(window, text="Other Tools")
        frm_other_tools.pack(padx=4, pady=4, fill="x")

        btn_prefix_manager = ttk.Button(frm_other_tools, text="Prefix Manager", command=prefix_manager)
        btn_prefix_manager.pack(side="left", padx=4, pady=4)

        btn_api_cleaner = ttk.Button(frm_other_tools, text="Manage API Keys", command=api_cleaner)
        btn_api_cleaner.pack(side="left", padx=4, pady=4)

    def cmd_ticket_form():
        prefix = cmb_prefix.get().lower()
        bootstyle = prefixes[prefix]["bootstyle"]
        window = ttk.Toplevel(title=f"{prefix.capitalize()} Tickets")
        v_from, v_to = ttk.IntVar(window), ttk.IntVar(window)
        v_id, v_fn, v_ln, v_pn, v_pref = ttk.IntVar(window), ttk.StringVar(window), ttk.StringVar(window), ttk.StringVar(window), ttk.StringVar(window)
        save_record = []
        
        def cmd_set_call(_=None):
            v_pref.set("CALL")
        
        def cmd_set_text(_=None):
            v_pref.set("TEXT")

        def cmd_tv_select(_=None):
            for s in tview.selection():
                r = tview.item(s)["values"]
                v_id.set(r[0]), v_fn.set(r[1]), v_ln.set(r[2]), v_pn.set(r[3]), v_pref.set(r[4])

        def cmd_update_all(_=None):
            if len(tview.get_children()) > 0:
                cmd_save()
            tview.delete(*tview.get_children())
            for i in range(v_from.get(), v_to.get()+1):
                if i % 2 > 0:
                    tview.insert("", "end", iid=i, values=(i, "", "", "", "CALL"), tags=("oddrow",))
                else:
                    tview.insert("", "end", iid=i, values=(i, "", "", "", "CALL"))
            response = get(f"{BASE_URL}tickets/{prefix.lower()}/{v_from.get()}/{v_to.get()}/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                if response.json():
                    for r in response.json():
                        tview.item(r["ticket_id"], values=(r["ticket_id"], r["first_name"], r["last_name"], r["phone_number"], r["preference"]))
            v_id.set(v_from.get())
            tview.selection_set(v_id.get())
            tview.see(tview.selection())
            txt_fn.focus()

        def cmd_prev_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()-diff), v_to.set(v_to.get()-diff)
            cmd_update_all()

        def cmd_next_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()+diff), v_to.set(v_to.get()+diff)
            cmd_update_all()

        def cmd_save(_=None):
            if tview.item(v_id.get())["values"] != [v_id.get(), v_fn.get(), v_ln.get(), v_pn.get(), v_pref.get()]:
                s_item = {"ticket_id": v_id.get(), "first_name": v_fn.get(), "last_name": v_ln.get(), "phone_number": v_pn.get(), "preference": v_pref.get()}
                response = post(f"{BASE_URL}ticket/{prefix.lower()}/", json=s_item, params={"api_key": api_key}, verify=False)
                if response.status_code == 200:
                    tview.item(v_id.get(), values=[v_id.get(), v_fn.get(), v_ln.get(), v_pn.get(), v_pref.get()])

        def cmd_cancel(_=None):
            v = tview.item(v_id.get())["values"]
            v_fn.set(v[1]), v_ln.set(v[2]), v_pn.set(v[3]), v_pref.set(v[4])

        def cmd_copy(_=None):
            save_record.clear()
            for c in (v_fn, v_ln, v_pn, v_pref):
                save_record.append(c.get())
        
        def cmd_paste(_=None):
            index = 0
            for c in (v_fn, v_ln, v_pn, v_pref):
                c.set(save_record[index])
                index += 1
            cmd_save()

        def cmd_move_up(_=None):
            cmd_save()
            if v_id.get() > v_from.get():
                v_id.set(v_id.get()-1)
                tview.selection_set(v_id.get())
            if v_id.get() > v_from.get():
                tview.see(v_id.get()-1)
            else:
                tview.yview_moveto(0)
            txt_fn.focus()

        def cmd_move_down(_=None):
            cmd_save()
            if v_id.get() < v_to.get():
                v_id.set(v_id.get()+1)
                tview.selection_set(v_id.get())
            if v_id.get() < v_to.get():
                tview.see(v_id.get()+1)
            else:
                tview.yview_moveto(1)
            txt_fn.focus()

        def cmd_dup_up(_=None):
            cmd_copy()
            cmd_move_up()
            cmd_paste()

        def cmd_dup_down(_=None):
            cmd_copy()
            cmd_move_down()
            cmd_paste()

        def cmd_random(_=None):
            first_name, last_name = generate_name()
            phone_number = generate_phone_number()
            pref = generate_preference()
            v_fn.set(first_name), v_ln.set(last_name), v_pn.set(phone_number), v_pref.set(pref)

        frm_ranger = ttk.LabelFrame(window, text="Range Control")
        frm_ranger.pack(padx=4, pady=4, fill="x")

        lbl_from = ttk.Label(frm_ranger, text="Range: ")
        lbl_from.pack(side="left", padx=4, pady=4)

        txt_from = ttk.Entry(frm_ranger, textvariable=v_from, width=10)
        txt_from.pack(side="left", padx=4, pady=4)

        lbl_to = ttk.Label(frm_ranger, text=" - ")
        lbl_to.pack(side="left", padx=4, pady=4)

        txt_to = ttk.Entry(frm_ranger, textvariable=v_to, width=10)
        txt_to.pack(side="left", padx=4, pady=4)

        btn_go = ttk.Button(frm_ranger, text="Go", command=cmd_update_all, bootstyle=bootstyle)
        btn_go.pack(side="left", padx=4, pady=4)

        btn_next_page = ttk.Button(frm_ranger, text="Next Page - Alt N", command=cmd_next_page, bootstyle=bootstyle)
        btn_next_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-n>", cmd_next_page)
        window.bind("<Alt-N>", cmd_next_page)

        btn_prev_page = ttk.Button(frm_ranger, text="Previous Page - Alt B", command=cmd_prev_page, bootstyle=bootstyle)
        btn_prev_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-b>", cmd_prev_page)
        window.bind("<Alt-B>", cmd_prev_page)

        frm_current_record = ttk.LabelFrame(window, text="Current Record")
        frm_current_record.pack(padx=4, pady=4, fill="x")

        lbl_id = ttk.Label(frm_current_record, text="Ticket ID")
        lbl_id.grid(column=0, row=0, padx=4, pady=4)

        txt_id = ttk.Entry(frm_current_record, textvariable=v_id, state="readonly", width=10)
        txt_id.grid(column=0, row=1, padx=4, pady=4)

        lbl_fn = ttk.Label(frm_current_record, text="First Name")
        lbl_fn.grid(column=1, row=0, padx=4, pady=4)

        txt_fn = ttk.Entry(frm_current_record, textvariable=v_fn, width=20)
        txt_fn.grid(column=1, row=1, padx=4, pady=4)

        lbl_ln = ttk.Label(frm_current_record, text="Last Name")
        lbl_ln.grid(column=2, row=0, padx=4, pady=4)

        txt_ln = ttk.Entry(frm_current_record, textvariable=v_ln, width=20)
        txt_ln.grid(column=2, row=1, padx=4, pady=4)

        lbl_pn = ttk.Label(frm_current_record, text="Phone Number")
        lbl_pn.grid(column=3, row=0, padx=4, pady=4)

        txt_pn = ttk.Entry(frm_current_record, textvariable=v_pn, width=20)
        txt_pn.grid(column=3, row=1, padx=4, pady=4)

        lbl_pref = ttk.Label(frm_current_record, text="Preference")
        lbl_pref.grid(column=4, row=0, padx=4, pady=4)

        txt_pref = ttk.Entry(frm_current_record, textvariable=v_pref, state="readonly")
        txt_pref.grid(column=4, row=1, padx=4, pady=4)
        txt_pref.bind("<c>", cmd_set_call)
        txt_pref.bind("<C>", cmd_set_call)
        txt_pref.bind("<t>", cmd_set_text)
        txt_pref.bind("<T>", cmd_set_text)

        btn_save = ttk.Button(frm_current_record, text="Save", command=cmd_save, bootstyle=bootstyle)
        btn_save.grid(column=5, row=1, padx=4, pady=4)
        window.bind("<Control-s>", cmd_save)
        window.bind("<Control-S>", cmd_save)

        btn_cancel = ttk.Button(frm_current_record, text="Cancel", command=cmd_cancel, bootstyle=bootstyle)
        btn_cancel.grid(column=6, row=1, padx=4, pady=4)
        window.bind("<Escape>", cmd_cancel)
        
        window.bind("<Alt-r>", cmd_random)
        window.bind("<Alt-R>", cmd_random)

        frm_commands = ttk.LabelFrame(window, text="Commands")
        frm_commands.pack(padx=4, pady=4, fill="x")

        btn_move_up = ttk.Button(frm_commands, text="Move Up - Alt O", command=cmd_move_up, bootstyle=bootstyle)
        btn_move_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-o>", cmd_move_up)
        window.bind("<Alt-O>", cmd_move_up)

        btn_move_down = ttk.Button(frm_commands, text="Move Down - Alt L", command=cmd_move_down, bootstyle=bootstyle)
        btn_move_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-l>", cmd_move_down)
        window.bind("<Alt-L>", cmd_move_down)

        btn_dup_up = ttk.Button(frm_commands, text="Duplicate Up - Alt U", command=cmd_dup_up, bootstyle=bootstyle)
        btn_dup_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-u>", cmd_dup_up)
        window.bind("<Alt-U>", cmd_dup_up)

        btn_dup_down = ttk.Button(frm_commands, text="Duplicate Down - Alt J", command=cmd_dup_down, bootstyle=bootstyle)
        btn_dup_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-j>", cmd_dup_down)
        window.bind("<Alt-J>", cmd_dup_down)

        btn_copy = ttk.Button(frm_commands, text="Copy - Alt C", command=cmd_copy, bootstyle=bootstyle)
        btn_copy.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-c>", cmd_copy)
        window.bind("<Alt-C>", cmd_copy)

        btn_paste = ttk.Button(frm_commands, text="Paste - Alt V", command=cmd_paste, bootstyle=bootstyle)
        btn_paste.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-v>", cmd_paste)
        window.bind("<Alt-V>", cmd_paste)

        frm_tv = ttk.LabelFrame(window, text="View Tickets")
        frm_tv.pack(padx=4, pady=4, fill="both", expand="yes")

        tv_sb = ttk.Scrollbar(frm_tv, orient="vertical")
        tv_sb.pack(side="right", padx=4, pady=4, fill="y")

        tview = ttk.Treeview(frm_tv, show="headings", columns=("id", "fn", "ln", "pn", "pref"), yscrollcommand=tv_sb.set)
        tview.heading("id", text="Ticket ID", anchor="w"), tview.heading("fn", text="First Name", anchor="w"), tview.heading("ln", text="Last Name", anchor="w")
        tview.heading("pn", text="Phone Number", anchor="w"), tview.heading("pref", text="Preference", anchor="w")
        tv_sb.config(command=tview.yview)
        tview.pack(padx=4, pady=4, fill="both", expand="yes")
        tview.tag_configure("oddrow", background=BAND_COLOR)

        tview.bind("<<TreeviewSelect>>", cmd_tv_select)

        txt_from.focus()

    def cmd_basket_form():
        prefix = cmb_prefix.get().lower()
        bootstyle = prefixes[prefix]["bootstyle"]
        window = ttk.Toplevel(title=f"{prefix.capitalize()} Baskets")
        v_from, v_to = ttk.IntVar(window), ttk.IntVar(window)
        v_id, v_de, v_do, v_wt = ttk.IntVar(window), ttk.StringVar(window), ttk.StringVar(window), ttk.IntVar(window)
        save_record = []
        
        def cmd_set_call(_=None):
            v_pref.set("CALL")
        
        def cmd_set_text(_=None):
            v_pref.set("TEXT")

        def cmd_tv_select(_=None):
            for s in tview.selection():
                r = tview.item(s)["values"]
                v_id.set(r[0]), v_de.set(r[1]), v_do.set(r[2]), v_wt.set(r[3])

        def cmd_update_all(_=None):
            if len(tview.get_children()) > 0:
                cmd_save()
            tview.delete(*tview.get_children())
            for i in range(v_from.get(), v_to.get()+1):
                if i % 2 > 0:
                    tview.insert("", "end", iid=i, values=(i, "", "", 0), tags=("oddrow",))
                else:
                    tview.insert("", "end", iid=i, values=(i, "", "", 0))
            response = get(f"{BASE_URL}baskets/{prefix.lower()}/{v_from.get()}/{v_to.get()}/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                if response.json():
                    for r in response.json():
                        tview.item(r["basket_id"], values=(r["basket_id"], r["description"], r["donors"], r["winning_ticket"]))
            v_id.set(v_from.get())
            tview.selection_set(v_id.get())
            tview.see(tview.selection())
            txt_de.focus()

        def cmd_prev_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()-diff), v_to.set(v_to.get()-diff)
            cmd_update_all()

        def cmd_next_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()+diff), v_to.set(v_to.get()+diff)
            cmd_update_all()

        def cmd_save(_=None):
            if tview.item(v_id.get())["values"] != [v_id.get(), v_de.get(), v_do.get(), v_wt.get()]:
                s_item = {"basket_id": v_id.get(), "description": v_de.get(), "donors": v_do.get(), "winning_ticket": v_wt.get()}
                result = post(f"{BASE_URL}basket/{prefix.lower()}/", json=s_item, params={"api_key": api_key}, verify=False)
                if result.status_code == 200:
                    tview.item(v_id.get(), values=(v_id.get(), v_de.get(), v_do.get(), v_wt.get()))
        
        def cmd_cancel(_=None):
            v = tview.item(v_id.get())["values"]
            v_de.set(v[1]), v_do.set(v[2])

        def cmd_copy(_=None):
            save_record.clear()
            for c in (v_de, v_do):
                save_record.append(c.get())
        
        def cmd_paste(_=None):
            index = 0
            for c in (v_de, v_do):
                c.set(save_record[index])
                index += 1
            cmd_save()

        def cmd_move_up(_=None):
            cmd_save()
            if v_id.get() > v_from.get():
                v_id.set(v_id.get()-1)
                tview.selection_set(v_id.get())
            if v_id.get() > v_from.get():
                tview.see(v_id.get()-1)
            else:
                tview.yview_moveto(0)
            txt_de.focus()

        def cmd_move_down(_=None):
            cmd_save()
            if v_id.get() < v_to.get():
                v_id.set(v_id.get()+1)
                tview.selection_set(v_id.get())
            if v_id.get() < v_to.get():
                tview.see(v_id.get()+1)
            else:
                tview.yview_moveto(1)
            txt_de.focus()

        def cmd_dup_up(_=None):
            cmd_copy()
            cmd_move_up()
            cmd_paste()

        def cmd_dup_down(_=None):
            cmd_copy()
            cmd_move_down()
            cmd_paste()

        frm_ranger = ttk.LabelFrame(window, text="Range Control")
        frm_ranger.pack(padx=4, pady=4, fill="x")

        lbl_from = ttk.Label(frm_ranger, text="Range: ")
        lbl_from.pack(side="left", padx=4, pady=4)

        txt_from = ttk.Entry(frm_ranger, textvariable=v_from, width=10)
        txt_from.pack(side="left", padx=4, pady=4)

        lbl_to = ttk.Label(frm_ranger, text=" - ")
        lbl_to.pack(side="left", padx=4, pady=4)

        txt_to = ttk.Entry(frm_ranger, textvariable=v_to, width=10)
        txt_to.pack(side="left", padx=4, pady=4)

        btn_go = ttk.Button(frm_ranger, text="Go", command=cmd_update_all, bootstyle=bootstyle)
        btn_go.pack(side="left", padx=4, pady=4)

        btn_next_page = ttk.Button(frm_ranger, text="Next Page - Alt N", command=cmd_next_page, bootstyle=bootstyle)
        btn_next_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-n>", cmd_next_page)
        window.bind("<Alt-N>", cmd_next_page)

        btn_prev_page = ttk.Button(frm_ranger, text="Previous Page - Alt B", command=cmd_prev_page, bootstyle=bootstyle)
        btn_prev_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-b>", cmd_prev_page)
        window.bind("<Alt-B>", cmd_prev_page)

        frm_current_record = ttk.LabelFrame(window, text="Current Record")
        frm_current_record.pack(padx=4, pady=4, fill="x")

        lbl_id = ttk.Label(frm_current_record, text="Basket ID")
        lbl_id.grid(column=0, row=0, padx=4, pady=4)

        txt_id = ttk.Entry(frm_current_record, textvariable=v_id, state="readonly", width=10)
        txt_id.grid(column=0, row=1, padx=4, pady=4)

        lbl_de = ttk.Label(frm_current_record, text="Description")
        lbl_de.grid(column=1, row=0, padx=4, pady=4)

        txt_de = ttk.Entry(frm_current_record, textvariable=v_de, width=20)
        txt_de.grid(column=1, row=1, padx=4, pady=4)

        lbl_do = ttk.Label(frm_current_record, text="Donors")
        lbl_do.grid(column=2, row=0, padx=4, pady=4)

        txt_do = ttk.Entry(frm_current_record, textvariable=v_do, width=20)
        txt_do.grid(column=2, row=1, padx=4, pady=4)

        lbl_wt = ttk.Label(frm_current_record, text="Winning Ticket")
        lbl_wt.grid(column=3, row=0, padx=4, pady=4)

        txt_wt = ttk.Entry(frm_current_record, textvariable=v_wt, state="readonly", width=10)
        txt_wt.grid(column=3, row=1, padx=4, pady=4)

        btn_save = ttk.Button(frm_current_record, text="Save", command=cmd_save, bootstyle=bootstyle)
        btn_save.grid(column=4, row=1, padx=4, pady=4)
        window.bind("<Control-s>", cmd_save)
        window.bind("<Control-S>", cmd_save)

        btn_cancel = ttk.Button(frm_current_record, text="Cancel", command=cmd_cancel, bootstyle=bootstyle)
        btn_cancel.grid(column=5, row=1, padx=4, pady=4)
        window.bind("<Escape>", cmd_cancel)

        frm_commands = ttk.LabelFrame(window, text="Commands")
        frm_commands.pack(padx=4, pady=4, fill="x")

        btn_move_up = ttk.Button(frm_commands, text="Move Up - Alt O", command=cmd_move_up, bootstyle=bootstyle)
        btn_move_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-o>", cmd_move_up)
        window.bind("<Alt-O>", cmd_move_up)

        btn_move_down = ttk.Button(frm_commands, text="Move Down - Alt L", command=cmd_move_down, bootstyle=bootstyle)
        btn_move_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-l>", cmd_move_down)
        window.bind("<Alt-L>", cmd_move_down)

        btn_dup_up = ttk.Button(frm_commands, text="Duplicate Up - Alt U", command=cmd_dup_up, bootstyle=bootstyle)
        btn_dup_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-u>", cmd_dup_up)
        window.bind("<Alt-U>", cmd_dup_up)

        btn_dup_down = ttk.Button(frm_commands, text="Duplicate Down - Alt J", command=cmd_dup_down, bootstyle=bootstyle)
        btn_dup_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-j>", cmd_dup_down)
        window.bind("<Alt-J>", cmd_dup_down)

        btn_copy = ttk.Button(frm_commands, text="Copy - Alt C", command=cmd_copy, bootstyle=bootstyle)
        btn_copy.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-c>", cmd_copy)
        window.bind("<Alt-C>", cmd_copy)

        btn_paste = ttk.Button(frm_commands, text="Paste - Alt V", command=cmd_paste, bootstyle=bootstyle)
        btn_paste.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-v>", cmd_paste)
        window.bind("<Alt-V>", cmd_paste)

        frm_tv = ttk.LabelFrame(window, text="View Tickets")
        frm_tv.pack(padx=4, pady=4, fill="both", expand="yes")

        tv_sb = ttk.Scrollbar(frm_tv, orient="vertical")
        tv_sb.pack(side="right", padx=4, pady=4, fill="y")

        tview = ttk.Treeview(frm_tv, show="headings", columns=("id", "de", "do", "wt"), yscrollcommand=tv_sb.set)
        tview.heading("id", text="Basket ID", anchor="w"), tview.heading("de", text="Description", anchor="w"), tview.heading("do", text="Donors", anchor="w")
        tview.heading("wt", text="Winning Ticket", anchor="w")
        tv_sb.config(command=tview.yview)
        tview.pack(padx=4, pady=4, fill="both", expand="yes")
        tview.tag_configure("oddrow", background=BAND_COLOR)

        tview.bind("<<TreeviewSelect>>", cmd_tv_select)

        txt_from.focus()

    def cmd_drawing_form():
        prefix = cmb_prefix.get().lower()
        bootstyle = prefixes[prefix]["bootstyle"]
        window = ttk.Toplevel(title=f"{prefix.capitalize()} Drawing")
        v_from, v_to = ttk.IntVar(window), ttk.IntVar(window)
        v_id, v_de, v_do, v_wt = ttk.IntVar(window), ttk.StringVar(window), ttk.StringVar(window), ttk.IntVar(window)
        v_wn = ttk.StringVar(window)
        save_record = []
        
        def cmd_set_call(_=None):
            v_pref.set("CALL")
        
        def cmd_set_text(_=None):
            v_pref.set("TEXT")

        def cmd_tv_select(_=None):
            for s in tview.selection():
                r = tview.item(s)["values"]
                v_id.set(r[0]), v_de.set(r[1]), v_do.set(r[2]), v_wt.set(r[3]), v_wn.set(r[4])

        def cmd_update_all(_=None):
            if len(tview.get_children()) > 0:
                cmd_save()
            tview.delete(*tview.get_children())
            for i in range(v_from.get(), v_to.get()+1):
                if i % 2 > 0:
                    tview.insert("", "end", iid=i, values=(i, "", "", 0, "No Winner"), tags=("oddrow",))
                else:
                    tview.insert("", "end", iid=i, values=(i, "", "", 0, "No Winner"))
            response = get(f"{BASE_URL}baskets/{prefix.lower()}/{v_from.get()}/{v_to.get()}/", params={"api_key": api_key}, verify=False)
            if response.status_code == 200:
                results = response.json()
                if results:
                    for r in results:
                        tview.item(r["basket_id"], values=(r["basket_id"], r["description"], r["donors"], r["winning_ticket"], "No Winner"))
            c_response = get(f"{BASE_URL}combined/{prefix.lower()}/{v_from.get()}/{v_to.get()}/", params={"api_key": api_key}, verify=False)
            if c_response.status_code == 200:
                c_results = c_response.json()
                if c_results:
                    for r in c_results:
                        tview.set(r["basket_id"], "wi", f"{r["last_name"]}, {r["first_name"]}")
            v_id.set(v_from.get())
            tview.selection_set(v_id.get())
            tview.see(tview.selection())
            txt_wt.focus()

        def cmd_prev_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()-diff), v_to.set(v_to.get()-diff)
            cmd_update_all()

        def cmd_next_page(_=None):
            diff = v_to.get()-v_from.get()+1
            v_from.set(v_from.get()+diff), v_to.set(v_to.get()+diff)
            cmd_update_all()

        def cmd_save(_=None):
            if tview.item(v_id.get())["values"] != [v_id.get(), v_de.get(), v_do.get(), v_wt.get(), v_wn.get()]:
                s_item = {"basket_id": v_id.get(), "description": v_de.get(), "donors": v_do.get(), "winning_ticket": v_wt.get()}
                response = post(f"{BASE_URL}basket/{prefix.lower()}/", json=s_item, params={"api_key": api_key}, verify=False)
                if response.status_code == 200:
                    tview.item(v_id.get(), values=(v_id.get(), v_de.get(), v_do.get(), v_wt.get(), "No Winner"))
                    c_response = get(f"{BASE_URL}combined/{prefix.lower()}/{v_id.get()}/", params={"api_key": api_key}, verify=False)
                    if c_response.status_code == 200:
                        c_result = c_response.json()
                        if c_result:
                            tview.set(v_id.get(), "wi", f"{c_result["last_name"]}, {c_result["first_name"]}")

        def cmd_cancel(_=None):
            r = tview.item(v_id.get())["values"]
            v_de.set(r[1]), v_do.set(r[2]), v_wt.set(r[3]), v_wn.set(r[4])

        def cmd_copy(_=None):
            save_record.clear()
            save_record.append(v_wt.get())
        
        def cmd_paste(_=None):
            v_wt.set(save_record[0])

        def cmd_move_up(_=None):
            cmd_save()
            if v_id.get() > v_from.get():
                v_id.set(v_id.get()-1)
                tview.selection_set(v_id.get())
            if v_id.get() > v_from.get():
                tview.see(v_id.get()-1)
            else:
                tview.yview_moveto(0)
            txt_wt.focus()

        def cmd_move_down(_=None):
            cmd_save()
            if v_id.get() < v_to.get():
                v_id.set(v_id.get()+1)
                tview.selection_set(v_id.get())
            if v_id.get() < v_to.get():
                tview.see(v_id.get()+1)
            else:
                tview.yview_moveto(1)
            txt_wt.focus()

        def cmd_dup_up(_=None):
            cmd_copy()
            cmd_move_up()
            cmd_paste()

        def cmd_dup_down(_=None):
            cmd_copy()
            cmd_move_down()
            cmd_paste()

        def cmd_random(_=None):
            try:
                result = get(f"{BASE_URL}random/tickets/{prefix}/", params={"api_key": api_key}, verify=False).json()
                v_wt.set(result["ticket_id"])
            except:
                pass

        def cmd_clear_wt(_=None):
            v_wt.set("")

        frm_ranger = ttk.LabelFrame(window, text="Range Control")
        frm_ranger.pack(padx=4, pady=4, fill="x")

        lbl_from = ttk.Label(frm_ranger, text="Range: ")
        lbl_from.pack(side="left", padx=4, pady=4)

        txt_from = ttk.Entry(frm_ranger, textvariable=v_from, width=10)
        txt_from.pack(side="left", padx=4, pady=4)

        lbl_to = ttk.Label(frm_ranger, text=" - ")
        lbl_to.pack(side="left", padx=4, pady=4)

        txt_to = ttk.Entry(frm_ranger, textvariable=v_to, width=10)
        txt_to.pack(side="left", padx=4, pady=4)

        btn_go = ttk.Button(frm_ranger, text="Go", command=cmd_update_all, bootstyle=bootstyle)
        btn_go.pack(side="left", padx=4, pady=4)

        btn_next_page = ttk.Button(frm_ranger, text="Next Page - Alt N", command=cmd_next_page, bootstyle=bootstyle)
        btn_next_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-n>", cmd_next_page)
        window.bind("<Alt-N>", cmd_next_page)

        btn_prev_page = ttk.Button(frm_ranger, text="Previous Page - Alt B", command=cmd_prev_page, bootstyle=bootstyle)
        btn_prev_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-b>", cmd_prev_page)
        window.bind("<Alt-B>", cmd_prev_page)

        frm_current_record = ttk.LabelFrame(window, text="Current Record")
        frm_current_record.pack(padx=4, pady=4, fill="x")

        lbl_id = ttk.Label(frm_current_record, text="Basket ID")
        lbl_id.grid(column=0, row=0, padx=4, pady=4)

        txt_id = ttk.Entry(frm_current_record, textvariable=v_id, state="readonly", width=10)
        txt_id.grid(column=0, row=1, padx=4, pady=4)

        lbl_de = ttk.Label(frm_current_record, text="Description")
        lbl_de.grid(column=1, row=0, padx=4, pady=4)

        txt_de = ttk.Entry(frm_current_record, textvariable=v_de, state="readonly", width=20)
        txt_de.grid(column=1, row=1, padx=4, pady=4)

        lbl_do = ttk.Label(frm_current_record, text="Donors")
        lbl_do.grid(column=2, row=0, padx=4, pady=4)

        txt_do = ttk.Entry(frm_current_record, textvariable=v_do, state="readonly", width=20)
        txt_do.grid(column=2, row=1, padx=4, pady=4)

        lbl_wt = ttk.Label(frm_current_record, text="Winning Ticket")
        lbl_wt.grid(column=3, row=0, padx=4, pady=4)

        txt_wt = ttk.Entry(frm_current_record, textvariable=v_wt, width=10)
        txt_wt.grid(column=3, row=1, padx=4, pady=4)
        window.bind("<Alt-m>", cmd_clear_wt)
        window.bind("<Alt-M>", cmd_clear_wt)

        btn_save = ttk.Button(frm_current_record, text="Save", command=cmd_save, bootstyle=bootstyle)
        btn_save.grid(column=4, row=1, padx=4, pady=4)
        window.bind("<Control-s>", cmd_save)
        window.bind("<Control-S>", cmd_save)

        btn_cancel = ttk.Button(frm_current_record, text="Cancel", command=cmd_cancel, bootstyle=bootstyle)
        btn_cancel.grid(column=5, row=1, padx=4, pady=4)
        window.bind("<Escape>", cmd_cancel)

        window.bind("<Alt-r>", cmd_random)
        window.bind("<Alt-R>", cmd_random)

        frm_commands = ttk.LabelFrame(window, text="Commands")
        frm_commands.pack(padx=4, pady=4, fill="x")

        btn_move_up = ttk.Button(frm_commands, text="Move Up - Alt O", command=cmd_move_up, bootstyle=bootstyle)
        btn_move_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-o>", cmd_move_up)
        window.bind("<Alt-O>", cmd_move_up)

        btn_move_down = ttk.Button(frm_commands, text="Move Down - Alt L", command=cmd_move_down, bootstyle=bootstyle)
        btn_move_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-l>", cmd_move_down)
        window.bind("<Alt-L>", cmd_move_down)

        btn_dup_up = ttk.Button(frm_commands, text="Duplicate Up - Alt U", command=cmd_dup_up, bootstyle=bootstyle)
        btn_dup_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-u>", cmd_dup_up)
        window.bind("<Alt-U>", cmd_dup_up)

        btn_dup_down = ttk.Button(frm_commands, text="Duplicate Down - Alt J", command=cmd_dup_down, bootstyle=bootstyle)
        btn_dup_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-j>", cmd_dup_down)
        window.bind("<Alt-J>", cmd_dup_down)

        btn_copy = ttk.Button(frm_commands, text="Copy - Alt C", command=cmd_copy, bootstyle=bootstyle)
        btn_copy.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-c>", cmd_copy)
        window.bind("<Alt-C>", cmd_copy)

        btn_paste = ttk.Button(frm_commands, text="Paste - Alt V", command=cmd_paste, bootstyle=bootstyle)
        btn_paste.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-v>", cmd_paste)
        window.bind("<Alt-V>", cmd_paste)

        frm_tv = ttk.LabelFrame(window, text="View Tickets")
        frm_tv.pack(padx=4, pady=4, fill="both", expand="yes")

        tv_sb = ttk.Scrollbar(frm_tv, orient="vertical")
        tv_sb.pack(side="right", padx=4, pady=4, fill="y")

        tview = ttk.Treeview(frm_tv, show="headings", columns=("id", "de", "do", "wt", "wi"), yscrollcommand=tv_sb.set)
        tview.heading("id", text="Basket ID", anchor="w"), tview.heading("de", text="Description", anchor="w"), tview.heading("do", text="Donors", anchor="w")
        tview.heading("wt", text="Winning Ticket", anchor="w"), tview.heading("wi", text="Winner", anchor="w")
        tv_sb.config(command=tview.yview)
        tview.pack(padx=4, pady=4, fill="both", expand="yes")
        tview.tag_configure("oddrow", background=BAND_COLOR)

        tview.bind("<<TreeviewSelect>>", cmd_tv_select)

        txt_from.focus()

    def cmd_byname_text():
        webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=text")

    def cmd_byname_call():
        webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=call")

    def cmd_byname_both():
        webbrowser.open(f"{BASE_URL}reports/byname/{cmb_prefix.get().lower()}/?api_key={api_key}")

    def cmd_bybasket_text():
        webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=text")

    def cmd_bybasket_call():
        webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}&filter=call")

    def cmd_bybasket_both():
        webbrowser.open(f"{BASE_URL}reports/bybasket/{cmb_prefix.get().lower()}/?api_key={api_key}")

    def cmd_view_counts():
        webbrowser.open(f"{BASE_URL}reports/counts/?api_key={api_key}")

    
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
    prefixes = cmd_get_prefixes()

    cmb_prefix.bind("<<ComboboxSelected>>", cmd_set_style)

    window.mainloop()

if __name__ == "__main__":
    main()