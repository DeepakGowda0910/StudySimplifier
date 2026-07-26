import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { ChevronRight, ChevronLeft, Check, BookOpen, GraduationCap, Landmark, Trophy, Briefcase, Zap, Book } from 'lucide-react'
import { getCategories, getCourses, getStreams } from '../api/study'
import { updateProfile } from '../api/user'
import { useAuthStore } from '../store/authStore'

const CATEGORY_META = {
  'K-12th': { icon: BookOpen, desc: 'School education from class 1 to 12' },
  'Undergraduate': { icon: GraduationCap, desc: 'Bachelor\'s degree programs' },
  'Postgraduate': { icon: Landmark, desc: 'Master\'s and doctoral programs' },
  'Competitive Exams': { icon: Trophy, desc: 'JEE, NEET, UPSC, CAT and more' },
  'Professional': { icon: Briefcase, desc: 'CA, CFA, CS, CMA and more' },
  'Skill & Certification': { icon: Zap, desc: 'Tech, design, language skills' },
}

const BOARDS = ['CBSE', 'ICSE', 'State Board', 'ISC', 'IB', 'Cambridge', 'General']

export default function Onboarding() {
  const [step, setStep] = useState(1)
  const [category, setCategory] = useState('')
  const [course, setCourse] = useState('')
  const [stream, setStream] = useState('')
  const [board, setBoard] = useState('')
  const [categories, setCategories] = useState([])
  const [courses, setCourses] = useState([])
  const [streams, setStreams] = useState([])
  const [loading, setLoading] = useState(false)
  const { setOnboarded, username } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => { getCategories().then(setCategories).catch(() => {}) }, [])
  useEffect(() => {
    if (category) getCourses(category).then(setCourses).catch(() => setCourses([]))
  }, [category])
  useEffect(() => {
    if (category && course) {
      getStreams(category, course).then(list => {
        setStreams(list)
        if (list.length === 1) setStream(list[0])
      }).catch(() => setStreams([]))
    }
  }, [category, course])

  const handleNext = () => {
    if (step === 1 && !category) return toast.error('Please select a category')
    if (step === 2 && !course) return toast.error('Please select a course')
    if (step === 3 && streams.length > 0 && !stream) return toast.error('Please select a stream')
    setStep(s => s + 1)
  }

  const handleFinish = async () => {
    setLoading(true)
    try {
      await updateProfile({ category, course, stream: stream || (streams[0] || 'General'), board: board || 'General' })
      setOnboarded()
      toast.success('Profile set up! Let\'s start studying')
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
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy-900 px-4 py-8">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gradient">Welcome, {username}!</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Let's personalize your learning experience</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1,2,3].map(s => (
            <React.Fragment key={s}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${s === step ? 'bg-navy-600 text-white shadow-lg scale-110' : s < step ? 'bg-teal-600 text-white' : 'bg-slate-200 dark:bg-navy-700 text-slate-500 dark:text-slate-400'}`}>
                {s < step ? <Check size={16} /> : s}
              </div>
              {s < 3 && <div className={`h-0.5 w-12 rounded transition-all ${s < step ? 'bg-teal-600' : 'bg-slate-200 dark:bg-navy-700'}`} />}
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
                    const meta = CATEGORY_META[cat] || { icon: Book, desc: '' }
                    return (
                      <button key={cat} onClick={() => setCategory(cat)}
                        className={`flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-all ${category === cat ? 'border-navy-500 bg-navy-50 dark:bg-navy-800' : 'border-slate-200 dark:border-navy-700 hover:border-navy-300 dark:hover:border-navy-600'}`}>
                        <div className="w-11 h-11 rounded-xl bg-navy-600 flex items-center justify-center shadow-sm shrink-0">
                          <meta.icon size={22} className="text-white" />
                        </div>
                        <div>
                          <p className="font-semibold text-slate-900 dark:text-white text-sm">{cat}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{meta.desc}</p>
                        </div>
                        {category === cat && <Check size={18} className="ml-auto text-navy-500 shrink-0" />}
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
                      className={`p-3 rounded-xl border-2 text-left text-sm font-medium transition-all ${course === c ? 'border-navy-500 bg-navy-50 dark:bg-navy-800 text-navy-700 dark:text-navy-300' : 'border-slate-200 dark:border-navy-700 hover:border-navy-300 text-slate-700 dark:text-slate-300'}`}>
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
                  {streams.length > 0 && (
                    <div>
                      <label className="label">Stream</label>
                      <div className="flex flex-wrap gap-2">
                        {streams.map(s => (
                          <button key={s} onClick={() => setStream(s)}
                            className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all ${stream === s ? 'border-navy-500 bg-navy-50 dark:bg-navy-800 text-navy-700 dark:text-navy-300' : 'border-slate-200 dark:border-navy-700 text-slate-600 dark:text-slate-400 hover:border-navy-300'}`}>
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                  <div>
                    <label className="label">Board / Curriculum</label>
                    <div className="flex flex-wrap gap-2">
                      {BOARDS.map(b => (
                        <button key={b} onClick={() => setBoard(b)}
                          className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all ${board === b ? 'border-navy-500 bg-navy-50 dark:bg-navy-800 text-navy-700 dark:text-navy-300' : 'border-slate-200 dark:border-navy-700 text-slate-600 dark:text-slate-400 hover:border-navy-300'}`}>
                          {b}
                        </button>
                      ))}
                    </div>
                  </div>
                  <p className="text-xs text-slate-400 dark:text-slate-500">Next: pick a subject and generate your first set of study notes.</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100 dark:border-navy-700">
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
