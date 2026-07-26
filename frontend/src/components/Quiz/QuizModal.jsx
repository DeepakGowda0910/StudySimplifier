import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Brain, CheckCircle, XCircle, ChevronRight, Award, BookOpen } from 'lucide-react'
import { generateQuiz, submitQuiz } from '../../api/quiz'
import toast from 'react-hot-toast'

const LETTER_MAP = { 0: 'A', 1: 'B', 2: 'C', 3: 'D' }

export default function QuizModal({ subject, chapter, contentSnippet, onClose }) {
  const [phase, setPhase] = useState('loading') // loading | quiz | results
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [current, setCurrent] = useState(0)
  const [results, setResults] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  React.useEffect(() => {
    generateQuiz({ subject, chapter, content_snippet: contentSnippet })
      .then(data => {
        setQuestions(data.questions)
        setPhase('quiz')
      })
      .catch(() => {
        toast.error('Failed to generate quiz')
        onClose()
      })
  }, [])

  const selectAnswer = (letter) => {
    if (answers[current] !== undefined) return
    setAnswers(prev => ({ ...prev, [current]: letter }))
  }

  const next = () => {
    if (current < questions.length - 1) {
      setCurrent(c => c + 1)
    } else {
      handleSubmit()
    }
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    const payload = {
      subject,
      chapter,
      answers: questions.map((q, i) => ({
        question: q.question,
        correct_answer: q.options.find(o => o.startsWith(q.correct + ')')),
        user_answer: answers[i] || 'A',
        correct_letter: q.correct,
        concept: q.concept,
        time_taken_secs: 30
      }))
    }
    try {
      const data = await submitQuiz(payload)
      setResults(data)
      setPhase('results')
    } catch {
      toast.error('Failed to submit quiz')
    } finally {
      setSubmitting(false)
    }
  }

  const reviewMistakes = () => {
    onClose()
    navigate('/flashcards')
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-navy-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-navy-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-100 dark:border-navy-700 bg-navy-700 text-white">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
              <Brain size={18} />
            </div>
            <div>
              <p className="font-semibold text-sm">Quiz</p>
              <p className="text-xs text-navy-200">{chapter}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 hover:bg-white/20 rounded-lg transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="p-6">
          {/* Loading */}
          {phase === 'loading' && (
            <div className="flex flex-col items-center justify-center py-12 gap-4">
              <div className="w-12 h-12 border-4 border-navy-200 border-t-navy-600 rounded-full animate-spin" />
              <p className="text-slate-500 dark:text-slate-400 text-sm">Generating your quiz…</p>
            </div>
          )}

          {/* Quiz */}
          {phase === 'quiz' && questions.length > 0 && (
            <AnimatePresence mode="wait">
              <motion.div
                key={current}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                {/* Progress */}
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex-1 h-1.5 bg-slate-100 dark:bg-navy-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-navy-600 rounded-full transition-all duration-500"
                      style={{ width: `${((current + 1) / questions.length) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-slate-500">{current + 1}/{questions.length}</span>
                </div>

                <p className="text-sm font-medium text-slate-800 dark:text-slate-200 leading-relaxed">
                  {questions[current].question}
                </p>

                <div className="space-y-2">
                  {questions[current].options.map((opt, i) => {
                    const letter = LETTER_MAP[i]
                    const selected = answers[current] === letter
                    const isCorrect = letter === questions[current].correct
                    const answered = answers[current] !== undefined

                    let cls = 'border border-slate-200 dark:border-navy-600 text-slate-700 dark:text-slate-300 hover:border-navy-400 hover:bg-navy-50 dark:hover:bg-navy-700'
                    if (answered) {
                      if (isCorrect) cls = 'border-2 border-green-500 bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300'
                      else if (selected) cls = 'border-2 border-red-400 bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300'
                      else cls = 'border border-slate-100 dark:border-navy-700 text-slate-400 dark:text-slate-600'
                    }

                    return (
                      <button
                        key={i}
                        onClick={() => selectAnswer(letter)}
                        disabled={answered}
                        className={`w-full flex items-center gap-3 p-3 rounded-xl text-left transition-all text-sm ${cls}`}
                      >
                        <span className="w-6 h-6 rounded-lg bg-current/10 flex items-center justify-center text-xs font-bold shrink-0">{letter}</span>
                        <span>{opt.replace(/^[A-D]\)\s*/, '')}</span>
                        {answered && isCorrect && <CheckCircle size={16} className="ml-auto text-green-500 shrink-0" />}
                        {answered && selected && !isCorrect && <XCircle size={16} className="ml-auto text-red-400 shrink-0" />}
                      </button>
                    )
                  })}
                </div>

                {answers[current] !== undefined && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-50 dark:bg-navy-700 rounded-xl p-3 text-xs text-slate-600 dark:text-slate-400"
                  >
                    <span className="font-semibold">Explanation: </span>{questions[current].explanation}
                  </motion.div>
                )}

                <button
                  onClick={next}
                  disabled={answers[current] === undefined || submitting}
                  className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
                >
                  {submitting ? (
                    <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Submitting…</>
                  ) : current < questions.length - 1 ? (
                    <>Next <ChevronRight size={16} /></>
                  ) : (
                    <>Finish & See Results <Award size={16} /></>
                  )}
                </button>
              </motion.div>
            </AnimatePresence>
          )}

          {/* Results */}
          {phase === 'results' && results && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <div className="text-center">
                <div className={`text-5xl font-bold mb-1 ${results.accuracy >= 0.8 ? 'text-green-500' : results.accuracy >= 0.6 ? 'text-amber-500' : 'text-red-500'}`}>
                  {Math.round(results.accuracy * 100)}%
                </div>
                <p className="text-slate-500 dark:text-slate-400 text-sm">{results.correct} of {results.total} correct</p>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="bg-slate-50 dark:bg-navy-700 rounded-xl p-3 text-center">
                  <p className="text-xs text-slate-500 mb-1">XP Earned</p>
                  <p className="font-bold text-navy-600 dark:text-navy-200">+{results.xp_earned}</p>
                </div>
                <div className="bg-slate-50 dark:bg-navy-700 rounded-xl p-3 text-center">
                  <p className="text-xs text-slate-500 mb-1">Accuracy</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200">{Math.round(results.accuracy * 100)}%</p>
                </div>
                <div className="bg-slate-50 dark:bg-navy-700 rounded-xl p-3 text-center">
                  <p className="text-xs text-slate-500 mb-1">Flashcards Added</p>
                  <p className="font-bold text-slate-800 dark:text-slate-200">{results.auto_flashcards_created}</p>
                </div>
              </div>

              <div className="space-y-2">
                {results.auto_flashcards_created > 0 && (
                  <button onClick={reviewMistakes} className="btn-secondary w-full flex items-center justify-center gap-2">
                    <BookOpen size={16} /> Review Missed Cards
                  </button>
                )}
                <button onClick={onClose} className="btn-primary w-full">Done</button>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
