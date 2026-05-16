"""Organization service — org CRUD, member management, admin operations."""

import logging
from datetime import datetime

from supabase import Client

from auth.models import Role
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class OrgService:
    """Business logic for organization and member management."""

    def __init__(self, supabase: Client):
        self.supabase = supabase

    # ── Organization CRUD ──────────────────────────────────────

    async def create_organization(
        self,
        name: str,
        slug: str,
        plan: str = "free",
        creator_user_id: str | None = None,
    ) -> dict:
        """Create a new organization and optionally add creator as manager."""
        result = (
            self.supabase.table("organizations")
            .insert({"name": name, "slug": slug, "plan": plan})
            .execute()
        )

        if not result.data:
            raise ValueError("Failed to create organization")

        org = result.data[0]

        # Add creator as manager if specified
        if creator_user_id:
            self.supabase.table("org_members").insert(
                {
                    "org_id": org["id"],
                    "user_id": creator_user_id,
                    "role": Role.MANAGER.value,
                    "status": "active",
                }
            ).execute()

        return org

    async def get_user_organizations(self, user_id: str) -> list[dict]:
        """Get all organizations a user belongs to."""
        result = (
            self.supabase.table("org_members")
            .select(
                "org_id, role, status, joined_at, "
                "organizations(id, name, slug, logo_url, plan, is_active, created_at)"
            )
            .eq("user_id", user_id)
            .eq("status", "active")
            .execute()
        )

        orgs = []
        for row in result.data or []:
            org_data = row.get("organizations", {}) or {}

            # Get member count for this org
            count_result = (
                self.supabase.table("org_members")
                .select("id", count="exact")
                .eq("org_id", row["org_id"])
                .eq("status", "active")
                .execute()
            )

            orgs.append(
                {
                    "id": org_data.get("id", row["org_id"]),
                    "name": org_data.get("name", ""),
                    "slug": org_data.get("slug", ""),
                    "logo_url": org_data.get("logo_url"),
                    "plan": org_data.get("plan", "free"),
                    "role": row["role"],
                    "member_count": count_result.count or 0,
                    "joined_at": row.get("joined_at", ""),
                }
            )
        return orgs

    async def get_organization_details(self, org_id: str) -> dict | None:
        """Get full org details."""
        result = (
            self.supabase.table("organizations")
            .select("*")
            .eq("id", org_id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        # Get member count
        count_result = (
            self.supabase.table("org_members")
            .select("id", count="exact")
            .eq("org_id", org_id)
            .eq("status", "active")
            .execute()
        )

        org = result.data
        org["member_count"] = count_result.count or 0
        return org

    async def update_organization(self, org_id: str, data: dict) -> dict:
        """Update organization fields."""
        update_data = {k: v for k, v in data.items() if v is not None}
        update_data["updated_at"] = datetime.utcnow().isoformat()

        result = (
            self.supabase.table("organizations")
            .update(update_data)
            .eq("id", org_id)
            .execute()
        )

        if not result.data:
            raise ValueError("Organization not found")

        return result.data[0]

    async def switch_organization(self, user_id: str, org_id: str) -> dict:
        """Validate user can switch to org and return org + role."""
        result = (
            self.supabase.table("org_members")
            .select("role, status, organizations(id, name, slug, logo_url, plan, settings)")
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise ValueError("You are not a member of this organization")

        if result.data.get("status") != "active":
            raise ValueError("Your membership is not active")

        org = result.data.get("organizations", {}) or {}
        return {
            "org": org,
            "role": result.data["role"],
        }

    # ── Member Management ──────────────────────────────────────

    async def get_org_members(self, org_id: str) -> list[dict]:
        """List all members of an organization."""
        result = (
            self.supabase.table("org_members")
            .select("id, org_id, user_id, role, status, invited_email, joined_at, updated_at")
            .eq("org_id", org_id)
            .order("joined_at", desc=False)
            .execute()
        )

        members = []
        for row in result.data or []:
            # Fetch profile for each member
            profile = {}
            if row.get("user_id"):
                profile_result = (
                    self.supabase.table("profiles")
                    .select("full_name, avatar_url")
                    .eq("id", row["user_id"])
                    .maybe_single()
                    .execute()
                )
                profile = profile_result.data or {}

            members.append(
                {
                    "user_id": row["user_id"],
                    "name": profile.get("full_name", row.get("invited_email", "Unknown")),
                    "email": row.get("invited_email", ""),
                    "avatar_url": profile.get("avatar_url"),
                    "role": row["role"],
                    "status": row["status"],
                    "joined_at": row.get("joined_at", ""),
                }
            )
        return members

    async def invite_member(self, org_id: str, email: str, role: str) -> dict:
        """Invite a user to an organization.

        Creates an org_members row with status='invited'.
        If user already exists (by email), links by user_id.
        """
        # Check if already a member
        existing = (
            self.supabase.table("org_members")
            .select("id, status")
            .eq("org_id", org_id)
            .eq("invited_email", email)
            .maybe_single()
            .execute()
        )

        if existing.data:
            if existing.data.get("status") == "active":
                raise ValueError(f"{email} is already a member of this organization")
            # Re-invite if disabled/invited
            self.supabase.table("org_members").update(
                {"status": "invited", "role": role}
            ).eq("id", existing.data["id"]).execute()
            return {"message": f"Re-invitation sent to {email}", "role": role}

        # Create invitation
        result = (
            self.supabase.table("org_members")
            .insert(
                {
                    "org_id": org_id,
                    "user_id": "00000000-0000-0000-0000-000000000000",  # placeholder until accepted
                    "role": role,
                    "status": "invited",
                    "invited_email": email,
                }
            )
            .execute()
        )

        if not result.data:
            raise ValueError("Failed to create invitation")

        return {
            "invite_id": result.data[0]["id"],
            "email": email,
            "role": role,
            "status": "invited",
        }

    async def update_member_role(self, org_id: str, user_id: str, new_role: str) -> dict:
        """Change a member's role within the organization."""
        # Prevent demoting the last manager
        if await self._is_sole_manager(org_id, user_id):
            raise ValueError("Cannot change role of the only manager. Add another manager first.")

        result = (
            self.supabase.table("org_members")
            .update({"role": new_role, "updated_at": datetime.utcnow().isoformat()})
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .execute()
        )

        if not result.data:
            raise ValueError("Member not found")

        return result.data[0]

    async def remove_member(self, org_id: str, user_id: str) -> dict:
        """Remove a member from the organization."""
        if await self._is_sole_manager(org_id, user_id):
            raise ValueError("Cannot remove the only manager. Transfer ownership first.")

        (
            self.supabase.table("org_members")
            .delete()
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .execute()
        )

        return {"message": "Member removed", "user_id": user_id}

    async def _is_sole_manager(self, org_id: str, user_id: str) -> bool:
        """Check if the user is the only manager in the organization."""
        # Check if user is a manager
        user_result = (
            self.supabase.table("org_members")
            .select("role")
            .eq("org_id", org_id)
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )

        if not user_result.data or user_result.data.get("role") != "manager":
            return False

        # Count managers
        manager_count = (
            self.supabase.table("org_members")
            .select("id", count="exact")
            .eq("org_id", org_id)
            .eq("role", "manager")
            .eq("status", "active")
            .execute()
        )

        return (manager_count.count or 0) <= 1

    # ── Admin Operations ───────────────────────────────────────

    async def admin_list_organizations(
        self, page: int = 1, limit: int = 20, search: str | None = None, plan: str | None = None
    ) -> dict:
        """List all organizations (platform admin view)."""
        query = self.supabase.table("organizations").select("*", count="exact")

        if search:
            query = query.ilike("name", f"%{search}%")
        if plan:
            query = query.eq("plan", plan)

        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        result = query.execute()

        # Attach member counts
        orgs = []
        for org in result.data or []:
            count_result = (
                self.supabase.table("org_members")
                .select("id", count="exact")
                .eq("org_id", org["id"])
                .eq("status", "active")
                .execute()
            )
            org["member_count"] = count_result.count or 0
            orgs.append(org)

        return {
            "organizations": orgs,
            "total": result.count or 0,
            "page": page,
            "limit": limit,
        }

    async def admin_create_organization(
        self, name: str, plan: str, manager_email: str
    ) -> dict:
        """Admin creates an org and invites initial manager."""
        slug = AuthService.generate_slug(name)
        org = await self.create_organization(name, slug, plan)

        # Invite the manager
        invitation = await self.invite_member(org["id"], manager_email, Role.MANAGER.value)

        return {
            "organization": org,
            "manager_invitation": invitation,
        }

    async def admin_get_organization(self, org_id: str) -> dict | None:
        """Admin view of an org (metadata + members, NOT factory data)."""
        org = await self.get_organization_details(org_id)
        if not org:
            return None

        members = await self.get_org_members(org_id)

        # Get usage stats
        anomaly_count = (
            self.supabase.table("anomalies")
            .select("id", count="exact")
            .eq("org_id", org_id)
            .execute()
        )
        po_count = (
            self.supabase.table("purchase_orders")
            .select("id", count="exact")
            .eq("org_id", org_id)
            .execute()
        )

        return {
            "organization": org,
            "members": members,
            "usage": {
                "anomalies_detected": anomaly_count.count or 0,
                "purchase_orders": po_count.count or 0,
            },
        }

    async def admin_list_users(
        self, page: int = 1, limit: int = 20, search: str | None = None
    ) -> dict:
        """List all platform users (admin view)."""
        query = self.supabase.table("profiles").select("*", count="exact")

        if search:
            query = query.ilike("full_name", f"%{search}%")

        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        result = query.execute()

        return {
            "users": result.data or [],
            "total": result.count or 0,
            "page": page,
            "limit": limit,
        }

    async def admin_get_platform_stats(self) -> dict:
        """Get platform-wide statistics."""
        orgs_count = (
            self.supabase.table("organizations")
            .select("id", count="exact")
            .execute()
        )
        active_orgs = (
            self.supabase.table("organizations")
            .select("id", count="exact")
            .eq("is_active", True)
            .execute()
        )
        users_count = (
            self.supabase.table("profiles")
            .select("id", count="exact")
            .execute()
        )
        tickets_open = (
            self.supabase.table("support_tickets")
            .select("id", count="exact")
            .eq("status", "open")
            .execute()
        )

        return {
            "total_orgs": orgs_count.count or 0,
            "active_orgs": active_orgs.count or 0,
            "total_users": users_count.count or 0,
            "tickets_open": tickets_open.count or 0,
        }
