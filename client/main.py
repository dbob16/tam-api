import os
import ttkbootstrap as ttk 
from requests import get, post
from configparser import ConfigParser

def main():
    config = ConfigParser()
    try:
        config.read('config.ini')
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
        with open('config.ini', 'w') as file:
            config.write(file)
        server = config["server"]
        BASE_URL = server["BASE_URL"]
        prefs = config["prefs"]

    window = ttk.Window(title="Ticket Auction Manager Main Menu", themename=prefs["theme"])
    v_status = ttk.StringVar(window)

    def cmd_check_cfg():
        try:
            result = get(f"{BASE_URL}").json()
            if result["whoami"] == "TAM-Server":
                v_status.set("Status: Connected")
                lbl_status.config(bootstyle="success")
            else:
                v_status.set("Status: Invalid Server Data")
                lbl_status.config(bootstyle="danger")
        except:
            v_status.set("Status: Not Connected")
            lbl_status.config(bootstyle="danger")

    def cmd_get_prefixes():
        l_pr = []
        l_di = {}
        try:
            results = get(f"{BASE_URL}/prefixes/").json()
            for r in results:
                l_pr.append(r["prefix"].capitalize())
                l_di[r["prefix"]] = {"bootstyle": r["bootstyle"]}
            return l_pr, l_di
        except:
            return [], {}

    prefix_names, prefixes = cmd_get_prefixes()

    def cmd_set_style(_=None):
        if len(cmb_prefix.get()) > 0:
            result = prefixes[cmb_prefix.get().lower()]
            btn_tickets.config(bootstyle=result["bootstyle"], state="normal")
            btn_baskets.config(bootstyle=result["bootstyle"], state="normal")
            btn_drawing.config(bootstyle=result["bootstyle"], state="normal")

    def cmd_settings_window():
        window = ttk.Toplevel(title="TAM Settings")
        v_base_url = ttk.StringVar(window)
        v_base_url.set(server["BASE_URL"])

        def save():
            config["server"] = {
                "BASE_URL": v_base_url.get()
            }
            config["prefs"] = {
                "theme": cmb_theme.get()
            }
            with open('config.ini', 'w') as file:
                config.write(file)
            window.destroy()
        
        def cancel():
            window.destroy()

        frm_server = ttk.LabelFrame(window, text="Server Settings")
        frm_server.pack(padx=4, pady=4, fill="x")

        lbl_base_url = ttk.Label(frm_server, text="Base URL: ")
        lbl_base_url.grid(row=0, column=0, padx=4, pady=4)

        txt_base_url = ttk.Entry(frm_server, textvariable=v_base_url)
        txt_base_url.grid(row=0, column=1, padx=4, pady=4)

        frm_prefs = ttk.LabelFrame(window, text="Preferences")
        frm_prefs.pack(padx=4, pady=4, fill="x")

        lbl_theme = ttk.Label(frm_prefs, text="Theme: ")
        lbl_theme.grid(row=0, column=0, padx=4, pady=4)

        cmb_theme = ttk.Combobox(frm_prefs, state="readonly", values=("cyborg", "solar", "superhero", "darkly", "vapor", "cosmo", "flatly", "journal", "litera", "lumen", "minty", "pulse", "sandstone", "united", "yeti", "morph", "simplex", "ciculean"))
        cmb_theme.grid(row=0, column=1, padx=4, pady=4)
        cmb_theme.set(prefs["theme"])

        lbl_caution = ttk.Label(window, text="Settings won't take effect until you exit entire application and reopen.")
        lbl_caution.pack(padx=4, pady=4)

        frm_btn = ttk.Frame(window)
        frm_btn.pack(padx=4, pady=4)

        btn_save = ttk.Button(frm_btn, text="Save", command=save)
        btn_save.pack(side="left", padx=4, pady=4)

        btn_cancel = ttk.Button(frm_btn, text="Cancel", bootstyle="secondary", command=cancel)
        btn_cancel.pack(side="left", padx=4, pady=4)

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
            tview.delete(*tview.get_children())
            for i in range(v_from.get(), v_to.get()+1):
                tview.insert("", "end", iid=i, values=(i, "", "", "", "CALL"))
            results = get(f"{BASE_URL}tickets/{prefix.lower()}/{v_from.get()}/{v_to.get()}/").json()
            if results:
                for r in results:
                    tview.item(r["ticket_id"], values=(r["ticket_id"], r["first_name"], r["last_name"], r["phone_number"], r["preference"]))
            if v_id.get() < v_from.get():
                v_id.set(v_from.get())
            if v_id.get() > v_to.get():
                v_id.set(v_to.get())
            tview.selection_set(v_id.get())
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
                result = post(f"{BASE_URL}ticket/{prefix.lower()}/", json=s_item).json()
                if result["success"] == True:
                    tview.item(v_id.get(), values=(v_id.get(), v_fn.get(), v_ln.get(), v_pn.get(), v_pref.get()))

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
            txt_fn.focus()

        def cmd_move_down(_=None):
            cmd_save()
            if v_id.get() < v_to.get():
                v_id.set(v_id.get()+1)
                tview.selection_set(v_id.get())
            txt_fn.focus()

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

        btn_prev_page = ttk.Button(frm_ranger, text="Previous Page - Alt B", command=cmd_prev_page, bootstyle=bootstyle)
        btn_prev_page.pack(side="right", padx=4, pady=4)
        window.bind("<Alt-b>", cmd_prev_page)

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
        txt_pref.bind("<t>", cmd_set_text)

        frm_commands = ttk.LabelFrame(window, text="Commands")
        frm_commands.pack(padx=4, pady=4, fill="x")

        btn_move_up = ttk.Button(frm_commands, text="Move Up - Alt O", command=cmd_move_up, bootstyle=bootstyle)
        btn_move_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-o>", cmd_move_up)

        btn_move_down = ttk.Button(frm_commands, text="Move Down - Alt L", command=cmd_move_down, bootstyle=bootstyle)
        btn_move_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-l>", cmd_move_down)

        btn_dup_up = ttk.Button(frm_commands, text="Duplicate Up - Alt U", command=cmd_dup_up, bootstyle=bootstyle)
        btn_dup_up.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-u>", cmd_dup_up)

        btn_dup_down = ttk.Button(frm_commands, text="Duplicate Down - Alt J", command=cmd_dup_down, bootstyle=bootstyle)
        btn_dup_down.pack(side="left", padx=4, pady=4)
        window.bind("<Alt-j>", cmd_dup_down)

        btn_copy = ttk.Button(frm_commands, text="Copy - Ctrl C", command=cmd_copy, bootstyle=bootstyle)
        btn_copy.pack(side="left", padx=4, pady=4)
        window.bind("<Control-c>", cmd_copy)

        btn_paste = ttk.Button(frm_commands, text="Paste - Ctrl V", command=cmd_paste, bootstyle=bootstyle)
        btn_paste.pack(side="left", padx=4, pady=4)
        window.bind("<Control-v>", cmd_paste)

        frm_tv = ttk.LabelFrame(window, text="View Tickets")
        frm_tv.pack(padx=4, pady=4, fill="both", expand="yes")

        tv_sb = ttk.Scrollbar(frm_tv, orient="vertical")
        tv_sb.pack(side="right", padx=4, pady=4, fill="y")

        tview = ttk.Treeview(frm_tv, show="headings", columns=("id", "fn", "ln", "pn", "pref"), yscrollcommand=tv_sb.set)
        tview.heading("id", text="Ticket ID", anchor="w"), tview.heading("fn", text="First Name", anchor="w"), tview.heading("ln", text="Last Name", anchor="w")
        tview.heading("pn", text="Phone Number", anchor="w"), tview.heading("pref", text="Preference", anchor="w")
        tv_sb.config(command=tview.yview)
        tview.pack(padx=4, pady=4, fill="both", expand="yes")

        tview.bind("<<TreeviewSelect>>", cmd_tv_select)

        txt_from.focus()

    frm_prefixes = ttk.LabelFrame(window, text="Prefix Selection")
    frm_prefixes.pack(padx=4, pady=4, fill="x")

    lbl_prefix = ttk.Label(frm_prefixes, text="Current Prefix: ")
    lbl_prefix.pack(side="left", padx=4, pady=4)

    cmb_prefix = ttk.Combobox(frm_prefixes, state="readonly", values=prefix_names)
    cmb_prefix.pack(side="left", padx=4, pady=4)

    frm_forms = ttk.LabelFrame(window, text="Forms")
    frm_forms.pack(padx=4, pady=4, fill="x")

    btn_tickets = ttk.Button(frm_forms, text="Tickets", command=cmd_ticket_form, state="disabled")
    btn_tickets.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

    btn_baskets = ttk.Button(frm_forms, text="Baskets", state="disabled")
    btn_baskets.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

    btn_drawing = ttk.Button(frm_forms, text="Drawing", state="disabled", width=50)
    btn_drawing.grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="ew")

    frm_statusbar = ttk.Frame(window)
    frm_statusbar.pack(side="bottom", padx=4, pady=4, fill="x")

    lbl_status = ttk.Label(frm_statusbar, textvariable=v_status)
    lbl_status.pack(side="left", padx=4, pady=4)

    btn_settings = ttk.Button(frm_statusbar, text="Settings", command=cmd_settings_window)
    btn_settings.pack(side="left", padx=4, pady=4)

    lbl_attribution = ttk.Label(frm_statusbar, text="TAM by Dilan Gilluly")
    lbl_attribution.pack(side="right", padx=4, pady=4)

    cmd_check_cfg()

    cmb_prefix.bind("<<ComboboxSelected>>", cmd_set_style)

    window.mainloop()

if __name__ == "__main__":
    main()