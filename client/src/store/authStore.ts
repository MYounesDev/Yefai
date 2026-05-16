'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserWithOrgs } from '@/types';
import { login as apiLogin, getCurrentUser } from '@/services/api';
import { useOrgStore } from './orgStore';

interface AuthState {
  user: UserWithOrgs | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loadUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const result = await apiLogin(email, password);
          const { user, token } = result as { user: UserWithOrgs; token: string };
          set({ user, token, isAuthenticated: true, isLoading: false });

          // Set first org as active
          if (user.organizations.length > 0) {
            const { setOrganizations, switchOrg } = useOrgStore.getState();
            setOrganizations(user.organizations);
            switchOrg(user.organizations[0].org_id);
          }
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
        useOrgStore.getState().setOrganizations([]);
      },

      loadUser: async () => {
        const { token } = get();
        if (!token) return;
        set({ isLoading: true });
        try {
          const user = await getCurrentUser() as UserWithOrgs;
          set({ user, isAuthenticated: true, isLoading: false });
          if (user.organizations.length > 0) {
            const { setOrganizations, activeOrgId } = useOrgStore.getState();
            setOrganizations(user.organizations);
            if (!activeOrgId) {
              useOrgStore.getState().switchOrg(user.organizations[0].org_id);
            }
          }
        } catch {
          set({ token: null, isAuthenticated: false, isLoading: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
