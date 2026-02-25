# utils/forms.py (crea este helper)
def style_form(form):
    base = "w-full rounded-2xl border border-black/10 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-black/20"
    for field in form.fields.values():
        css = field.widget.attrs.get("class", "")
        field.widget.attrs["class"] = (css + " " + base).strip()
