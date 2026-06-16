import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { ChevronRight, ChevronLeft, Check } from 'lucide-react'
import { getCategories, getCourses, getStreams } from '../api/study'
import { updateProfile } from '../api/user'
import { useAuthStore } from '../store/authStore'

const CATEGORY_META = {
  'K-12th': { icon: '📚', desc: 'School education from class 1 to 12', color: 'from-blue-500 to-cyan-500' },
  'Undergraduate': { icon: '🎓', desc: 'Bachelor\'s degree programs', color: 'from-violet-500 to-purple-500' },
  'Postgraduate': { icon: '🏛️', desc: 'Master\'s and doctoral programs', color: 'from-emerald-500 to-teal-500' },
  'Competitive Exams': { icon: '🏆', desc: 'JEE, NEET, UPSC, CAT and more', color: 'from-amber-500 to-orange-500' },
  'Professional': { icon: '💼', desc: 'CA, CFA, CS, CMA and more', color: 'from-rose-500 to-pink-500' },
  'Skill & Certification': { icon: '⚡', desc: 'Tech, design, language skills', color: 'from-indigo-500 to-blue-500' },
}

const BOARDS = ['CBSE', 'ICSE', 'State Board', 'ISC', 'IB', 'Cambridge', 'General']
const STREAMS = ['Science', 'Commerce', 'Arts', 'General', 'Engineering', 'Medical']

export default function Onboarding() {
  const [step, setStep] = useState(1)
  const [category, setCategory] = useState('')
  const [course, setCourse] = useState('')
  const [stream, setStream] = useState('')
  const [board, setBoard] = useState('')
  const [categories, setCategories] = useState([])
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(false)
  const { setOnboarded, username } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => { getCategories().then(setCategories).catch(() => {}) }, [])
  useEffect(() => {
    if (category) getCourses(category).then(setCourses).catch(() => setCourses([]))
  }, [category])

  const noCoursePick = ['Competitive Exams', 'Professional', 'Skill & Certification']

  const handleNext = () => {
    if (step === 1 && !category) return toast.error('Please select a category')
    if (step === 2 && !course && !noCoursePick.includes(category)) return toast.error('Please select a course')
    if (step === 1 && noCoursePick.includes(category)) {
      setStep(3)
    } else {
      setStep(s => s + 1)
    }
  }

  const handleFinish = async () => {
    setLoading(true)
    try {
      await updateProfile({ category, course: course || category, stream: stream || 'General', board: board || 'General' })
      setOnboarded()
      toast.success('Profile set up! Let\'s start studying 🚀')
      navigate('/')
    } catch {
      toast.error('Failed to save profile')
    } finally {
      setLoading(false)
    }
  }

  const variants = {
    enter: { opacity: 0, x: 40 },
    center: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -40 }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-violet-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 px-4 py-8">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gradient">Welcome, {username}!</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Let's personalize your learning experience</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1,2,3].map(s => (
            <React.Fragment key={s}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${s === step ? 'bg-blue-600 text-white shadow-lg scale-110' : s < step ? 'bg-green-500 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-500'}`}>
                {s < step ? <Check size={16} /> : s}
              </div>
              {s < 3 && <div className={`h-0.5 w-12 rounded transition-all ${s < step ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'}`} />}
            </React.Fragment>
          ))}
        </div>

        <div className="card p-8">
          <AnimatePresence mode="wait">
            {step === 1 && (
              <motion.div key="step1" variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.2 }}>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">What are you studying?</h2>
                <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">Select your education category</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {categories.map(cat => {
                    const meta = CATEGORY_META[cat] || { icon: '📖', desc: '', color: 'from-slate-500 to-slate-600' }
                    return (
                      <button key={cat} onClick={() => setCategory(cat)}
                        className={`flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all ${category === cat ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' : 'border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700'}`}>
                        <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${meta.color} flex items-center justify-center text-2xl shadow-sm shrink-0`}>{meta.icon}</div>
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white text-sm">{cat}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{meta.desc}</p>
                        </div>
                        {category === cat && <Check size={18} className="ml-auto text-blue-500 shrink-0" />}
                      </button>
                    )
                  })}
                </div>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div key="step2" variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.2 }}>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Select your course</h2>
                <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">Choose your specific program</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-72 overflow-y-auto pr-1">
                  {courses.map(c => (
                    <button key={c} onClick={() => setCourse(c)}
                      className={`p-3 rounded-xl border-2 text-left text-sm font-medium transition-all ${course === c ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-400' : 'border-slate-200 dark:border-slate-700 hover:border-blue-300 text-slate-700 dark:text-slate-300'}`}>
                      {c}
                    </button>
                  ))}
                </div>
              </motion.div>
            )}

            {step === 3 && (
              <motion.div key="step3" variants={variants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.2 }}>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Almost done!</h2>
                <p className="text-slate-500 dark:text-slate-400 text-sm mb-6">Select your stream and board (optional)</p>
                <div className="space-y-5">
                  <div>
                    <label className="label">Stream</label>
                    <div className="flex flex-wrap gap-2">
                      {STREAMS.map(s => (
                        <button key={s} onClick={() => setStream(s)}
                          className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all ${stream === s ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-400' : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-blue-300'}`}>
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="label">Board / Curriculum</label>
                    <div className="flex flex-wrap gap-2">
                      {BOARDS.map(b => (
                        <button key={b} onClick={() => setBoard(b)}
                          className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all ${board === b ? 'border-blue-500 bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-400' : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-blue-300'}`}>
                          {b}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100 dark:border-slate-800">
            <button onClick={() => setStep(s => Math.max(1, s - 1))} disabled={step === 1} className="btn-secondary flex items-center gap-2">
              <ChevronLeft size={18} /> Back
            </button>
            {step < 3 ? (
              <button onClick={handleNext} className="btn-primary flex items-center gap-2">
                Continue <ChevronRight size={18} />
              </button>
            ) : (
              <button onClick={handleFinish} disabled={loading} className="btn-primary flex items-center gap-2">
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Check size={18} />}
                Start Learning!
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
