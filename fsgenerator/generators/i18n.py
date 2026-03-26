from __future__ import annotations

import json

from fsgenerator.parser import AppConfig, EntityDef


def _label(name: str) -> str:
    """Convert snake_case name to Title Case label: first_name -> First Name"""
    return name.replace("_", " ").title()


def generate(entities: list[EntityDef], config: AppConfig) -> list[tuple[str, str]]:
    data: dict = {
        "common": {
            "save": "Save",
            "cancel": "Cancel",
            "edit": "Edit",
            "delete": "Delete",
            "add_new": "Add New",
            "actions": "Actions",
            "id": "ID",
            "list": "List",
            "new": "New",
            "select": "-- Select --",
            "manage": "Manage",
            "error_unique": "A record with the same unique value already exists",
            "error_foreign": "Referenced record does not exist",
            "error_notnull": "A required field is missing",
            "error_check": "Validation failed",
            "error_integrity": "Data integrity error",
            "error_generic": "An error occurred",
            "no_records": "No records",
            "all": "All",
        },
        "auth": {
            "login": "Login",
            "logout": "Logout",
            "register": "Register",
            "email": "Email",
            "password": "Password",
            "password_confirm": "Confirm Password",
            "current_password": "Current Password",
            "new_password": "New Password",
            "new_password_confirm": "Confirm New Password",
            "change_password": "Change Password",
            "no_account": "Don't have an account?",
            "have_account": "Already have an account?",
            "invalid_credentials": "Invalid email or password",
            "account_inactive": "Your account is not yet activated. Please contact an administrator.",
            "password_mismatch": "Passwords do not match",
            "password_too_short": "Password must be at least 8 characters",
            "email_taken": "This email is already registered",
            "registration_pending": "Registration successful! An administrator will activate your account.",
            "wrong_current_password": "Current password is incorrect",
            "password_changed": "Password changed successfully",
            "user_management": "User Management",
            "active": "Active",
            "admin": "Admin",
            "created_at": "Created",
            "activate": "Activate",
            "deactivate": "Deactivate",
            "grant_admin": "Grant Admin",
            "revoke_admin": "Revoke Admin",
            "yes": "Yes",
            "no": "No",
        },
    }

    for entity in entities:
        section: dict[str, str] = {"_label": _label(entity.name)}
        for field in entity.fields:
            section[field.name] = _label(field.name)
        for rel in entity.relations:
            if rel.type in ("many_to_one", "one_to_one"):
                section[rel.field_name] = _label(rel.field_name)
        data[entity.name] = section

    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return [("i18n/en.json", content)]
