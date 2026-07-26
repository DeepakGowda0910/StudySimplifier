import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { CreditCard, Trophy, Flame, Star, Clock, Zap, ArrowRight, BarChart2 } from 'lucide-react'
import { getStats, getProfile } from '../api/user'
import { useAuthStore } from '../store/authStore'

function StatCard({ label, value, icon: Icon, color, sub }) {
  return (
    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="stat-card">
      <div className="flex items-center justify-between mb-3">
        <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
        <div className={`w-9 h-9 rounded-xl ${color} flex items-center justify-center shadow-sm`}>
          <Icon size={18} className="text-white" />
        </div>
      </div>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
      {sub && <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{sub}</p>}
    </motion.div>
  )
}

export default function Dashboard() {
  const { username, justOnboarded, clearJustOnboarded } = useAuthStore()
  const navigate = useNavigate()
  const { data: stats, isLoading } = useQuery({ queryKey: ['stats'], queryFn: getStats, refetchInterval: 30000 })
  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile })

  useEffect(() => {
    if (justOnboarded) {
      const t = setTimeout(() => clearJustOnboarded(), 8000)
      return () => clearTimeout(t)
    }
  }, [justOnboarded])

  const xpPct = stats ? Math.min(100, (stats.level_progress / 500) * 100) : 0
  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const hasStudied = (stats?.total_minutes ?? 0) > 0
  const flashcardsDue = stats?.flashcards_due ?? 0

  let nextStep = {
    title: 'Nice work — check your progress',
    desc: 'See how you\'re doing across subjects and badges.',
    cta: 'View Analytics',
    to: '/analytics',
    icon: BarChart2,
  }
  if (!hasStudied) {
    nextStep = {
      title: 'Start your first study session',
      desc: 'Pick a subject and chapter, and generate your first set of notes.',
      cta: 'Go to Study Tools',
      to: '/study',
      icon: Zap,
    }
  } else if (flashcardsDue > 0) {
    nextStep = {
      title: `You have ${flashcardsDue} card${flashcardsDue > 1 ? 's' : ''} to review`,
      desc: 'Spaced repetition works best when you review consistently.',
      cta: 'Review Flashcards',
      to: '/flashcards',
      icon: CreditCard,
    }
  }

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
            {justOnboarded ? `Welcome, ${username}!` : `${greeting()}, ${username}!`}
          </h2>
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
              <div className="w-8 h-8 rounded-lg bg-navy-600 flex items-center justify-center shadow-sm">
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
        <StatCard label="Study Streak" value={isLoading ? '…' : `${stats?.streak_days ?? 0}d`} icon={Flame} color="bg-orange-500" sub={stats?.longest_streak ? `Best: ${stats.longest_streak}d` : null} />
        <StatCard label="Cards Due" value={isLoading ? '…' : stats?.flashcards_due ?? 0} icon={CreditCard} color="bg-navy-600" sub="Review today" />
        <StatCard label="Study Time" value={isLoading ? '…' : `${Math.floor((stats?.total_minutes ?? 0) / 60)}h`} icon={Clock} color="bg-teal-600" sub={`${stats?.total_minutes ?? 0} min total`} />
        <StatCard label="Badges" value={isLoading ? '…' : stats?.badges_earned ?? 0} icon={Trophy} color="bg-amber-500" sub="Earned" />
      </div>

      {/* Next Step */}
      <motion.button
        initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        onClick={() => navigate(nextStep.to)}
        className="w-full text-left bg-navy-700 dark:bg-navy-800 rounded-2xl p-5 text-white flex items-center justify-between gap-4 hover:bg-navy-800 dark:hover:bg-navy-700 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center shrink-0">
            <nextStep.icon size={22} />
          </div>
          <div className="min-w-0">
            <p className="font-bold">{nextStep.title}</p>
            <p className="text-navy-200 text-sm truncate">{nextStep.desc}</p>
          </div>
        </div>
        <div className="flex items-center gap-1 text-sm font-medium shrink-0">
          {nextStep.cta} <ArrowRight size={16} />
        </div>
      </motion.button>
    </div>
  )
}
