import { motion } from 'framer-motion'
import { CheckCircle2, Lock, ArrowRight } from 'lucide-react'

const GRADE_TITLES = {
  6: 'What is AI?',
  7: 'Algorithms & Patterns',
  8: 'Your First Real Code',
  9: 'Data is the New Oil',
  10: 'How AI Actually Learns',
  11: 'Build Real AI',
  12: 'Ship an AI Product',
}

const GRADE_COLORS = {
  6: 'from-pink-500 to-rose-600',
  7: 'from-orange-500 to-amber-600',
  8: 'from-yellow-500 to-orange-600',
  9: 'from-emerald-500 to-teal-600',
  10: 'from-cyan-500 to-blue-600',
  11: 'from-indigo-500 to-purple-600',
  12: 'from-purple-500 to-violet-600',
}

export default function GradeProgressMap({ currentGrade, completedGrades = [], onSelectGrade }) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {[6, 7, 8, 9, 10, 11, 12].map((grade, idx) => {
        const isCompleted = completedGrades.includes(grade)
        const isCurrent = grade === currentGrade
        const isLocked = grade > currentGrade

        return (
          <div key={grade} className="flex items-center">
            <motion.button
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => !isLocked && onSelectGrade?.(grade)}
              className={`relative flex flex-col items-center p-3 rounded-xl border transition-all ${
                isCurrent
                  ? `bg-gradient-to-br ${GRADE_COLORS[grade]} border-transparent shadow-lg shadow-indigo-500/30 scale-110`
                  : isCompleted
                  ? 'bg-emerald-500/10 border-emerald-500/30 hover:border-emerald-400/50'
                  : isLocked
                  ? 'bg-white/3 border-white/5 opacity-40 cursor-not-allowed'
                  : 'bg-white/5 border-white/10 hover:border-white/20 cursor-pointer'
              }`}
            >
              {isCompleted && !isCurrent && (
                <CheckCircle2 className="absolute -top-1.5 -right-1.5 w-4 h-4 text-emerald-400 bg-slate-900 rounded-full" />
              )}
              {isLocked && (
                <Lock className="absolute -top-1.5 -right-1.5 w-3.5 h-3.5 text-slate-600" />
              )}
              <span className={`text-xs font-bold ${isCurrent ? 'text-white' : isCompleted ? 'text-emerald-400' : 'text-slate-400'}`}>
                Grade
              </span>
              <span className={`text-2xl font-black ${isCurrent ? 'text-white' : isCompleted ? 'text-emerald-300' : 'text-slate-500'}`}>
                {grade}
              </span>
              <span className={`text-xs text-center leading-tight max-w-16 ${isCurrent ? 'text-white/80' : 'text-slate-500'}`}>
                {GRADE_TITLES[grade].split(' ').slice(0, 3).join(' ')}
              </span>
            </motion.button>
            {idx < 6 && (
              <ArrowRight className={`w-4 h-4 mx-1 flex-shrink-0 ${
                grade < currentGrade ? 'text-emerald-500' : 'text-slate-700'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}
