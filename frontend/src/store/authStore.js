import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      username: null,
      onboarded: false,
      justOnboarded: false,
      theme: 'light',
      // School module fields
      role: 'studysmart_user',
      schoolId: null,
      schoolName: null,
      fullName: null,

      setAuth: (token, username, onboarded) => {
        set({ token, username, onboarded, role: 'studysmart_user', schoolId: null, schoolName: null })
        if (typeof window !== 'undefined') {
          document.documentElement.classList.toggle('dark', get().theme === 'dark')
        }
      },
      setSchoolAuth: ({ access_token, username, role, school_id, school_name, full_name }) => {
        set({ token: access_token, username, role, schoolId: school_id, schoolName: school_name, fullName: full_name, onboarded: true })
      },
      setOnboarded: () => set({ onboarded: true, justOnboarded: true }),
      clearJustOnboarded: () => set({ justOnboarded: false }),
      setTheme: (theme) => {
        set({ theme })
        document.documentElement.classList.toggle('dark', theme === 'dark')
      },
      logout: () => {
        set({ token: null, username: null, onboarded: false, role: 'studysmart_user', schoolId: null, schoolName: null, fullName: null })
        document.documentElement.classList.remove('dark')
      },
      isAuthenticated: () => !!get().token,
      isSchoolUser: () => ['school_admin', 'school_teacher', 'school_student'].includes(get().role),
    }),
    {
      name: 'studysmart-auth',
      partialize: (s) => ({
        token: s.token, username: s.username, onboarded: s.onboarded,
        theme: s.theme, role: s.role, schoolId: s.schoolId,
        schoolName: s.schoolName, fullName: s.fullName
      })
    }
  )
)
