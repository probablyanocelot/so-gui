def create_form_row(frame, row, label, variable, readonly=False, **kwargs):
    """
    Helper function to create a labeled form row with an entry widget.
    """
    label_widget = ctk.CTkLabel(frame, text=label)
    label_widget.grid(row=row, column=0, sticky="w", padx=5, pady=5)

    entry_widget = ctk.CTkEntry(frame, textvariable=variable, **kwargs)
    entry_widget.grid(row=row, column=1, sticky="ew", padx=5, pady=5)

    if readonly:
        entry_widget.configure(state="readonly")

    return label_widget, entry_widget