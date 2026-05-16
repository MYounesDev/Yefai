"""Auth service — wraps Supabase Auth operations for user management."""

import logging
import re

from supabase import Client, create_client

from auth.models import OrgMembership, Role
from db.config import get_settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer for Supabase Auth + profile/org operations."""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.settings = get_settings()
        # Instantiate a fresh client for auth ops to not mutate global service role client
        self.auth_client = create_client(self.settings.supabase_url, self.settings.supabase_service_key)

    async def sign_up(self, email: str, password: str, full_name: str) -> dict:
        """Register a new user via Supabase Auth and create their profile.

        Returns:
            dict with user data and session token.
        """
        # Create user in Supabase Auth using auth_client to not mutate global client
        auth_response = self.auth_client.auth.sign_up(
            {"email": email, "password": password, "options": {"data": {"full_name": full_name}}}
        )

        if not auth_response.user:
            raise ValueError("Failed to create user")

        user_id = auth_response.user.id

        # Create profile row
        try:
            is_admin = self._is_admin_email(email)
            self.supabase.table("profiles").upsert(
                {
                    "id": user_id,
                    "full_name": full_name,
                    "is_platform_admin": is_admin,
                }
            ).execute()
        except Exception as e:
            logger.error("Failed to create profile for user %s: %s", user_id, e)

        return {
            "user": {
                "id": user_id,
                "email": email,
                "name": full_name,
            },
            "token": auth_response.session.access_token if auth_response.session else None,
            "refresh_token": auth_response.session.refresh_token if auth_response.session else None,
        }

    async def sign_in(self, email: str, password: str) -> dict:
        """Authenticate user via Supabase Auth.

        Returns:
            dict with user data, session tokens, and org memberships.
        """
        auth_response = self.auth_client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if not auth_response.user or not auth_response.session:
            raise ValueError("Invalid credentials")

        user_id = auth_response.user.id

        # Fetch profile
        profile = self._get_profile(user_id)

        # Fetch org memberships
        orgs = await self.get_user_organizations(user_id)

        return {
            "user": {
                "id": user_id,
                "email": email,
                "name": profile.get("full_name", ""),
                "avatar_url": profile.get("avatar_url"),
                "is_platform_admin": profile.get("is_platform_admin", False),
            },
            "token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "organizations": orgs,
        }

    async def sign_out(self, token: str) -> None:
        """Sign out user (invalidate Supabase session)."""
        try:
            self.auth_client.auth.sign_out(token)
        except Exception as e:
            logger.warning("Sign out failed (may already be expired): %s", e)

    async def get_current_user_data(self, user_id: str) -> dict:
        """Get full user profile + org memberships for /auth/me endpoint."""
        profile = self._get_profile(user_id)
        orgs = await self.get_user_organizations(user_id)

        return {
            "user": {
                "id": user_id,
                "email": profile.get("email", ""),
                "name": profile.get("full_name", ""),
                "avatar_url": profile.get("avatar_url"),
                "is_platform_admin": profile.get("is_platform_admin", False),
                "created_at": profile.get("created_at", ""),
            },
            "organizations": orgs,
        }

    async def get_user_organizations(self, user_id: str) -> list[dict]:
        """Get all org memberships for a user."""
        try:
            result = (
                self.supabase.table("org_members")
                .select("org_id, role, joined_at, status, organizations(id, name, slug, logo_url)")
                .eq("user_id", user_id)
                .eq("status", "active")
                .execute()
            )

            memberships = []
            for row in result.data or []:
                org = row.get("organizations", {}) or {}
                memberships.append(
                    {
                        "org_id": row["org_id"],
                        "org_name": org.get("name", ""),
                        "org_slug": org.get("slug", ""),
                        "org_logo_url": org.get("logo_url"),
                        "role": row["role"],
                        "joined_at": row.get("joined_at", ""),
                    }
                )
            return memberships

        except Exception as e:
            logger.error("Failed to fetch orgs for user %s: %s", user_id, e)
            return []

    async def forgot_password(self, email: str) -> None:
        """Trigger password reset email via Supabase Auth."""
        try:
            self.auth_client.auth.reset_password_email(email)
        except Exception as e:
            # Don't reveal if email exists
            logger.info("Password reset requested for %s: %s", email, e)

    async def reset_password(self, access_token: str, new_password: str) -> None:
        """Reset password using the token from the reset email."""
        self.auth_client.auth.update_user(
            {"password": new_password},
        )

    async def refresh_session(self, refresh_token: str) -> dict:
        """Refresh an expired access token."""
        result = self.auth_client.auth.refresh_session(refresh_token)

        if not result.session:
            raise ValueError("Failed to refresh session")

        return {
            "token": result.session.access_token,
            "refresh_token": result.session.refresh_token,
            "expires_at": result.session.expires_at,
        }

    async def accept_invitation(self, invite_token: str, user_id: str) -> dict:
        """Accept an org invitation — activate the org_members row.

        invite_token is the org_members.id for the invited row.
        """
        # Find the invitation
        result = (
            self.supabase.table("org_members")
            .select("*, organizations(id, name, slug)")
            .eq("id", invite_token)
            .eq("status", "invited")
            .maybe_single()
            .execute()
        )

        if not result.data:
            raise ValueError("Invalid or expired invitation")

        invitation = result.data

        # Activate membership
        self.supabase.table("org_members").update(
            {"user_id": user_id, "status": "active", "joined_at": "now()"}
        ).eq("id", invite_token).execute()

        org = invitation.get("organizations", {}) or {}
        return {
            "org_id": invitation["org_id"],
            "org_name": org.get("name", ""),
            "role": invitation["role"],
        }

    def _get_profile(self, user_id: str) -> dict:
        """Fetch profile from profiles table."""
        try:
            result = (
                self.supabase.table("profiles")
                .select("*")
                .eq("id", user_id)
                .maybe_single()
                .execute()
            )
            return result.data or {}
        except Exception:
            return {}

    def _is_admin_email(self, email: str) -> bool:
        """Check if the email is in the admin_emails config list."""
        if not self.settings.admin_emails:
            return False
        admin_list = [e.strip().lower() for e in self.settings.admin_emails.split(",")]
        return email.lower() in admin_list

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-safe slug from organization name."""
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")
