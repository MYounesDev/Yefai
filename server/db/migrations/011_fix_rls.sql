-- Fix infinite recursion on org_members
DROP POLICY IF EXISTS org_members_own_orgs ON org_members;

-- Allow members to see their own records
CREATE POLICY org_members_own_orgs ON org_members FOR SELECT
    USING (user_id = auth.uid());
