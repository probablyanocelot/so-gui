    # ============================================================
    # Maintenance dialog
    # ============================================================

    def open_maintenance_window(self):
        """
        Open a dialog to add a maintenance note for the selected asset.
        The note is stored via add_maintenance_entry in the service layer.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset first.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Add Maintenance Entry - {self.selected_asset_id}")
        win.geometry("500x350")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        info_lbl = ctk.CTkLabel(
            frame,
            text=f"Asset ID: {self.selected_asset_id}\nEnter maintenance notes below:",
            justify="left",
        )
        info_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.maint_text = ctk.CTkTextbox(frame, height=180)
        self.maint_text.grid(row=1, column=0, sticky="nsew")

        status_lbl = ctk.CTkLabel(frame, text="")
        status_lbl.grid(row=2, column=0, sticky="w", pady=(5, 0))

        def save_maintenance():
            """
            Save the maintenance note to the database and close the dialog.
            """
            note = self.maint_text.get("1.0", "end").strip()
            if not note:
                status_lbl.configure(text="Maintenance note cannot be empty.", text_color="red")
                return

            try:
                add_maintenance_entry(
                    asset_id=self.selected_asset_id,
                    emp_id=self.acting_emp_id,
                    note=note,
                )
            except Exception as e:
                status_lbl.configure(text=str(e), text_color="red")
                return

            status_lbl.configure(text="Maintenance entry saved.", text_color="green")
            win.after(600, win.destroy)

        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_frame, text="Save", command=save_maintenance)
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")
