    # ============================================================
    # Add asset dialog
    # ============================================================

    def open_add_asset_window(self):
        """
        Open a dialog for creating a brand new asset.
        Only Asset ID is required; everything else is optional.
        """
        win = ctk.CTkToplevel(self)
        win.title("Add Asset")
        win.geometry("500x550")
        win.grab_set()

        frame = ctk.CTkFrame(win)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(1, weight=1)

        # Form state variables
        self.asset_id_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.brand_var = ctk.StringVar()
        self.model_var = ctk.StringVar()
        self.serial_var = ctk.StringVar()
        self.purchase_date_var = ctk.StringVar()
        self.cost_var = ctk.StringVar()
        self.site_var = ctk.StringVar()
        self.location_var = ctk.StringVar()
        self.dept_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.image_path_var = ctk.StringVar()
        self.available_var = ctk.BooleanVar(value=True)

        def add_row(row, label_text, var):
            lbl = ctk.CTkLabel(frame, text=label_text)
            lbl.grid(row=row, column=0, sticky="w", pady=4)
            ent = ctk.CTkEntry(frame, textvariable=var)
            ent.grid(row=row, column=1, sticky="ew", pady=4)

        add_row(0, "Asset ID *", self.asset_id_var)
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

        def browse_image():
            """
            Let the user select a local image file and store the path.
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
            command=browse_image,
        )
        browse_btn.grid(row=0, column=1)

        # Row 12: Available checkbox
        chk = ctk.CTkCheckBox(frame, text="Available", variable=self.available_var)
        chk.grid(row=12, column=0, columnspan=2, sticky="w", pady=6)

        # Buttons at bottom of dialog
        btn_frame = ctk.CTkFrame(win)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        save_btn = ctk.CTkButton(btn_frame, text="Save", command=lambda: self.save_asset(win))
        save_btn.pack(side="right", padx=(5, 0))

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=win.destroy)
        cancel_btn.pack(side="right")
