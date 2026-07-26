import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, XCircle, ChevronRight, Trophy } from 'lucide-react'

export default function InteractiveQuiz({ questions = [], onComplete }) {
  const [current, setCurrent] = useState(0)
  const [selected, setSelected] = useState(null)
  const [answers, setAnswers] = useState([])
  const [done, setDone] = useState(false)

  const q = questions[current]
  const isAnswered = selected !== null

  const handleSelect = (idx) => {
    if (isAnswered) return
    setSelected(idx)
  }

  const handleNext = () => {
    const newAnswers = [...answers, { question: q.q, selected, correct: q.answer, isCorrect: selected === q.answer }]
    setAnswers(newAnswers)

    if (current + 1 < questions.length) {
      setCurrent(c => c + 1)
      setSelected(null)
    } else {
      setDone(true)
      const score = Math.round((newAnswers.filter(a => a.isCorrect).length / questions.length) * 100)
      onComplete?.(score)
    }
  }

  if (!questions.length) return null

  if (done) {
    const correct = answers.filter(a => a.isCorrect).length
    const score = Math.round((correct / questions.length) * 100)
    return (
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-8">
        <Trophy className={`w-16 h-16 mx-auto mb-4 ${score >= 80 ? 'text-yellow-400' : score >= 60 ? 'text-indigo-400' : 'text-slate-500'}`} />
        <p className="text-3xl font-black text-white mb-1">{score}%</p>
        <p className="text-slate-400 text-sm">{correct} of {questions.length} correct</p>
        <div className="mt-6 space-y-3 text-left max-h-48 overflow-y-auto">
          {answers.map((a, i) => (
            <div key={i} className={`flex items-start gap-2 text-sm p-3 rounded-lg ${a.isCorrect ? 'bg-emerald-500/10' : 'bg-red-500/10'}`}>
              {a.isCorrect ? <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" /> : <XCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />}
              <div>
                <p className="text-slate-300 font-medium">{a.question}</p>
                {!a.isCorrect && (
                  <p className="text-slate-500 text-xs mt-0.5">Correct: {questions[i].options[a.correct]}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Progress */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all"
            style={{ width: `${((current) / questions.length) * 100}%` }}
          />
        </div>
        <span className="text-xs text-slate-500 flex-shrink-0">{current + 1}/{questions.length}</span>
      </div>

      {/* Question */}
      <AnimatePresence mode="wait">
        <motion.div key={current} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
          <p className="text-white font-medium mb-4">{q.q}</p>
          <div className="space-y-2">
            {q.options.map((opt, idx) => {
              let cls = 'border-white/15 bg-white/5 hover:border-indigo-400/50 hover:bg-indigo-500/5'
              if (isAnswered) {
                if (idx === q.answer) cls = 'border-emerald-500/60 bg-emerald-500/10'
                else if (idx === selected) cls = 'border-red-500/60 bg-red-500/10'
                else cls = 'border-white/5 bg-white/3 opacity-50'
              }
              return (
                <button
                  key={idx}
                  onClick={() => handleSelect(idx)}
                  className={`w-full text-left px-4 py-3 rounded-xl border text-sm transition-all flex items-center gap-3 ${cls}`}
                >
                  <span className={`w-6 h-6 rounded-full border flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                    isAnswered && idx === q.answer ? 'border-emerald-500 text-emerald-400 bg-emerald-500/20' :
                    isAnswered && idx === selected ? 'border-red-500 text-red-400 bg-red-500/20' :
                    'border-slate-600 text-slate-500'
                  }`}>
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span className={isAnswered && idx === q.answer ? 'text-emerald-300' : isAnswered && idx === selected ? 'text-red-300' : 'text-slate-200'}>
                    {opt}
                  </span>
                  {isAnswered && idx === q.answer && <CheckCircle2 className="w-4 h-4 text-emerald-400 ml-auto" />}
                  {isAnswered && idx === selected && idx !== q.answer && <XCircle className="w-4 h-4 text-red-400 ml-auto" />}
                </button>
              )
            })}
          </div>
        </motion.div>
      </AnimatePresence>

      {isAnswered && (
        <motion.button
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
          onClick={handleNext}
          className="w-full mt-2 flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition"
        >
          {current + 1 < questions.length ? 'Next Question' : 'Finish Quiz'}
          <ChevronRight className="w-4 h-4" />
        </motion.button>
      )}
    </div>
  )
}
