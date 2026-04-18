        # ---------------- Bottom action buttons ----------------
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.add_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Add Asset",
            command=self.open_add_asset_window,
        )
        self.add_asset_btn.pack(side="right", padx=10)

        self.edit_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Edit Asset",
            state="disabled",
            command=self.open_edit_asset_window,
        )
        self.edit_asset_btn.pack(side="right", padx=(10, 0))

        self.delete_asset_btn = ctk.CTkButton(
            bottom_frame,
            text="Delete Asset",
            state="disabled",
            fg_color="#b91c1c",  # red-ish tone
            hover_color="#ef4444",
            command=self.delete_selected_asset,
        )
        self.delete_asset_btn.pack(side="right", padx=(10, 0))

        self.maint_btn = ctk.CTkButton(
            bottom_frame,
            text="Add Maintenance Entry",
            state="disabled",
            command=self.open_maintenance_window,
        )
        self.maint_btn.pack(side="right")

        self.status_label = ctk.CTkLabel(bottom_frame, text="")
        self.status_label.pack(side="left", padx=10)
