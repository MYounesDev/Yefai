-- Yefai Phase B9 — Row Level Security Policies

-- 1. Enable RLS on org-scoped tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;
ALTER TABLE anomalies ENABLE ROW LEVEL SECURITY;
ALTER TABLE spare_parts_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE part_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_parts ENABLE ROW LEVEL SECURITY;

-- 2. Create Policies
-- Note: Service key bypasses RLS, these are for defense in depth

-- Profile: users can see their own profile
CREATE POLICY profiles_own ON profiles FOR ALL
    USING (id = auth.uid());

-- Org members: users can see members of orgs they belong to
CREATE POLICY org_members_own_orgs ON org_members FOR SELECT
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Sets: org members can access their org's data
CREATE POLICY sets_org_access ON sets FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Images
CREATE POLICY images_org_access ON images FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Anomalies
CREATE POLICY anomalies_org_access ON anomalies FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Chat: users can only see their own sessions
CREATE POLICY chat_sessions_own ON chat_sessions FOR ALL
    USING (user_id = auth.uid() AND org_id IN (
        SELECT org_id FROM org_members WHERE user_id = auth.uid()
    ));

CREATE POLICY chat_messages_own ON chat_messages FOR ALL
    USING (session_id IN (
        SELECT id FROM chat_sessions WHERE user_id = auth.uid()
    ));

-- Support tickets
CREATE POLICY support_tickets_org ON support_tickets FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Files
CREATE POLICY files_org_access ON files FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));

-- Spare Parts
CREATE POLICY spare_parts_org_access ON spare_parts_catalog FOR ALL
    USING (org_id IN (SELECT org_id FROM org_members WHERE user_id = auth.uid()));
