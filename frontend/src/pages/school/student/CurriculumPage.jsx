import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, BookOpen } from 'lucide-react'
import { getCurriculum } from '../../../api/curriculum'
import LessonCard from '../../../components/school/LessonCard'
import { useAuthStore } from '../../../store/authStore'

export default function CurriculumPage() {
  const navigate = useNavigate()
  const { schoolName } = useAuthStore()
  const { data, isLoading } = useQuery({ queryKey: ['curriculum'], queryFn: getCurriculum })

  const lessons = data?.lessons || []
  const grade = data?.grade

  const completed = lessons.filter(l => l.progress_status === 'completed').length
  const pct = lessons.length ? Math.round((completed / lessons.length) * 100) : 0

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate('/school/student')} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-white font-semibold">Grade {grade} Curriculum</h1>
            <p className="text-xs text-slate-500">{schoolName} · {completed}/{lessons.length} completed · {pct}%</p>
          </div>
          <BookOpen className="w-5 h-5 text-indigo-400" />
        </div>
        {lessons.length > 0 && (
          <div className="h-0.5 bg-white/5">
            <motion.div
              initial={{ width: 0 }} animate={{ width: `${pct}%` }}
              className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
            />
          </div>
        )}
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6">
        {isLoading ? (
          <div className="space-y-2">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-2">
            {lessons.map((lesson, i) => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                index={i}
                onClick={l => navigate(`/school/student/lesson/${l.id}`)}
              />
            ))}
            {lessons.length === 0 && (
              <div className="text-center py-16 text-slate-500">
                <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p>No lessons available yet.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
