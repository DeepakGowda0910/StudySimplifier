import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Trophy, Lock } from 'lucide-react'
import { getAchievements } from '../api/user'
import { getStats } from '../api/user'

const CATEGORY_COLORS = {
  milestones: 'from-amber-400 to-yellow-500',
  streaks: 'from-orange-400 to-red-500',
  levels: 'from-violet-400 to-purple-500',
  flashcards: 'from-blue-400 to-cyan-500',
  study: 'from-emerald-400 to-teal-500',
  content: 'from-pink-400 to-rose-500',
  focus: 'from-red-400 to-orange-500',
  notes: 'from-indigo-400 to-blue-500',
}

export default function Achievements() {
  const { data: badges = [], isLoading } = useQuery({ queryKey: ['achievements'], queryFn: getAchievements })
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: getStats })

  const earned = badges.filter(b => b.earned)
  const grouped = badges.reduce((acc, b) => {
    if (!acc[b.category]) acc[b.category] = []
    acc[b.category].push(b)
    return acc
  }, {})

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="card p-6 bg-gradient-to-r from-amber-400 to-yellow-500 text-white">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">
            <Trophy size={32} />
          </div>
          <div>
            <p className="text-2xl font-bold">{earned.length} / {badges.length} Badges Earned</p>
            <p className="text-yellow-100 text-sm mt-0.5">Level {stats?.level ?? 1} · {stats?.total_xp ?? 0} XP total</p>
          </div>
        </div>
        <div className="mt-4 h-2 bg-white/30 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-white rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${(earned.length / Math.max(badges.length, 1)) * 100}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
        <p className="text-yellow-100 text-xs mt-1">{Math.round((earned.length / Math.max(badges.length, 1)) * 100)}% complete</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(12)].map((_, i) => <div key={i} className="card h-36 shimmer" />)}
        </div>
      ) : (
        Object.entries(grouped).map(([cat, items]) => (
          <div key={cat}>
            <h3 className="section-title mb-3 capitalize">{cat}</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {items.map((b, i) => (
                <motion.div
                  key={b.id}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className={`card p-4 text-center relative overflow-hidden ${!b.earned ? 'opacity-50 grayscale' : ''}`}
                >
                  {b.earned && (
                    <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${CATEGORY_COLORS[b.category] || 'from-blue-400 to-violet-400'}`} />
                  )}
                  <div className={`w-14 h-14 rounded-2xl mx-auto mb-3 flex items-center justify-center text-3xl ${b.earned ? `bg-gradient-to-br ${CATEGORY_COLORS[b.category] || 'from-slate-400 to-slate-500'}` : 'bg-slate-100 dark:bg-slate-800'}`}>
                    {b.earned ? b.icon : <Lock size={20} className="text-slate-400" />}
                  </div>
                  <p className="font-semibold text-slate-900 dark:text-white text-sm">{b.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-tight">{b.desc}</p>
                  <p className="text-xs font-medium text-amber-500 mt-2">+{b.xp} XP</p>
                  {b.earned && b.earned_at && (
                    <p className="text-xs text-green-500 dark:text-green-400 mt-1">
                      {new Date(b.earned_at).toLocaleDateString()}
                    </p>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
