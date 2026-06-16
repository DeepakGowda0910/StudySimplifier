import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BookOpen, CreditCard, BarChart2, Calendar, Trophy, Flame, Star, Clock, Zap, ArrowRight, Target } from 'lucide-react'
import { getStats, getProfile } from '../api/user'
import { useAuthStore } from '../store/authStore'

const QUICK_ACTIONS = [
  { label: 'Study Tools', desc: 'Generate notes, quizzes & more', icon: BookOpen, color: 'from-blue-500 to-blue-600', to: '/study' },
  { label: 'Flashcards', desc: 'Review due cards', icon: CreditCard, color: 'from-violet-500 to-violet-600', to: '/flashcards' },
  { label: 'Study Planner', desc: 'Plan your exam prep', icon: Calendar, color: 'from-emerald-500 to-emerald-600', to: '/planner' },
  { label: 'My Notes', desc: 'Write and organize notes', icon: BookOpen, color: 'from-amber-500 to-amber-600', to: '/notes' },
]

function StatCard({ label, value, icon: Icon, color, sub }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="stat-card">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shadow-sm`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
      {sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{sub}</p>}
    </motion.div>
  )
}

export default function Dashboard() {
  const { username } = useAuthStore()
  const navigate = useNavigate()
  const { data: stats, isLoading } = useQuery({ queryKey: ['stats'], queryFn: getStats, refetchInterval: 30000 })
  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile })

  const xpPct = stats ? Math.min(100, (stats.level_progress / 500) * 100) : 0
  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{greeting()}, {username}! 👋</h2>
          {profile?.course && (
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">
              {profile.category} · {profile.course}{profile.stream && profile.stream !== 'General' ? ` · ${profile.stream}` : ''}{profile.board && profile.board !== 'General' ? ` · ${profile.board}` : ''}
            </p>
          )}
        </div>
        <button onClick={() => navigate('/study')} className="btn-primary flex items-center gap-2 self-start sm:self-auto">
          <Zap size={16} /> Start Studying
        </button>
      </motion.div>

      {/* XP Bar */}
      {stats && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-sm">
                <Star size={16} className="text-white" />
              </div>
              <div>
                <p className="font-semibold text-slate-900 dark:text-white text-sm">Level {stats.level}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">{stats.total_xp} XP total</p>
              </div>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">{stats.level_progress} / 500 XP to Level {stats.level + 1}</p>
          </div>
          <div className="xp-bar">
            <motion.div className="xp-fill" initial={{ width: 0 }} animate={{ width: `${xpPct}%` }} transition={{ duration: 0.8, ease: 'easeOut' }} />
          </div>
        </motion.div>
      )}

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Study Streak" value={isLoading ? '…' : `${stats?.streak_days ?? 0}d`} icon={Flame} color="from-orange-400 to-red-500" sub={stats?.longest_streak ? `Best: ${stats.longest_streak}d` : null} />
        <StatCard label="Cards Due" value={isLoading ? '…' : stats?.flashcards_due ?? 0} icon={CreditCard} color="from-violet-400 to-purple-500" sub="Review today" />
        <StatCard label="Study Time" value={isLoading ? '…' : `${Math.floor((stats?.total_minutes ?? 0) / 60)}h`} icon={Clock} color="from-emerald-400 to-teal-500" sub={`${stats?.total_minutes ?? 0} min total`} />
        <StatCard label="Badges" value={isLoading ? '…' : stats?.badges_earned ?? 0} icon={Trophy} color="from-amber-400 to-yellow-500" sub="Earned" />
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="section-title mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {QUICK_ACTIONS.map(({ label, desc, icon: Icon, color, to }) => (
            <motion.button
              key={label}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => navigate(to)}
              className="card-hover p-5 text-left group"
            >
              <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center shadow-sm mb-3`}>
                <Icon size={22} className="text-white" />
              </div>
              <p className="font-semibold text-slate-900 dark:text-white text-sm">{label}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{desc}</p>
              <div className="flex items-center gap-1 text-blue-500 text-xs font-medium mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                Open <ArrowRight size={12} />
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Flashcards due banner */}
      {stats?.flashcards_due > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl p-5 text-white cursor-pointer"
          onClick={() => navigate('/flashcards')}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <CreditCard size={22} />
              </div>
              <div>
                <p className="font-bold">{stats.flashcards_due} flashcards due for review!</p>
                <p className="text-violet-200 text-sm">Keep your streak going — review now</p>
              </div>
            </div>
            <ArrowRight size={22} className="shrink-0 opacity-80" />
          </div>
        </motion.div>
      )}

      {/* Today's goals */}
      <div>
        <h3 className="section-title mb-4">Today's Goals</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {[
            { label: 'Study 30 minutes', done: (stats?.total_minutes ?? 0) > 0, icon: '⏱️' },
            { label: 'Review flashcards', done: (stats?.flashcards_due ?? 1) === 0, icon: '🃏' },
            { label: 'Generate study material', done: false, icon: '✨' },
          ].map(g => (
            <div key={g.label} className={`card p-4 flex items-center gap-3 ${g.done ? 'bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800' : ''}`}>
              <span className="text-2xl">{g.icon}</span>
              <p className={`text-sm font-medium ${g.done ? 'line-through text-green-600 dark:text-green-400' : 'text-slate-700 dark:text-slate-300'}`}>{g.label}</p>
              {g.done && <div className="ml-auto w-5 h-5 rounded-full bg-green-500 flex items-center justify-center"><Target size={12} className="text-white" /></div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
