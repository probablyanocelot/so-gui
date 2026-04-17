# soGUI (Slightly Optimized Graphical User Interface)

## Application Overview

soGUI is a fork of a Python-based desktop application designed to simplify asset tracking for small academic or administrative environments. The system allows authorized users to manage inventory items and inspect histories, inventory users, maintenance logs, and audit records through an organized, user-friendly interface.

soGUI follows a lightweight MVC structure, where the UI (View) is separated from data-handling logic (Model) via a dedicated service layer. This keeps the application organized, maintainable, and easy to extend.

This document provides a high-level overview of how the application is built, how to run it, and what to expect during future updates.

## Getting Started

### 1. Install Python

Download the latest Windows installer from:

```text
https://www.python.org/downloads/windows/
```

When installing, make sure to check **Add Python to PATH** before selecting **Install Now**.

### 2. Install Required Packages

Open a Windows terminal or command prompt, navigate to the `soGUI` project folder, and install dependencies:

```powershell
pip install -r requirements.txt
```

If you are using an IDE such as VS Code, open the `soGUI` folder first and run the above command inside the IDE terminal.

#### Example folder navigation

PowerShell:

```powershell
cd "$env:USERPROFILE\OneDrive\Desktop\soGUI"
cd "$env:USERPROFILE\Downloads\soGUI"
```

Command Prompt:

```cmd
dcd %USERPROFILE%\OneDrive\Desktop\soGUI
cd %USERPROFILE%\Downloads\soGUI
```

### 3. Run the Application

From the terminal or IDE built-in terminal, run:

```powershell
python main.py
```

Alternatively, open `main.py` in Python IDLE and run it as a module.

### 4. Default Login Credentials

A built-in admin account is available for first-time access:

- **Username:** `admin`
- **Password:** `pswd`

### 5. Optional: Reset soGUI to Default State

To return soGUI to a clean first-launch condition:

- In the project root folder (`soGUI`), remove the `__pycache__` directory and any generated database files.
- In `soGUI/UI`, remove the `__pycache__` directory.

This clears cached files and the working database while preserving the default admin login.

## Dependencies

### Core Requirements

soGUI requires the following components:

- Python 3.10+ (developed and tested on Python 3.11.9)
- SQLite3
- Tkinter 8.6.x (included with standard Python installs)

> Note: Pillow 12.0.0 may not be compatible with Python 3.9 or earlier.

### External Libraries

Install these packages using:

```powershell
pip install -r requirements.txt
```

Primary external libraries include:

- `CustomTkinter 5.2.2`
- `Pillow 12.0.0`

## Testing

soGUI was tested with a scenario-based approach to verify module behavior and application stability.

### Functional testing

- **Login and Authentication** — Valid credentials, invalid credentials, default admin login, and password reset routing.
- **Inventory Management** — Create, edit, checkout, return, and delete assets while preserving consistent CRUD behavior.
- **Customer Management** — Add, update, and remove customer profiles, ensuring proper linkage to checkout and audit records.
- **Checkout and Return Workflow** — Confirm timestamp, due date, active checkout view, and return actions refresh correctly.
- **Maintenance Logs** — Verify logs can be created, viewed, and linked to specific assets.
- **Audit Tracking** — Confirm actions such as login attempts, inventory updates, and checkouts generate audit entries.

### Interface and usability testing

- Screen navigation remains responsive and lag-free.
- Layout behavior is consistent across main application sections.
- Appearance is consistent on Windows, with partial prototype compatibility on macOS.

### Error and edge case testing

This prototype was tested for overall functionality, but error handling is not exhaustive. Future versions should replace free-form text entry with controlled fields, dropdowns, and preset options to reduce input errors.

## Development & Testing Tools

The application was developed and tested using:

- **Visual Studio Code** 1.106.3
- **Python** 3.11.9
- **Windows 11** (version 25H2)
- **macOS 15 (Tahoe)**
- **Pillow** 12.0.0
- **CustomTkinter** 5.2.2
- **Tkinter** 8.6.15
- **SQLite3**

Using similar versions is recommended for the most consistent results.

## Future Development

soGUI has a solid foundation, and the following improvements would enhance usability and reliability:

### 1. Minimize user input to reduce errors

- Replace free-form text fields with structured controls.
- Use dropdown menus, predefined value lists, and guided input fields.
- Reduce typos, invalid IDs, and inconsistent records.

### 2. Increase controlled input environments

- Add validation constraints and auto-population of related fields.
- Example: selecting a customer filters available items; selecting an asset auto-fills categories or maintenance intervals.
- This improves consistency across checkouts and updates.

### 3. Add inventory support for replenishable items

- Support quantity-based inventory tracking.
- Add automatic low-stock alerts.
- Implement simple restock workflows.
- This expands the app beyond durable assets to supplies and high-turnover items.

### 4. Add barcode / QR code scanning integration

- Enable asset lookup, checkout, and returns with barcode or QR scanning.
- Improve speed and accuracy of asset identification.
- Reduce reliance on manual searching.
- Support USB scanners or mobile devices as scanning inputs.
