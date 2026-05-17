"""Permission system — maps roles to permissions, provides check functions."""

from enum import StrEnum

from fastapi import HTTPException, status

from auth.models import Role


class Permission(StrEnum):
    """Fine-grained permissions that are granted to roles."""

    # Dashboard
    VIEW_DASHBOARD = "view:dashboard"

    # Anomalies
    VIEW_ANOMALIES = "view:anomalies"
    MARK_ANOMALY_REVIEWED = "action:mark_anomaly_reviewed"

    # Predictions
    VIEW_PREDICTIONS = "view:predictions"
    RECALCULATE_PREDICTION = "action:recalculate_prediction"

    # Spare Parts & POs
    VIEW_SPARE_PARTS = "view:spare_parts"
    APPROVE_PO = "action:approve_po"
    MANAGE_SUPPLIERS = "action:manage_suppliers"

    # Chat
    VIEW_CHAT = "view:chat"

    # Notifications
    VIEW_NOTIFICATIONS = "view:notifications"
    TRIGGER_NOTIFICATION = "action:trigger_notification"

    # Org Management
    MANAGE_MEMBERS = "manage:members"
    MANAGE_ORG_SETTINGS = "manage:org_settings"

    # Platform Admin
    ADMIN_MANAGE_ORGS = "admin:manage_orgs"
    ADMIN_MANAGE_USERS = "admin:manage_users"
    ADMIN_VIEW_TICKETS = "admin:view_tickets"
    ADMIN_PLATFORM_SETTINGS = "admin:platform_settings"


# All org-level view permissions (used by Manager and Viewer)
_ALL_ORG_VIEW = {
    Permission.VIEW_DASHBOARD,
    Permission.VIEW_ANOMALIES,
    Permission.VIEW_PREDICTIONS,
    Permission.VIEW_SPARE_PARTS,
    Permission.VIEW_CHAT,
    Permission.VIEW_NOTIFICATIONS,
}

# All org-level action permissions (used by Manager)
_ALL_ORG_ACTIONS = {
    Permission.MARK_ANOMALY_REVIEWED,
    Permission.RECALCULATE_PREDICTION,
    Permission.APPROVE_PO,
    Permission.MANAGE_SUPPLIERS,
    Permission.TRIGGER_NOTIFICATION,
    Permission.MANAGE_MEMBERS,
    Permission.MANAGE_ORG_SETTINGS,
}

ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {
        Permission.ADMIN_MANAGE_ORGS,
        Permission.ADMIN_MANAGE_USERS,
        Permission.ADMIN_VIEW_TICKETS,
        Permission.ADMIN_PLATFORM_SETTINGS,
    },
    Role.MANAGER: _ALL_ORG_VIEW | _ALL_ORG_ACTIONS,
    Role.OPERATOR: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANOMALIES,
        Permission.VIEW_PREDICTIONS,
        Permission.VIEW_CHAT,
        Permission.VIEW_NOTIFICATIONS,
    },
    Role.TECHNICIAN: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_ANOMALIES,
        Permission.MARK_ANOMALY_REVIEWED,
        Permission.VIEW_PREDICTIONS,
        Permission.RECALCULATE_PREDICTION,
        Permission.VIEW_SPARE_PARTS,
        Permission.VIEW_CHAT,
        Permission.VIEW_NOTIFICATIONS,
    },
    Role.PROCUREMENT: {
        Permission.VIEW_SPARE_PARTS,
        Permission.APPROVE_PO,
        Permission.MANAGE_SUPPLIERS,
        Permission.VIEW_NOTIFICATIONS,
    },
    Role.VIEWER: _ALL_ORG_VIEW,
}


def has_permission(role: Role, permission: Permission) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())


def check_permission(role: Role, permission: Permission) -> None:
    """Raise 403 if the role does not have the required permission."""
    if not has_permission(role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{role.value}' does not have permission '{permission.value}'",
        )
