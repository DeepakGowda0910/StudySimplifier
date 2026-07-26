import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, CheckCircle2, Clock, BarChart3, Trophy } from 'lucide-react'
import { getStudentProgressDetail } from '../../../api/school'

export default function StudentProgress() {
  const { studentId } = useParams()
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['student-progress', studentId],
    queryFn: () => getStudentProgressDetail(studentId),
  })

  const lessons = data?.progress || []
  const completed = lessons.filter(l => l.status === 'completed')
  const totalTime = lessons.reduce((a, l) => a + (l.time_spent_mins || 0), 0)
  const avgScore = completed.filter(l => l.score != null).length
    ? Math.round(completed.filter(l => l.score != null).reduce((a, l) => a + l.score, 0) / completed.filter(l => l.score != null).length)
    : null

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-white font-semibold">{data?.student?.name || 'Student'}</h1>
            <p className="text-xs text-slate-500">Lesson progress detail</p>
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6 space-y-5">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <Trophy className="w-5 h-5 text-yellow-400 mx-auto mb-1" />
            <p className="text-xl font-bold">{completed.length}</p>
            <p className="text-xs text-slate-500">Completed</p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <Clock className="w-5 h-5 text-indigo-400 mx-auto mb-1" />
            <p className="text-xl font-bold">{totalTime}m</p>
            <p className="text-xs text-slate-500">Time Spent</p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
            <BarChart3 className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
            <p className="text-xl font-bold">{avgScore != null ? `${avgScore}%` : '—'}</p>
            <p className="text-xs text-slate-500">Avg Score</p>
          </div>
        </div>

        {/* Lesson list */}
        {isLoading ? (
          <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : (
          <div className="space-y-1.5">
            {lessons.map((l, i) => (
              <motion.div
                key={l.lesson_id}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.025 }}
                className="flex items-center gap-3 bg-white/3 border border-white/5 rounded-lg px-4 py-3"
              >
                <CheckCircle2 className={`w-4 h-4 flex-shrink-0 ${
                  l.status === 'completed' ? 'text-emerald-400' :
                  l.status === 'in_progress' ? 'text-indigo-400' : 'text-slate-700'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-300 truncate">{l.lesson_title}</p>
                  <p className="text-xs text-slate-600">Grade {l.grade}</p>
                </div>
                <div className="flex items-center gap-3 text-xs text-slate-500 flex-shrink-0">
                  {l.score != null && <span className="text-indigo-400 font-medium">{l.score}%</span>}
                  {l.time_spent_mins > 0 && <span>{l.time_spent_mins}m</span>}
                  <span className={`capitalize ${
                    l.status === 'completed' ? 'text-emerald-400' :
                    l.status === 'in_progress' ? 'text-amber-400' : 'text-slate-600'
                  }`}>{l.status.replace('_', ' ')}</span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
