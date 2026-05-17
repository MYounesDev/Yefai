'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  sidebarCollapsed: boolean;
  notificationCount: number;
  commandPaletteOpen: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
  setNotificationCount: (n: number) => void;
  setCommandPaletteOpen: (v: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      notificationCount: 3,
      commandPaletteOpen: false,

      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
      setNotificationCount: (n) => set({ notificationCount: n }),
      setCommandPaletteOpen: (v) => set({ commandPaletteOpen: v }),
    }),
    { name: 'ui-storage' }
  )
);
