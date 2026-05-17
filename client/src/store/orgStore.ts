'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { OrgMembership, Role } from '@/types';

interface OrgState {
  activeOrgId: string | null;
  activeRole: Role | null;
  organizations: OrgMembership[];
  switchOrg: (orgId: string) => void;
  setOrganizations: (orgs: OrgMembership[]) => void;
}

export const useOrgStore = create<OrgState>()(
  persist(
    (set, get) => ({
      activeOrgId: null,
      activeRole: null,
      organizations: [],

      setOrganizations: (organizations) => {
        set({ organizations });
      },

      switchOrg: (orgId) => {
        const { organizations } = get();
        const membership = organizations.find((o) => o.org_id === orgId);
        if (membership) {
          set({ activeOrgId: orgId, activeRole: membership.role });
        } else if (organizations.length > 0) {
          set({ activeOrgId: organizations[0].org_id, activeRole: organizations[0].role });
        }
      },
    }),
    {
      name: 'org-storage',
      partialize: (state) => ({ activeOrgId: state.activeOrgId }),
    }
  )
);
