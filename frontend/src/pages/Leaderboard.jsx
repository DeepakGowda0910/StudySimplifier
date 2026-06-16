import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Trophy, Crown, Flame, Clock } from 'lucide-react'
import { getLeaderboard } from '../api/user'
import { useAuthStore } from '../store/authStore'

const RANK_STYLES = {
  1: 'bg-amber-50 dark:bg-amber-950 border-amber-300 dark:border-amber-700',
  2: 'bg-slate-50 dark:bg-slate-800 border-slate-300 dark:border-slate-600',
  3: 'bg-orange-50 dark:bg-orange-950 border-orange-300 dark:border-orange-700',
}
const RANK_ICONS = { 1: '🥇', 2: '🥈', 3: '🥉' }

export default function Leaderboard() {
  const { username } = useAuthStore()
  const { data: lb = [], isLoading } = useQuery({ queryKey: ['leaderboard'], queryFn: getLeaderboard, refetchInterval: 60000 })

  const top3 = lb.slice(0, 3)
  const rest = lb.slice(3)
  const myEntry = lb.find(e => e.username === username)

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="card p-6 text-center bg-gradient-to-br from-blue-600 to-violet-700 text-white">
        <Crown size={36} className="mx-auto mb-2" />
        <h2 className="text-2xl font-bold">Leaderboard</h2>
        <p className="text-blue-200 text-sm mt-1">Top learners ranked by XP</p>
        {myEntry && (
          <div className="mt-4 inline-flex items-center gap-2 bg-white/20 px-4 py-2 rounded-full text-sm font-medium">
            Your rank: #{myEntry.rank} · {myEntry.total_xp} XP
          </div>
        )}
      </div>

      {/* Top 3 podium */}
      {top3.length > 0 && (
        <div className="flex items-end justify-center gap-4 pb-4">
          {/* 2nd */}
          {top3[1] && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-slate-300 to-slate-400 flex items-center justify-center text-2xl font-black text-white shadow-lg mb-2">
                {top3[1].username[0].toUpperCase()}
              </div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">{top3[1].username}</p>
              <p className="text-xs text-slate-500">{top3[1].total_xp} XP</p>
              <div className="w-20 h-16 bg-slate-200 dark:bg-slate-700 rounded-t-xl mt-2 flex items-center justify-center text-2xl">🥈</div>
            </motion.div>
          )}
          {/* 1st */}
          {top3[0] && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col items-center">
              <Crown size={20} className="text-amber-500 mb-1" />
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center text-3xl font-black text-white shadow-xl mb-2">
                {top3[0].username[0].toUpperCase()}
              </div>
              <p className="font-bold text-slate-900 dark:text-white">{top3[0].username}</p>
              <p className="text-xs text-slate-500">{top3[0].total_xp} XP</p>
              <div className="w-24 h-24 bg-amber-200 dark:bg-amber-900 rounded-t-xl mt-2 flex items-center justify-center text-3xl">🥇</div>
            </motion.div>
          )}
          {/* 3rd */}
          {top3[2] && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-orange-300 to-orange-400 flex items-center justify-center text-2xl font-black text-white shadow-lg mb-2">
                {top3[2].username[0].toUpperCase()}
              </div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">{top3[2].username}</p>
              <p className="text-xs text-slate-500">{top3[2].total_xp} XP</p>
              <div className="w-20 h-10 bg-orange-200 dark:bg-orange-900 rounded-t-xl mt-2 flex items-center justify-center text-2xl">🥉</div>
            </motion.div>
          )}
        </div>
      )}

      {/* Full list */}
      <div className="card overflow-hidden">
        <div className="p-4 border-b border-slate-100 dark:border-slate-800 grid grid-cols-12 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          <span className="col-span-1">Rank</span>
          <span className="col-span-4">Student</span>
          <span className="col-span-2 text-right">XP</span>
          <span className="col-span-2 text-right">Level</span>
          <span className="col-span-2 text-right">Streak</span>
          <span className="col-span-1 text-right">Time</span>
        </div>
        {isLoading ? (
          <div className="space-y-px">
            {[...Array(10)].map((_, i) => <div key={i} className="h-14 shimmer mx-4 my-1 rounded-lg" />)}
          </div>
        ) : lb.map((e, i) => (
          <motion.div
            key={e.username}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.03 }}
            className={`grid grid-cols-12 items-center px-4 py-3 border-b border-slate-50 dark:border-slate-800/50 last:border-0 ${e.is_current_user ? 'bg-blue-50 dark:bg-blue-950' : 'hover:bg-slate-50 dark:hover:bg-slate-800/50'}`}
          >
            <span className="col-span-1 font-bold text-slate-500 dark:text-slate-400">
              {RANK_ICONS[e.rank] || `#${e.rank}`}
            </span>
            <div className="col-span-4 flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold shadow-sm ${e.is_current_user ? 'bg-gradient-to-br from-blue-500 to-violet-500' : 'bg-gradient-to-br from-slate-400 to-slate-500'}`}>
                {e.username[0].toUpperCase()}
              </div>
              <span className={`text-sm font-medium ${e.is_current_user ? 'text-blue-700 dark:text-blue-400' : 'text-slate-800 dark:text-slate-200'}`}>
                {e.username} {e.is_current_user && <span className="text-xs font-normal">(you)</span>}
              </span>
            </div>
            <span className="col-span-2 text-right text-sm font-semibold text-violet-600 dark:text-violet-400">{e.total_xp.toLocaleString()}</span>
            <span className="col-span-2 text-right text-sm text-slate-600 dark:text-slate-400">Lv {e.level}</span>
            <div className="col-span-2 flex items-center justify-end gap-1 text-sm text-orange-500">
              <Flame size={13} />
              <span>{e.streak_days}d</span>
            </div>
            <div className="col-span-1 flex items-center justify-end gap-1 text-xs text-slate-400">
              <Clock size={11} />
              <span>{Math.floor(e.total_minutes / 60)}h</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
