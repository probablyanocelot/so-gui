"""
soGUI — Main Application Entry Point

Description:
    This file is the starting point for the soGUI application.
    It makes sure the database is ready to use and then launches
    the main GUI window for the app.
"""
# Check for dependencies / 
# customtkinter is external library
try:
    import customtkinter
except ImportError:
    print("CustomTkinter is not installed. Please run:")
    print("pip install -r requirements.txt")
    exit(1)
from db import init_db
from UI.app import soGUIApp
from services import seed_default_admin

def main():
    """
    Initialize the database and start the main GUI loop.
    """
    # Make sure the database file and required tables exist
    init_db()
    seed_default_admin()

    # Create the main application window and start the event loop
    app = soGUIApp()
    app.mainloop()


if __name__ == "__main__":
    # Only run the app if this file is executed directly
    main()
