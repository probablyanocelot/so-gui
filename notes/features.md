# Features

## User Types

- **Standard User**: Can access most features but has limited permissions for certain actions.
- **Admin**: Has full access to all features and settings.
- **Others**: added in future, as needed; denoted as "Future User Roles".
  - **Different Levels of Access**: Some features may have tiered access levels

## Access By User Type

- **Standard User**:
  - Checkout/Return
  - Reservation Functions
  - Can view and interact with content but cannot modify it

- **Admin**:
  - Full access to all features
  - Audit Logs
  - Inventory Log
  - Reports
  - Tracking Functions
  - Etc

- **IT Admin**:
  - Maintenance Reports
  - Server Backups
  - Etc

## Functionality

### Asset Management

#### Asset Data Shape

    - Description
    - Cost
    - Serial Number (for tracking)
    - Location
    - Department (for sorting, *visibility optional*)
    - Availability Status (will be displayed)
    - **ALL SHOWN IN CHECKOUT PAGE**

#### Management

items can be tracked
email & history of checkouts (who&what)
Audit Logs: checkout, loc, email, damages, pics, etc
policies will b avail for creation

### Checkout Features / Functions

- Asset List with Images
- Checkbox selection
- Search Bar
- Form w/ Date,Email,Location (for tracking + records)
- Allows Easy Navigation

#### Checkout Data Shape

- Asset ID
- Email
- First Name
- Last Name
- Phone (optional)
- Return Due Date (sounds optional)
- Notes (optional)
- STORE CHECKOUT TIMESTAMP (rendered in "Active Checkouts / Check In" tab)
- While checked out, can reserve asset for some_user ( reservee's name, desired date )

#### Checkout Flow

- assets in checkout tab
- checkout -> move asset to "Active Checkouts / Check In" tab

### Reports Page

- Inventory Report : all inv if admin, all for user's dept otherwise
- Audit Log
  1. EVERY ACTION LOGGED
  2. filter functionality: action, asset ID, employee ID, start date, end date (apply/clear buttons)
- Maintenance Log
  1. uses maintenance record
  2. filter functionality: asset ID, start date, end date (apply/show all buttons)
- All have export to .csv functionality

### Change Password Button

- Security Emphasized - **IMPLEMENT GOOD VALIDATION PRACTICES (& MANDATORY PASSWORD ROTATION TIMES ?)**

## Mentioned ("things to look forward to" slide)

- In-house benefits (security, accountability, maintenance, etc)
- Sovereignty
- Customization / Modularity
- Storage: Modularity (in-house vs cloud...) **REQ**
- Ease of Admin (policy mgmt)
- Easily Accessible for Auth Users

## Notes

- Slides have uml sys diagram

## My Suggestions

1. Security
   - Login: Replace "not in system" with "invalid credentials"
   - Login: Sign-Up option listed below login
