import ttkbootstrap as ttk
from httpx import get, post

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

def ticket_form(BASE_URL:str, BAND_COLOR:str, api_key:str, prefix:str, prefixes:dict):
    prefix = prefix.lower()
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
            s_item = {"prefix": prefix, "ticket_id": v_id.get(), "first_name": v_fn.get(), "last_name": v_ln.get(), "phone_number": v_pn.get(), "preference": v_pref.get()}
            response = post(f"{BASE_URL}ticket/", json=s_item, params={"api_key": api_key}, verify=False)
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

    def on_close(window):
        if not tview.get_children():
            window.destroy()
            return
        if tview.item(v_id.get())["values"] != [v_id.get(), v_fn.get(), v_ln.get(), v_pn.get(), v_pref.get()]:
            dialog_response = ttk.dialogs.Messagebox.yesnocancel("Do you want to save before closing?", title="Save?",\
                parent=window, alert=None)
        else:
            window.destroy()
            return
        if dialog_response == "Yes":
            cmd_save()
            window.destroy()
            return
        elif dialog_response == "No":
            window.destroy()
            return
        elif dialog_response == "Cancel":
            pass

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
    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))

    txt_from.focus()