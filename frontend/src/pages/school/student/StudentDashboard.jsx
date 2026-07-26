import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { BookOpen, CheckCircle2, Clock, Flame, ArrowRight, Brain } from 'lucide-react'
import { getStudentDashboard } from '../../../api/curriculum'
import LessonCard from '../../../components/school/LessonCard'
import GradeProgressMap from '../../../components/school/GradeProgressMap'
import { useAuthStore } from '../../../store/authStore'

export default function StudentDashboard() {
  const navigate = useNavigate()
  const { schoolName, fullName, username } = useAuthStore()
  const { data, isLoading } = useQuery({ queryKey: ['student-dashboard'], queryFn: getStudentDashboard })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-10 h-10 text-indigo-400 animate-pulse mx-auto mb-3" />
          <p className="text-slate-400">Loading your dashboard…</p>
        </div>
      </div>
    )
  }

  const d = data || {}
  const completionPct = d.completion_pct || 0

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-950 via-purple-950 to-slate-950 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-slate-400 text-sm">{schoolName} · Grade {d.grade}</p>
              <h1 className="text-2xl font-bold text-white mt-1">
                Welcome back, {fullName || username}!
              </h1>
              <p className="text-slate-400 text-sm mt-1">Continue your AI learning journey</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-black text-indigo-400">{completionPct}%</div>
              <p className="text-xs text-slate-500">complete</p>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4 h-2 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${completionPct}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
            />
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { icon: CheckCircle2, label: 'Completed', value: d.completed_lessons || 0, color: 'text-emerald-400' },
            { icon: Flame, label: 'In Progress', value: d.in_progress_lessons || 0, color: 'text-amber-400' },
            { icon: BookOpen, label: 'Total Lessons', value: d.total_lessons || 0, color: 'text-indigo-400' },
          ].map(({ icon: Icon, label, value, color }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
              <Icon className={`w-6 h-6 ${color} mx-auto mb-1`} />
              <p className="text-2xl font-bold text-white">{value}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </div>
          ))}
        </div>

        {/* Grade journey map */}
        <div className="bg-white/3 border border-white/10 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4">Your Learning Journey</h2>
          <GradeProgressMap currentGrade={d.grade} />
        </div>

        {/* Next lesson CTA */}
        {d.next_lesson && (
          <div className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-xl p-5">
            <p className="text-xs text-indigo-400 font-medium mb-1 uppercase tracking-wide">Continue Learning</p>
            <h3 className="text-white font-semibold text-lg">{d.next_lesson.title}</h3>
            <p className="text-slate-400 text-sm mt-1 line-clamp-1">{d.next_lesson.description}</p>
            <div className="flex items-center gap-4 mt-4">
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />{d.next_lesson.estimated_mins} min
              </span>
              <button
                onClick={() => navigate(`/school/student/lesson/${d.next_lesson.id}`)}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition ml-auto"
              >
                Start Lesson <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Recent lessons */}
        {d.recent_lessons?.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-white font-semibold">Recent Lessons</h2>
              <button
                onClick={() => navigate('/school/student/curriculum')}
                className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                View all <ArrowRight className="w-3 h-3" />
              </button>
            </div>
            <div className="space-y-2">
              {d.recent_lessons.map((lesson, i) => (
                <LessonCard
                  key={lesson.id}
                  lesson={lesson}
                  index={i}
                  onClick={l => navigate(`/school/student/lesson/${l.id}`)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
