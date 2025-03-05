import os
import ttkbootstrap as ttk 
import webbrowser
from httpx import get, post, delete

bootstyle_values = ("primary", "secondary", "success", "info", "warning", "danger", "light", "dark")

def prefix_manager(BASE_URL:str=None, api_key:str=None):
    window = ttk.Toplevel(title="TAM Prefix Manager")
    v_status = ttk.StringVar(window)
    d_current = {}

    def cmd_get_prefixes():
        response = get(f"{BASE_URL}prefixes/", params={"api_key": api_key}, verify=False)
        if response.status_code == 200:
            d_current.clear()
            r_j = response.json()
            p_l = [r["prefix"] for r in r_j]
            cmb_prefix.config(values=p_l)
            for r in r_j:
                d_current[r["prefix"]] = {"bootstyle": r["bootstyle"], "sort_order": r["sort_order"]}
        else:
            v_status.set(f"Getting list of prefixes unsuccessful, status code <{response.status_code}>")
            lbl_status.config(bootstyle="danger")

    def cmd_cmb_prefix(_=None):
        cr = d_current[cmb_prefix.get()]
        cmb_bootstyle.set(cr["bootstyle"])
        spn_sort_order.set(cr["sort_order"])

    def cmd_add_prefix():
        response = post(f"{BASE_URL}prefix/", json={"prefix": cmb_prefix.get(), "bootstyle": cmb_bootstyle.get(), "sort_order": spn_sort_order.get()}, params={"api_key": api_key}, verify=False)
        if response.status_code == 200:
            v_status.set(f"Created prefix {cmb_prefix.get()} successfully")
            lbl_status.config(bootstyle="success")
            cmd_get_prefixes()
        else:
            v_status.set(f"Prefix creation unsuccessful, status code <{response.status_code}>")
            lbl_status.config(bootstyle="danger")

    def cmd_rm_prefix():
        response = delete(f"{BASE_URL}delprefix/", params={"api_key": api_key, "prefix": cmb_prefix.get()}, verify=False)
        if response.status_code == 200:
            v_status.set(f"Deleted prefix {cmb_prefix.get()} successfully")
            lbl_status.config(bootstyle="success")
            cmd_get_prefixes()
        else:
            v_status.set(f"Prefix deletion unsuccessful, status code <{response.status_code}>")

    frm_prefixes = ttk.LabelFrame(window, text="Prefixes")
    frm_prefixes.pack(padx=4, pady=4, fill="x")

    lbl_prefix = ttk.Label(frm_prefixes, text="Prefix")
    lbl_prefix.grid(row=0, column=0)

    cmb_prefix = ttk.Combobox(frm_prefixes)
    cmb_prefix.grid(row=1, column=0, padx=4, pady=4)
    cmb_prefix.bind("<<ComboboxSelected>>", cmd_cmb_prefix)

    lbl_bootstyle = ttk.Label(frm_prefixes, text="Bootsyle")
    lbl_bootstyle.grid(row=0, column=1, padx=4, pady=4)

    cmb_bootstyle = ttk.Combobox(frm_prefixes, state="readonly", values=bootstyle_values)
    cmb_bootstyle.grid(row=1, column=1, padx=4, pady=4)

    lbl_sort_order = ttk.Label(frm_prefixes, text="Sort Order")
    lbl_sort_order.grid(row=0, column=2)

    spn_sort_order = ttk.Spinbox(frm_prefixes, from_=1, to=9)
    spn_sort_order.grid(row=1, column=2, padx=4, pady=4)

    btn_add_update = ttk.Button(frm_prefixes, text="Add/Update", command=cmd_add_prefix)
    btn_add_update.grid(row=1, column=3, padx=4, pady=4)

    btn_remove = ttk.Button(frm_prefixes, text="Remove", bootstyle="danger", command=cmd_rm_prefix)
    btn_remove.grid(row=1, column=4, padx=4, pady=4)

    frm_showcase = ttk.LabelFrame(window, text="Showcase")
    frm_showcase.pack(padx=4, pady=4, fill="x")

    btn_bootstyle_primary = ttk.Button(frm_showcase, text="Primary", bootstyle="primary", command=lambda: cmb_bootstyle.set("primary"))
    btn_bootstyle_primary.pack(side="left", padx=4, pady=4)

    btn_bootstyle_secondary = ttk.Button(frm_showcase, text="Secondary", bootstyle="secondary", command=lambda: cmb_bootstyle.set("secondary"))
    btn_bootstyle_secondary.pack(side="left", padx=4, pady=4)

    btn_bootstyle_success = ttk.Button(frm_showcase, text="Success", bootstyle="success", command=lambda: cmb_bootstyle.set("success"))
    btn_bootstyle_success.pack(side="left", padx=4, pady=4)

    btn_bootstyle_info = ttk.Button(frm_showcase, text="Info", bootstyle="info", command=lambda: cmb_bootstyle.set("info"))
    btn_bootstyle_info.pack(side="left", padx=4, pady=4)

    btn_bootstyle_warning = ttk.Button(frm_showcase, text="Warning", bootstyle="warning", command=lambda: cmb_bootstyle.set("warning"))
    btn_bootstyle_warning.pack(side="left", padx=4, pady=4)

    btn_bootstyle_danger = ttk.Button(frm_showcase, text="Danger", bootstyle="danger", command=lambda: cmb_bootstyle.set("danger"))
    btn_bootstyle_danger.pack(side="left", padx=4, pady=4)

    btn_bootstyle_light = ttk.Button(frm_showcase, text="Light", bootstyle="light", command=lambda: cmb_bootstyle.set("light"))
    btn_bootstyle_light.pack(side="left", padx=4, pady=4)

    btn_bootstyle_dark = ttk.Button(frm_showcase, text="Dark", bootstyle="dark", command=lambda: cmb_bootstyle.set("dark"))
    btn_bootstyle_dark.pack(side="left", padx=4, pady=4)


    frm_status_bar = ttk.Frame(window)
    frm_status_bar.pack(side="bottom", padx=4, pady=4)

    lbl_status = ttk.Label(frm_status_bar, textvariable=v_status)
    lbl_status.pack(side="left", padx=4, pady=4)

    cmb_bootstyle.set("primary")
    spn_sort_order.set(1)
    cmd_get_prefixes()
