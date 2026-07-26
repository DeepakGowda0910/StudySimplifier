import { motion } from 'framer-motion'
import { CheckCircle2, Circle, PlayCircle } from 'lucide-react'

const STATUS_COLORS = {
  completed: 'bg-emerald-500',
  in_progress: 'bg-indigo-500',
  not_started: 'bg-white/10',
}

const STATUS_LABELS = {
  completed: 'Completed',
  in_progress: 'In Progress',
  not_started: 'Not Started',
}

export default function ClassProgressHeatmap({ data }) {
  const { students = [], lessons = [], progress = {} } = data || {}

  if (!students.length || !lessons.length) {
    return <p className="text-slate-500 text-sm text-center py-8">No data yet</p>
  }

  return (
    <div className="overflow-auto">
      <div className="min-w-max">
        {/* Legend */}
        <div className="flex gap-4 mb-4 text-xs">
          {Object.entries(STATUS_LABELS).map(([status, label]) => (
            <div key={status} className="flex items-center gap-1.5">
              <div className={`w-3 h-3 rounded-sm ${STATUS_COLORS[status]}`} />
              <span className="text-slate-400">{label}</span>
            </div>
          ))}
        </div>

        {/* Header row */}
        <div className="flex gap-1 mb-1">
          <div className="w-40 flex-shrink-0" />
          {lessons.map(lesson => (
            <div key={lesson.id} className="w-8 flex-shrink-0 flex items-end justify-center" title={lesson.title}>
              <span className="text-xs text-slate-500 transform -rotate-45 origin-bottom-left translate-y-1 block w-16 text-left">
                {lesson.order + 1}
              </span>
            </div>
          ))}
        </div>

        {/* Rows */}
        {students.map((student, si) => (
          <motion.div
            key={student.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: si * 0.03 }}
            className="flex items-center gap-1 mb-1"
          >
            <div className="w-40 flex-shrink-0 pr-2">
              <p className="text-xs text-slate-300 truncate">{student.name}</p>
            </div>
            {lessons.map(lesson => {
              const status = progress[String(student.id)]?.[String(lesson.id)] || 'not_started'
              return (
                <div
                  key={lesson.id}
                  className={`w-8 h-8 rounded-md flex-shrink-0 flex items-center justify-center transition-all ${STATUS_COLORS[status]}`}
                  title={`${student.name} — ${lesson.title}: ${STATUS_LABELS[status]}`}
                >
                  {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-900/60" />}
                  {status === 'in_progress' && <PlayCircle className="w-4 h-4 text-indigo-900/60" />}
                </div>
              )
            })}
          </motion.div>
        ))}
      </div>
    </div>
  )
}
