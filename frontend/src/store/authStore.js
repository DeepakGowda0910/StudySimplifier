import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      username: null,
      onboarded: false,
      theme: 'light',

      setAuth: (token, username, onboarded) => {
        set({ token, username, onboarded })
        if (typeof window !== 'undefined') {
          document.documentElement.classList.toggle('dark', get().theme === 'dark')
        }
      },
      setOnboarded: () => set({ onboarded: true }),
      setTheme: (theme) => {
        set({ theme })
        document.documentElement.classList.toggle('dark', theme === 'dark')
      },
      logout: () => {
        set({ token: null, username: null, onboarded: false })
        document.documentElement.classList.remove('dark')
      },
      isAuthenticated: () => !!get().token,
    }),
    { name: 'studysmart-auth', partialize: (s) => ({ token: s.token, username: s.username, onboarded: s.onboarded, theme: s.theme }) }
  )
)
