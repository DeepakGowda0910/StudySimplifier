import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, CheckCircle2, Clock, Trophy, BarChart3 } from 'lucide-react'
import { getMyProgress } from '../../../api/curriculum'

export default function MyProgress() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({ queryKey: ['my-progress'], queryFn: getMyProgress })

  const lessons = data?.lessons || []
  const completed = lessons.filter(l => l.status === 'completed')
  const totalTime = data?.total_time_mins || 0
  const avgScore = completed.filter(l => l.score != null).length
    ? Math.round(completed.filter(l => l.score != null).reduce((a, l) => a + l.score, 0) / completed.filter(l => l.score != null).length)
    : null

  // Group by grade
  const byGrade = {}
  lessons.forEach(l => {
    if (!byGrade[l.grade]) byGrade[l.grade] = []
    byGrade[l.grade].push(l)
  })

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold">My Progress</h1>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <Trophy className="w-6 h-6 text-yellow-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-white">{data?.total_completed || 0}</p>
            <p className="text-xs text-slate-500">Completed</p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <Clock className="w-6 h-6 text-indigo-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-white">{totalTime}</p>
            <p className="text-xs text-slate-500">Minutes</p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <BarChart3 className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <p className="text-2xl font-bold text-white">{avgScore != null ? `${avgScore}%` : '—'}</p>
            <p className="text-xs text-slate-500">Avg Score</p>
          </div>
        </div>

        {/* By grade */}
        {isLoading ? (
          <div className="space-y-2">{[...Array(4)].map((_, i) => <div key={i} className="h-12 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : (
          Object.entries(byGrade).sort(([a], [b]) => Number(a) - Number(b)).map(([grade, gradeLessons]) => (
            <div key={grade}>
              <h3 className="text-sm font-medium text-slate-400 mb-2">Grade {grade}</h3>
              <div className="space-y-1.5">
                {gradeLessons.map((l, i) => (
                  <motion.div
                    key={l.lesson_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="flex items-center gap-3 bg-white/3 border border-white/5 rounded-lg px-3 py-2.5"
                  >
                    <CheckCircle2 className={`w-4 h-4 flex-shrink-0 ${l.status === 'completed' ? 'text-emerald-400' : 'text-slate-600'}`} />
                    <span className="text-sm text-slate-300 flex-1 truncate">{l.title}</span>
                    <div className="flex items-center gap-3 text-xs text-slate-500 flex-shrink-0">
                      {l.score != null && <span className="text-indigo-400">{l.score}%</span>}
                      {l.time_spent_mins > 0 && <span>{l.time_spent_mins}m</span>}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ))
        )}

        {!isLoading && lessons.length === 0 && (
          <div className="text-center py-16 text-slate-500">
            <Trophy className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No progress yet — start your first lesson!</p>
          </div>
        )}
      </div>
    </div>
  )
}
