import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { TrendingUp, Clock, Target, BookOpen } from 'lucide-react'
import { getAnalytics, getStats } from '../api/user'

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899', '#84cc16']

function StatBox({ label, value, icon: Icon, color }) {
  return (
    <div className="stat-card">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
        <div className={`w-8 h-8 rounded-lg ${color} flex items-center justify-center`}>
          <Icon size={16} className="text-white" />
        </div>
      </div>
      <p className="text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
    </div>
  )
}

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({ queryKey: ['analytics'], queryFn: getAnalytics })
  const { data: stats } = useQuery({ queryKey: ['stats'], queryFn: getStats })

  const weeklyHours = analytics ? Math.round((analytics.weekly_summary?.total_minutes || 0) / 60 * 10) / 10 : 0

  return (
    <div className="page-container space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatBox label="Weekly Study" value={`${weeklyHours}h`} icon={Clock} color="bg-navy-600" />
        <StatBox label="Total XP" value={stats?.total_xp ?? 0} icon={TrendingUp} color="bg-teal-600" />
        <StatBox label="Current Level" value={stats?.level ?? 1} icon={Target} color="bg-emerald-500" />
        <StatBox label="Streak" value={`${stats?.streak_days ?? 0}d`} icon={BookOpen} color="bg-amber-500" />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => <div key={i} className="card h-64 shimmer" />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily study minutes */}
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Daily Study Minutes (Last 30 Days)</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={analytics?.daily_minutes || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d?.slice(5)} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => [`${v} min`, 'Study Time']} labelFormatter={l => `Date: ${l}`} contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 24px rgba(0,0,0,0.1)' }} />
                <Bar dataKey="minutes" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Subject distribution */}
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Study by Subject</h3>
            {analytics?.subject_distribution?.length > 0 ? (
              <div className="flex items-center gap-6">
                <ResponsiveContainer width="50%" height={180}>
                  <PieChart>
                    <Pie data={analytics.subject_distribution} dataKey="minutes" nameKey="subject" cx="50%" cy="50%" outerRadius={70} innerRadius={40}>
                      {analytics.subject_distribution.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                    </Pie>
                    <Tooltip formatter={(v) => [`${v} min`, '']} contentStyle={{ borderRadius: 12, border: 'none' }} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex-1 space-y-2">
                  {analytics.subject_distribution.slice(0, 6).map((item, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                      <span className="text-xs text-slate-600 dark:text-slate-400 truncate flex-1">{item.subject}</span>
                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{item.minutes}m</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-40 text-slate-400 text-sm">
                No study sessions recorded yet
              </div>
            )}
          </div>

          {/* XP trend placeholder */}
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Weekly Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Total XP This Week', value: analytics?.weekly_summary?.total_xp ?? 0, color: 'text-teal-600 dark:text-teal-400' },
                { label: 'Study Minutes', value: analytics?.weekly_summary?.total_minutes ?? 0, color: 'text-navy-600 dark:text-navy-300' },
                { label: 'Current Level', value: analytics?.weekly_summary?.level ?? 1, color: 'text-emerald-600 dark:text-emerald-400' },
                { label: 'Day Streak', value: `${analytics?.weekly_summary?.streak ?? 0}d`, color: 'text-amber-600 dark:text-amber-400' },
              ].map(item => (
                <div key={item.label} className="bg-slate-50 dark:bg-slate-800 rounded-xl p-4">
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{item.label}</p>
                  <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Level progress */}
          <div className="card p-6">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Level Progress</h3>
            <div className="flex items-center gap-4 mb-6">
              <div className="w-20 h-20 rounded-2xl bg-navy-600 flex items-center justify-center shadow-lg">
                <span className="text-3xl font-black text-white">{stats?.level ?? 1}</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Level {stats?.level ?? 1}</p>
                <p className="text-2xl font-bold text-slate-900 dark:text-white mt-0.5">{stats?.total_xp ?? 0} XP</p>
                <p className="text-xs text-slate-400 mt-1">{500 - (stats?.level_progress ?? 0)} XP to next level</p>
              </div>
            </div>
            <div className="xp-bar">
              <motion.div className="xp-fill" initial={{ width: 0 }} animate={{ width: `${((stats?.level_progress ?? 0) / 500) * 100}%` }} transition={{ duration: 0.8 }} />
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>{stats?.level_progress ?? 0} XP</span>
              <span>500 XP</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
