import React from 'react'
import { useLocation } from 'react-router-dom'
import { Menu, Bell } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { getStats } from '../../api/user'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/study': 'Study Tools',
  '/flashcards': 'Flashcards',
  '/notes': 'My Notes',
  '/planner': 'Study Planner',
  '/analytics': 'Analytics',
  '/achievements': 'Achievements',
  '/leaderboard': 'Leaderboard',
}

export default function TopBar({ onMenuClick }) {
  const { pathname } = useLocation()
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: getStats, refetchInterval: 60000 })

  return (
    <header className="h-14 flex items-center gap-3 px-4 border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
      <button onClick={onMenuClick} className="btn-ghost p-2 lg:hidden">
        <Menu size={20} />
      </button>
      <h1 className="font-semibold text-slate-900 dark:text-slate-100 flex-1">
        {PAGE_TITLES[pathname] || 'StudySmart AI'}
      </h1>
      {stats && (
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-400 px-3 py-1.5 rounded-full text-xs font-semibold">
            <span>🔥</span>
            <span>{stats.streak_days}d streak</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-400 px-3 py-1.5 rounded-full text-xs font-semibold">
            <span>⭐</span>
            <span>Lv {stats.level}</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-400 px-3 py-1.5 rounded-full text-xs font-semibold">
            <span>✨</span>
            <span>{stats.total_xp} XP</span>
          </div>
        </div>
      )}
    </header>
  )
}
