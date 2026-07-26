import React from 'react'
import { useLocation } from 'react-router-dom'
import { Menu, Bell, Flame, Star, Sparkles } from 'lucide-react'
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
    <header className="h-14 flex items-center gap-3 px-4 border-b border-slate-100 dark:border-navy-700 bg-white dark:bg-navy-800 shrink-0">
      <button onClick={onMenuClick} className="btn-ghost p-2 lg:hidden">
        <Menu size={20} />
      </button>
      <h1 className="font-semibold text-slate-900 dark:text-slate-100 flex-1">
        {PAGE_TITLES[pathname] || 'StudySmart AI'}
      </h1>
      {stats && (
        <div className="flex items-center gap-2">
          <div className="hidden sm:flex items-center gap-1.5 bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-400 px-3 py-1.5 rounded-full text-xs font-semibold">
            <Flame size={14} />
            <span>{stats.streak_days}d streak</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 bg-navy-50 dark:bg-navy-800 text-navy-700 dark:text-navy-300 px-3 py-1.5 rounded-full text-xs font-semibold">
            <Star size={14} />
            <span>Lv {stats.level}</span>
          </div>
          <div className="hidden sm:flex items-center gap-1.5 bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-400 px-3 py-1.5 rounded-full text-xs font-semibold">
            <Sparkles size={14} />
            <span>{stats.total_xp} XP</span>
          </div>
        </div>
      )}
    </header>
  )
}
