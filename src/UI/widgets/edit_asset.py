    # ============================================================
    # Edit asset dialog
    # ============================================================

    def open_edit_asset_window(self):
        """
        Open a dialog with the selected asset's info prefilled for editing.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset to edit.", text_color="red")
            return

        row = get_asset(self.selected_asset_id)
        if not row:
            self.status_label.configure(text="Selected asset not found.", text_color="red")
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Edit Asset - {self.selected_asset_id}")
        win.geometry("500x550")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        # Form variables, prefilled from DB
        self.asset_id_var = ctk.StringVar(value=row["ASSET_ID"])
        self.description_var = ctk.StringVar(value=row["DESCRIPTION"] or "")
        self.brand_var = ctk.StringVar(value=row["BRAND"] or "")
        self.model_var = ctk.StringVar(value=row["MODEL"] or "")
        self.serial_var = ctk.StringVar(value=row["SERIAL"] or "")
        self.purchase_date_var = ctk.StringVar(value=row["PURCHASE_DATE"] or "")
        self.cost_var = ctk.StringVar(
            value=str(row["COST"]) if row["COST"] is not None else ""
        )
        self.site_var = ctk.StringVar(value=row["SITE_NAME"] or "")
        self.location_var = ctk.StringVar(value=row["LOCATION_NAME"] or "")
        self.dept_var = ctk.StringVar(value=row["DEPT_NAME"] or "")
        self.category_var = ctk.StringVar(value=row["CATEGORY_NAME"] or "")
        self.image_path_var = ctk.StringVar(value=row["IMAGE_PATH"] or "")
        self.available_var = ctk.BooleanVar(value=bool(row["AVAILABLE"]))

        def add_row(row_index, label_text, var, readonly=False):
            lbl = ctk.CTkLabel(frame, text=label_text)
            lbl.grid(row=row_index, column=0, sticky="w", pady=4)
            ent = ctk.CTkEntry(frame, textvariable=var)
            if readonly:
                ent.configure(state="disabled")
            ent.grid(row=row_index, column=1, sticky="ew", pady=4)

        # Asset ID stays read-only
        add_row(0, "Asset ID", self.asset_id_var, readonly=True)
        add_row(1, "Description", self.description_var)
        add_row(2, "Brand", self.brand_var)
        add_row(3, "Model", self.model_var)
        add_row(4, "Serial", self.serial_var)
        add_row(5, "Purchase Date", self.purchase_date_var)
        add_row(6, "Cost", self.cost_var)
        add_row(7, "Site", self.site_var)
        add_row(8, "Location", self.location_var)
        add_row(9, "Department", self.dept_var)
        add_row(10, "Category", self.category_var)

        # Row 11: Image path + Browse button
        lbl_img = ctk.CTkLabel(frame, text="Image path / URL")
        lbl_img.grid(row=11, column=0, sticky="w", pady=4)

        img_row_frame = ctk.CTkFrame(frame)
        img_row_frame.grid(row=11, column=1, sticky="ew", pady=4)
        img_row_frame.grid_columnconfigure(0, weight=1)

        img_entry = ctk.CTkEntry(img_row_frame, textvariable=self.image_path_var)
        img_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        def browse_image_edit():
            """
            Let the user select a new image file for the asset.
            """
            file_path = filedialog.askopenfilename(
                title="Select image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*"),
                ],
            )
            if file_path:
                self.image_path_var.set(file_path)

        browse_btn = ctk.CTkButton(
            img_row_frame,
            text="Browse...",
            width=80,
            command=browse_image_edit,
        )
        browse_btn.grid(row=0, column=1)

        # Row 12: Available checkbox
        chk = ctk.CTkCheckBox(frame, text="Available", variable=self.available_var)
        chk.grid(row=12, column=0, columnspan=2, sticky="w", pady=6)

        # Buttons at bottom of dialog
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Changes",
            command=lambda: self.save_edited_asset(win, row["ASSET_ID"]),
        )
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")

    def save_edited_asset(self, window, asset_id):
        """
        Read the edit-asset form, validate, and update the asset record.
        """
        description = self.description_var.get().strip() or None
        brand = self.brand_var.get().strip() or None
        model = self.model_var.get().strip() or None
        serial = self.serial_var.get().strip() or None
        purchase_date = self.purchase_date_var.get().strip() or None
        site = self.site_var.get().strip() or None
        location = self.location_var.get().strip() or None
        dept = self.dept_var.get().strip() or None
        category = self.category_var.get().strip() or None
        image_path = self.image_path_var.get().strip() or None
        available = self.available_var.get()

        cost_value = None
        cost_str = self.cost_var.get().strip()
        if cost_str:
            try:
                cost_value = float(cost_str)
            except ValueError:
                print("Cost must be a number.")
                return

        try:
            update_asset(
                asset_id=asset_id,
                description=description,
                brand=brand,
                model=model,
                serial=serial,
                purchase_date=purchase_date,
                cost=cost_value,
                site_name=site,
                location_name=location,
                dept_name=dept,
                category_name=category,
                image_path=image_path,
                available=available,
                acting_emp_id=self.acting_emp_id,
            )
        except Exception as e:
            print("Error updating asset:", e)
            return

        window.destroy()
        self.refresh_table()