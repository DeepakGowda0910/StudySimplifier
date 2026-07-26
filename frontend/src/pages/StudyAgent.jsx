import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { getDailyAgenda, regenerateAgenda, getWeakSpots, getPerformanceSummary } from '../api/agent'
import {
  Brain, RefreshCw, Clock, BookOpen, CreditCard, Zap, Coffee,
  Target, TrendingUp, TrendingDown, AlertTriangle, Star, Trophy, Flame
} from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

const BLOCK_ICONS = {
  flashcards: CreditCard,
  study: BookOpen,
  quiz: Brain,
  revision: Zap,
  break: Coffee,
}
const BLOCK_COLORS = {
  flashcards: 'bg-navy-100 text-navy-700 dark:bg-navy-800 dark:text-navy-300 border-navy-200 dark:border-navy-600',
  study: 'bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-400 border-teal-200 dark:border-teal-800',
  quiz: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400 border-green-200 dark:border-green-800',
  revision: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400 border-amber-200 dark:border-amber-800',
  break: 'bg-slate-100 text-slate-600 dark:bg-navy-800 dark:text-slate-400 border-slate-200 dark:border-navy-600',
}

const ELO_LABEL_COLOR = {
  Beginner: 'text-red-500',
  Intermediate: 'text-amber-500',
  Advanced: 'text-navy-500',
  Expert: 'text-green-500',
}

function AgendaBlock({ block, index }) {
  const Icon = BLOCK_ICONS[block.type] || BookOpen
  const colorClass = BLOCK_COLORS[block.type] || BLOCK_COLORS.study
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08 }}
      className={`flex gap-4 p-4 rounded-xl border ${colorClass}`}
    >
      <div className="flex flex-col items-center gap-1 shrink-0">
        <div className="w-9 h-9 rounded-xl bg-current/10 flex items-center justify-center">
          <Icon size={18} />
        </div>
        <span className="text-xs font-medium opacity-70">{block.minutes}m</span>
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-xs font-semibold opacity-70 uppercase tracking-wider">{block.time}</p>
            <p className="font-medium text-sm mt-0.5">{block.subject} — {block.topic}</p>
            <p className="text-sm opacity-80 mt-1">{block.action}</p>
          </div>
          <span className="shrink-0 text-xs font-bold bg-current/10 px-2 py-1 rounded-lg">+{block.xp} XP</span>
        </div>
        {block.why && <p className="text-xs opacity-60 mt-2 italic">{block.why}</p>}
      </div>
    </motion.div>
  )
}

