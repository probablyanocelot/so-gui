    # ============================================================
    # Delete asset
    # ============================================================

    def delete_selected_asset(self):
        """
        Delete the currently selected asset after a confirmation dialog.
        """
        if not self.selected_asset_id:
            self.status_label.configure(text="Please select an asset to delete.", text_color="red")
            return

        answer = messagebox.askyesno(
            "Delete Asset",
            f"Are you sure you want to delete asset '{self.selected_asset_id}'?\nThis cannot be undone.",
        )
        if not answer:
            return

        try:
            delete_asset(self.selected_asset_id, acting_emp_id=self.acting_emp_id)
        except Exception as e:
            self.status_label.configure(text=f"Error deleting asset: {e}", text_color="red")
            return

        self.status_label.configure(
            text=f"Deleted asset: {self.selected_asset_id}",
            text_color="white",
        )
        self.refresh_table()
