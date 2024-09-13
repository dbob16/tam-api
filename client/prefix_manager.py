import os
import ttkbootstrap as ttk 
import webbrowser
from requests import get, post, delete
from configparser import ConfigParser

bootstyle_values = ("primary", "secondary", "success", "info", "warning", "danger", "light", "dark")
theme_values = ("cyborg", "solar", "superhero", "darkly", "vapor", "cosmo", "flatly", "journal", "litera", "lumen", "minty", "pulse", "sandstone", "united", "yeti", "morph", "simplex", "ciculean")

config = ConfigParser()
config.read('config.ini')

try:
    BASE_URL = config["server"]["base_url"]
except:
    BASE_URL = "http://localhost/"

try:
    api_key = config["server"]["api_key"]
except:
    api_key = None

def main():
    window = ttk.Window(title="TAM Prefix Manager", themename="cyborg")

    def cmd_get_prefixes():
        response = get(f"{BASE_URL}prefixes/", params={"api_key": api_key}).json()
        try:
            current_prefixes = [v["prefix"] for v in response]
            cmb_prefix.config(values=current_prefixes)
        except:
            cmb_prefix.set("No current prefixes")


    def cmd_add_prefix():
        response = post(f"{BASE_URL}prefix/", json={"prefix": cmb_prefix.get(), "bootstyle": cmb_bootstyle.get(), "sort_order": spn_sort_order.get()}, params={"api_key": api_key})
        r_s = response.json()
        try:
            if r_s["success"]:
                cmd_get_prefixes()
                cmb_prefix.set("")
        except:
            print(response)

    def cmd_rm_prefix():
        response = delete(f"{BASE_URL}delprefix/", params={"api_key": api_key, "prefix": cmb_prefix.get()}).json()
        try:
            if response["success"]:
                cmd_get_prefixes()
                cmb_prefix.set("")
        except:
            pass

    def cmd_set_theme(_=None):
        style = ttk.Style(cmb_theme.get())

    frm_prefixes = ttk.LabelFrame(window, text="Prefixes")
    frm_prefixes.pack(padx=4, pady=4, fill="x")

    lbl_prefix = ttk.Label(frm_prefixes, text="Prefix")
    lbl_prefix.grid(row=0, column=0)

    cmb_prefix = ttk.Combobox(frm_prefixes)
    cmb_prefix.grid(row=1, column=0, padx=4, pady=4)

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

    btn_remove = ttk.Button(frm_prefixes, text="Remove", bootstyle="danger")
    btn_remove.grid(row=1, column=4, padx=4, pady=4)

    frm_showcase = ttk.LabelFrame(window, text="Showcase")
    frm_showcase.pack(padx=4, pady=4, fill="x")

    lbl_theme = ttk.Label(frm_showcase, text="Theme: ")
    lbl_theme.grid(row=0, column=0, padx=4, pady=4)

    cmb_theme = ttk.Combobox(frm_showcase, state="readonly", values=theme_values)
    cmb_theme.grid(row=0, column=1, padx=4, pady=4)
    cmb_theme.bind("<<ComboboxSelected>>", cmd_set_theme)

    frm_btn_showcase = ttk.Frame(frm_showcase)
    frm_btn_showcase.grid(row=1, column=0, columnspan=2)

    for bootstyle in bootstyle_values:
        btn_style = ttk.Button(frm_btn_showcase, text=f"{bootstyle.capitalize()}", bootstyle=bootstyle)
        btn_style.pack(side="left", padx=4, pady=4)

    cmb_bootstyle.set("primary")
    spn_sort_order.set(1)
    cmd_get_prefixes()

    window.mainloop()

if __name__ == "__main__":
    main()