import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../../store/authStore'
import {
  LayoutDashboard, BookOpen, CreditCard, Trophy, BarChart2,
  FileText, Calendar, Users, LogOut, X, GraduationCap, Moon, Sun,
  Brain, Network, Settings as SettingsIcon
} from 'lucide-react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/study', label: 'Study Tools', icon: BookOpen },
  { to: '/flashcards', label: 'Flashcards', icon: CreditCard },
  { to: '/notes', label: 'Notes', icon: FileText },
  { to: '/planner', label: 'Planner', icon: Calendar },
  { to: '/agent', label: 'Study Agent', icon: Brain, badge: 'AI' },
  { to: '/graph', label: 'Knowledge Graph', icon: Network },
  { to: '/analytics', label: 'Analytics', icon: BarChart2 },
  { to: '/achievements', label: 'Achievements', icon: Trophy },
  { to: '/leaderboard', label: 'Leaderboard', icon: Users },
  { to: '/settings', label: 'Settings', icon: SettingsIcon },
]

export default function Sidebar({ open, onClose }) {
  const { username, logout, theme, setTheme } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const content = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-100 dark:border-navy-700">
        <div className="w-9 h-9 rounded-xl bg-navy-600 flex items-center justify-center shadow-lg">
          <GraduationCap size={20} className="text-white" />
        </div>
        <div>
          <p className="font-bold text-slate-900 dark:text-white leading-none">StudySmart</p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">AI Learning Platform</p>
        </div>
        <button onClick={onClose} className="ml-auto lg:hidden btn-ghost p-1.5">
          <X size={18} />
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {NAV.map(({ to, label, icon: Icon, badge }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            onClick={onClose}
            className={({ isActive }) => isActive ? 'nav-item-active' : 'nav-item-inactive'}
          >
            <Icon size={18} />
            <span className="text-sm flex-1">{label}</span>
            {badge && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-400">{badge}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 border-t border-slate-100 dark:border-navy-700 space-y-1">
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className="nav-item-inactive w-full"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          <span className="text-sm">{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
        </button>
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-8 h-8 rounded-full bg-navy-600 flex items-center justify-center text-white text-sm font-bold">
            {username?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">{username}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">Student</p>
          </div>
          <button onClick={handleLogout} className="btn-ghost p-1.5 text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-56 flex-col bg-white dark:bg-navy-800 border-r border-slate-100 dark:border-navy-700 shrink-0">
        {content}
      </aside>

      {/* Mobile overlay */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={onClose}
            />
            <motion.aside
              initial={{ x: -256 }} animate={{ x: 0 }} exit={{ x: -256 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed left-0 top-0 bottom-0 w-56 bg-white dark:bg-navy-800 z-50 lg:hidden flex flex-col shadow-2xl"
            >
              {content}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  )
}
