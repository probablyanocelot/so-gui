class ImagePreview(ctk.CTkFrame):

    # thumbnail loading / full-size image popup        # ---------------- Image preview area ----------------
    # Keep a reference to the CTkImage so it doesn't get garbage-collected
    self.preview_ctkimage = None

    preview_frame = ctk.CTkFrame(self)
    preview_frame.pack(fill="x", padx=10, pady=(0, 10))

    preview_label = ctk.CTkLabel(
        preview_frame,
        text="Image preview (click to open full size):",
        anchor="w",
    )
    preview_label.pack(anchor="w")

    self.preview_image_label = ctk.CTkLabel(
        preview_frame,
        text="No image",
        width=150,
        height=150,
        corner_radius=8,
    )
    self.preview_image_label.pack(anchor="w", pady=(4, 0))

    # Clicking the thumbnail opens a larger image window
    self.preview_image_label.bind("<Button-1>", self.open_full_image_window)


    # Update thumbnail preview when selection changes
    self.update_image_preview()

# ============================================================
# Image preview
# ============================================================

def update_image_preview(self):
    """
    Load a small thumbnail for the selected asset, if it has an IMAGE_PATH.

    This version:
    - clears the label's visible image,
    - loads the image (if present),
    - creates a CTkImage thumbnail,
    - and stores a reference on the label to prevent garbage collection.
    """

    # Clear the visible image/text (safe even if an old image exists)
    self.preview_image_label.configure(image=None, text="No image")

    # If nothing is selected, we're done
    if not getattr(self, "selected_asset_id", None):
        return

    row = get_asset(self.selected_asset_id)
    if not row:
        return

    img_path = row["IMAGE_PATH"]
    if not img_path:
        return

    try:
        pil_img = Image.open(img_path)
    except Exception:
        self.preview_image_label.configure(text="Could not load image")
        return

    # Create thumbnail (e.g., max 150x150)
    max_size = (150, 150)
    pil_img.thumbnail(max_size)

    # Create CTkImage thumbnail
    thumb = ctk.CTkImage(
        light_image=pil_img,
        dark_image=pil_img,
        size=pil_img.size,
    )

    # Attach the CTkImage to the label AND keep a reference on the label
    self.preview_image_label.configure(image=thumb, text="")
    self.preview_image_label.image = thumb  # set image to thumb




    def open_full_image_window(self, event=None):
        """
        Open a larger view of the selected asset's image in a new pop-up window.
        """
        if not self.selected_asset_id:
            return

        row = get_asset(self.selected_asset_id)
        if not row:
            return

        img_path = row["IMAGE_PATH"]
        if not img_path:
            return

        try:
            pil_img = Image.open(img_path)
        except Exception:
            return

        win = ctk.CTkToplevel(self)
        win.title(f"Image - {self.selected_asset_id}")
        win.geometry("650x650")
        win.grab_set()

        # Resize image to fit nicely in the window
        max_size = (600, 600)
        pil_img.thumbnail(max_size)

        full_image = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=pil_img.size,
        )

        img_label = ctk.CTkLabel(win, image=full_image, text="")
        img_label.image = full_image  # keep a reference on the label
        img_label.pack(padx=20, pady=20)
