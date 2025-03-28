import ttkbootstrap as ttk
from dao import BasketRepo, Basket, WinnerRepo, BasketWinner, TicketRepo, Ticket

def drawing_form(BASE_URL:str, BAND_COLOR:str, api_key:str, prefix:str, prefixes:dict):
    prefix = prefix.lower()
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
        repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
        results = repo.get_basket_range(prefix, v_from.get(), v_to.get())
        if results:
            for r in results:
                if r.winner_name == ", ":
                    tview.item(r.basket_id, values=[r.basket_id, r.description, r.donors, r.winning_ticket, "No Winner"])
                else:
                    tview.item(r.basket_id, values=[r.basket_id, r.description, r.donors, r.winning_ticket, r.winner_name])
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
            repo = BasketRepo(BASE_URL=BASE_URL, api_key=api_key)
            repo.update_winner(prefix, v_id.get(), v_wt.get())
            repo = WinnerRepo(BASE_URL=BASE_URL, api_key=api_key)
            w = repo.get_basket_one(prefix, v_id.get())
            if w.winner_name == ", ":
                tview.item(w.basket_id, values=[w.basket_id, w.description, w.donors, w.winning_ticket, "No Winner"])
            else:
                tview.item(w.basket_id, values=[w.basket_id, w.description, w.donors, w.winning_ticket, w.winner_name])

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
        repo = TicketRepo(BASE_URL=BASE_URL, api_key=api_key)
        try:
            t = repo.get_random(prefix)
            v_wt.set(t.ticket_id)
        except:
            pass

    def cmd_clear_wt(_=None):
        v_wt.set("")
    
    def on_close(window:ttk.Toplevel):
        if not tview.get_children():
            window.destroy()
            return
        if tview.item(v_id.get())["values"] != [v_id.get(), v_de.get(), v_do.get(), v_wt.get(), v_wn.get()]:
            dialog_response = ttk.dialogs.Messagebox.yesnocancel("Do you want to save before closing?", title="Save",\
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

    window.protocol("WM_DELETE_WINDOW", lambda: on_close(window))

    txt_from.focus()