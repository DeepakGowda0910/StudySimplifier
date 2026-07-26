import { motion } from 'framer-motion'
import { CheckCircle2, Circle, Clock, PlayCircle, Lock, Code, FileText, HelpCircle, Rocket } from 'lucide-react'

const TYPE_ICONS = {
  text: FileText,
  coding: Code,
  quiz: HelpCircle,
  project: Rocket,
  video: PlayCircle,
}

const STATUS_CONFIG = {
  completed: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', label: 'Completed' },
  in_progress: { icon: PlayCircle, color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/30', label: 'In Progress' },
  not_started: { icon: Circle, color: 'text-slate-500', bg: 'bg-white/3 border-white/10', label: 'Not Started' },
  locked: { icon: Lock, color: 'text-slate-600', bg: 'bg-white/2 border-white/5', label: 'Locked' },
}

export default function LessonCard({ lesson, onClick, index = 0 }) {
  const status = lesson.progress_status || 'not_started'
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.not_started
  const StatusIcon = cfg.icon
  const TypeIcon = TYPE_ICONS[lesson.content_type] || FileText

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      onClick={() => status !== 'locked' && onClick?.(lesson)}
      className={`group border rounded-xl p-4 transition-all cursor-pointer ${cfg.bg} ${
        status === 'locked' ? 'opacity-50 cursor-not-allowed' : 'hover:border-indigo-500/50 hover:bg-indigo-500/5'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Status icon */}
        <div className="mt-0.5 flex-shrink-0">
          <StatusIcon className={`w-5 h-5 ${cfg.color}`} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className={`font-medium text-sm leading-tight ${
              status === 'locked' ? 'text-slate-600' : 'text-white group-hover:text-indigo-300 transition-colors'
            }`}>
              {lesson.title}
            </h3>
            <div className="flex-shrink-0 flex items-center gap-1.5">
              <TypeIcon className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-xs text-slate-500 flex items-center gap-0.5">
                <Clock className="w-3 h-3" />{lesson.estimated_mins}m
              </span>
            </div>
          </div>

          {lesson.description && (
            <p className="text-xs text-slate-500 mt-1 line-clamp-1">{lesson.description}</p>
          )}

          {/* Score badge for completed */}
          {status === 'completed' && lesson.score != null && (
            <div className="mt-2">
              <span className="text-xs bg-emerald-500/15 text-emerald-400 px-2 py-0.5 rounded-full">
                Score: {lesson.score}%
              </span>
            </div>
          )}

          {/* Progress bar for in_progress */}
          {status === 'in_progress' && (
            <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 rounded-full w-1/3 animate-pulse" />
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