export default function StudyAgent() {
  const qc = useQueryClient()

  const { data: agendaData, isLoading: agendaLoading } = useQuery({
    queryKey: ['daily-agenda'],
    queryFn: getDailyAgenda,
    staleTime: 1000 * 60 * 30,
  })

  const { data: weakData, isLoading: weakLoading } = useQuery({
    queryKey: ['weak-spots'],
    queryFn: getWeakSpots,
  })

  const { data: perfData } = useQuery({
    queryKey: ['performance-summary'],
    queryFn: getPerformanceSummary,
  })

  const regenerate = useMutation({
    mutationFn: regenerateAgenda,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['daily-agenda'] })
    }
  })

  const agenda = agendaData?.agenda
  const weak = weakData?.weak || []
  const strong = weakData?.strong || []

  const radarData = weak.slice(0, 6).map(w => ({
    subject: `${w.subject.slice(0, 10)}`,
    elo: Math.round(w.elo),
    fullMark: 1500,
  }))

  const barData = [...weak.slice(0, 5).map(w => ({ name: w.chapter.slice(0, 14), elo: Math.round(w.elo), fill: '#ef4444' })),
    ...strong.slice(0, 3).map(s => ({ name: s.chapter.slice(0, 14), elo: Math.round(s.elo), fill: '#22c55e' }))]

  return (
    <div className="page-container space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Brain className="text-navy-500" size={26} /> Study Agent
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-0.5">AI-powered personalized learning schedule</p>
        </div>
        <button
          onClick={() => regenerate.mutate()}
          disabled={regenerate.isPending}
          className="btn-secondary flex items-center gap-2"
        >
          <RefreshCw size={15} className={regenerate.isPending ? 'animate-spin' : ''} />
          Regenerate
        </button>
      </div>

      {/* Performance pills */}
      {perfData && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Avg ELO', value: perfData.average_elo, icon: TrendingUp, color: 'text-navy-500' },
            { label: 'Level', value: perfData.elo_label, icon: Trophy, color: ELO_LABEL_COLOR[perfData.elo_label] || 'text-navy-500' },
            { label: 'Subjects', value: perfData.subjects_studied, icon: BookOpen, color: 'text-teal-500' },
            { label: 'Mistakes', value: perfData.mistake_count, icon: AlertTriangle, color: 'text-amber-500' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card p-4 flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl bg-current/10 flex items-center justify-center ${color}`}>
                <Icon size={18} className={color} />
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
                <p className="font-bold text-slate-800 dark:text-slate-200">{value}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Daily agenda */}
        <div className="lg:col-span-3 space-y-4">
          {agendaLoading ? (
            <div className="card p-12 flex flex-col items-center gap-4">
              <div className="w-12 h-12 border-4 border-navy-200 border-t-navy-600 rounded-full animate-spin" />
              <p className="text-slate-500 text-sm">Agent is analyzing your learning data…</p>
            </div>
          ) : agenda ? (
            <>
              {/* Greeting card */}
              <div className="card p-5 bg-navy-700 text-white border-0">
                <div className="flex items-start gap-3">
                  <Flame size={22} className="shrink-0 mt-0.5 text-amber-300" />
                  <div>
                    <p className="font-semibold text-base">{agenda.greeting}</p>
                    {agenda.priority_alert && (
                      <div className="mt-2 bg-white/15 rounded-xl p-3 text-sm text-navy-100">
                        <span className="font-semibold text-white">Priority: </span>{agenda.priority_alert}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Predicted score */}
              {agenda.predicted_score && (
                <div className="card p-4 flex items-center gap-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
                  <Target size={18} className="text-amber-600 shrink-0" />
                  <p className="text-sm text-amber-800 dark:text-amber-300">{agenda.predicted_score}</p>
                </div>
              )}

              {/* Blocks */}
              <div className="card p-4 space-y-3">
                <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                  <Clock size={16} className="text-navy-500" /> Today's Schedule
                </h3>
                {(agenda.blocks || []).map((block, i) => (
                  <AgendaBlock key={i} block={block} index={i} />
                ))}
              </div>

              {/* Insight */}
              {agenda.insight && (
                <div className="card p-4 flex items-start gap-3 bg-navy-50 dark:bg-navy-800/50 border border-navy-200 dark:border-navy-600">
                  <Star size={16} className="text-navy-500 shrink-0 mt-0.5" />
                  <p className="text-sm text-navy-800 dark:text-navy-300">{agenda.insight}</p>
                </div>
              )}
            </>
          ) : (
            <div className="card p-12 text-center text-slate-500">No agenda available. Try regenerating.</div>
          )}
        </div>

        {/* Weak spots panel */}
        <div className="lg:col-span-2 space-y-4">
          {/* Radar chart */}
          {radarData.length > 0 && (
            <div className="card p-4">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-3 text-sm">Skill Radar</h3>
              <ResponsiveContainer width="100%" height={200}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="#e2e8f0" />
                  <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <Radar name="ELO" dataKey="elo" stroke="#2e4d7a" fill="#2e4d7a" fillOpacity={0.2} strokeWidth={2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* ELO bar chart */}
          {barData.length > 0 && (
            <div className="card p-4">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-3 text-sm">Chapter ELO</h3>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={barData} layout="vertical">
                  <XAxis type="number" domain={[600, 1500]} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <YAxis type="category" dataKey="name" width={80} tick={{ fontSize: 10, fill: '#94a3b8' }} />
                  <Tooltip
                    contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#f1f5f9', fontSize: 12 }}
                    cursor={{ fill: 'rgba(46,77,122,0.1)' }}
                  />
                  <Bar dataKey="elo" radius={[0, 4, 4, 0]}>
                    {barData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Weak list */}
          {weak.length > 0 && (
            <div className="card p-4">
              <h3 className="font-semibold text-slate-900 dark:text-white mb-3 text-sm flex items-center gap-2">
                <TrendingDown size={14} className="text-red-500" /> Needs Attention
              </h3>
              <div className="space-y-2">
                {weak.slice(0, 5).map((w, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-700 dark:text-slate-300 truncate">{w.chapter}</p>
                      <p className="text-xs text-slate-400">{w.subject}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <div className="w-16 h-1.5 bg-slate-100 dark:bg-navy-700 rounded-full overflow-hidden">
                        <div className="h-full bg-red-400 rounded-full" style={{ width: `${Math.round(w.accuracy * 100)}%` }} />
                      </div>
                      <span className="text-xs font-bold text-red-500 w-8 text-right">{Math.round(w.elo)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {weakLoading && (
            <div className="card p-8 flex justify-center">
              <div className="w-8 h-8 border-4 border-navy-200 border-t-navy-600 rounded-full animate-spin" />
            </div>
          )}

          {!weakLoading && weak.length === 0 && (
            <div className="card p-6 text-center text-slate-500 dark:text-slate-400 text-sm">
              Take some quizzes to see your weak spots!
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
