'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarCollapsed: boolean;
  notificationCount: number;
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
  setNotificationCount: (n: number) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      notificationCount: 3,

      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
      setNotificationCount: (n) => set({ notificationCount: n }),
    }),
    { name: 'ui-storage' }
  )
);
