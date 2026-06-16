import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Calendar, Plus, Trash2, Wand2, Timer, ChevronDown, ChevronUp } from 'lucide-react'
import { getExams, createExam, deleteExam, generatePlan, getPlans } from '../api/planner'
import PomodoroTimer from '../components/Planner/PomodoroTimer'

const EXAM_COLORS = ['blue', 'violet', 'emerald', 'amber', 'rose']
const DOT_MAP = { blue: 'bg-blue-500', violet: 'bg-violet-500', emerald: 'bg-emerald-500', amber: 'bg-amber-500', rose: 'bg-rose-500' }
const URGENCY = (days) => days <= 7 ? 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950' : days <= 30 ? 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950' : 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950'

export default function Planner() {
  const [tab, setTab] = useState('exams')
  const [showExamForm, setShowExamForm] = useState(false)
  const [examForm, setExamForm] = useState({ exam_name: '', subject: '', exam_date: '', notes: '', color: 'blue' })
  const [planForm, setPlanForm] = useState({ exam_name: '', exam_date: '', subjects: '', daily_hours: 3 })
  const [generating, setGenerating] = useState(false)
  const [expandedPlan, setExpandedPlan] = useState(null)
  const qc = useQueryClient()

  const { data: exams = [] } = useQuery({ queryKey: ['exams'], queryFn: getExams })
  const { data: plans = [] } = useQuery({ queryKey: ['plans'], queryFn: getPlans })

  const createExamMut = useMutation({
    mutationFn: createExam,
    onSuccess: () => { toast.success('Exam added!'); setShowExamForm(false); setExamForm({ exam_name: '', subject: '', exam_date: '', notes: '', color: 'blue' }); qc.invalidateQueries(['exams']) }
  })
  const deleteExamMut = useMutation({
    mutationFn: deleteExam,
    onSuccess: () => { toast.success('Exam removed'); qc.invalidateQueries(['exams']) }
  })

  const handleGeneratePlan = async () => {
    if (!planForm.exam_name || !planForm.exam_date || !planForm.subjects) return toast.error('Fill in all fields')
    setGenerating(true)
    try {
      const subjects = planForm.subjects.split(',').map(s => s.trim()).filter(Boolean)
      await generatePlan({ ...planForm, subjects })
      toast.success('Study plan generated! +20 XP 🎯')
      qc.invalidateQueries(['plans'])
      setTab('plans')
    } catch { toast.error('Plan generation failed') }
    finally { setGenerating(false) }
  }

  return (
    <div className="page-container space-y-6">
      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl w-fit">
        {[
          { id: 'exams', label: '📅 Exam Countdown' },
          { id: 'planner', label: '🗓️ Generate Plan' },
          { id: 'plans', label: `📋 My Plans (${plans.length})` },
          { id: 'pomodoro', label: '🍅 Pomodoro' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white dark:bg-slate-900 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}>
            {t.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Exam countdown */}
        {tab === 'exams' && (
          <motion.div key="exams" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="section-title">Upcoming Exams</h3>
              <button onClick={() => setShowExamForm(v => !v)} className="btn-primary flex items-center gap-2">
                <Plus size={16} /> Add Exam
              </button>
            </div>

            <AnimatePresence>
              {showExamForm && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="card p-5 space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div><label className="label">Exam Name</label><input className="input text-sm" placeholder="e.g. Physics Final" value={examForm.exam_name} onChange={e => setExamForm(f => ({ ...f, exam_name: e.target.value }))} /></div>
                    <div><label className="label">Subject</label><input className="input text-sm" placeholder="e.g. Physics" value={examForm.subject} onChange={e => setExamForm(f => ({ ...f, subject: e.target.value }))} /></div>
                    <div><label className="label">Exam Date</label><input className="input text-sm" type="date" value={examForm.exam_date} onChange={e => setExamForm(f => ({ ...f, exam_date: e.target.value }))} /></div>
                    <div>
                      <label className="label">Color</label>
                      <div className="flex gap-2 mt-2">
                        {EXAM_COLORS.map(c => <button key={c} onClick={() => setExamForm(f => ({ ...f, color: c }))} className={`w-7 h-7 rounded-full ${DOT_MAP[c]} border-2 transition-all ${examForm.color === c ? 'border-slate-800 dark:border-white scale-110' : 'border-transparent'}`} />)}
                      </div>
                    </div>
                  </div>
                  <div><label className="label">Notes</label><input className="input text-sm" placeholder="Any notes…" value={examForm.notes} onChange={e => setExamForm(f => ({ ...f, notes: e.target.value }))} /></div>
                  <button onClick={() => createExamMut.mutate(examForm)} disabled={!examForm.exam_name || !examForm.exam_date} className="btn-primary">Add Exam</button>
                </motion.div>
              )}
            </AnimatePresence>

            {exams.length === 0 ? (
              <div className="card p-12 text-center">
                <Calendar size={40} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                <p className="font-semibold text-slate-600 dark:text-slate-400">No exams added yet</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {exams.map(e => (
                  <motion.div key={e.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card p-5 group">
                    <div className="flex items-start justify-between">
                      <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${DOT_MAP[e.color] || DOT_MAP.blue}`} />
                      <button onClick={() => deleteExamMut.mutate(e.id)} className="opacity-0 group-hover:opacity-100 transition-opacity btn-ghost p-1 text-red-400">
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <p className="font-semibold text-slate-900 dark:text-white mt-2">{e.exam_name}</p>
                    {e.subject && <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{e.subject}</p>}
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">{e.exam_date}</p>
                    <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold mt-3 ${URGENCY(e.days_left)}`}>
                      {e.days_left < 0 ? 'Passed' : e.days_left === 0 ? 'Today!' : `${e.days_left} days left`}
                    </div>
                    {e.notes && <p className="text-xs text-slate-400 mt-2">{e.notes}</p>}
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Generate plan */}
        {tab === 'planner' && (
          <motion.div key="planner" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="card p-6 max-w-xl space-y-4">
              <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <Wand2 size={18} className="text-violet-500" /> AI Study Plan Generator
              </h3>
              <div><label className="label">Exam Name</label><input className="input text-sm" placeholder="e.g. JEE Main 2025" value={planForm.exam_name} onChange={e => setPlanForm(f => ({ ...f, exam_name: e.target.value }))} /></div>
              <div><label className="label">Exam Date</label><input className="input text-sm" type="date" value={planForm.exam_date} onChange={e => setPlanForm(f => ({ ...f, exam_date: e.target.value }))} /></div>
              <div><label className="label">Subjects (comma separated)</label><input className="input text-sm" placeholder="e.g. Physics, Chemistry, Maths" value={planForm.subjects} onChange={e => setPlanForm(f => ({ ...f, subjects: e.target.value }))} /></div>
              <div>
                <label className="label">Daily Study Hours: {planForm.daily_hours}h</label>
                <input type="range" min={1} max={12} value={planForm.daily_hours} onChange={e => setPlanForm(f => ({ ...f, daily_hours: +e.target.value }))} className="w-full accent-blue-600" />
              </div>
              <button onClick={handleGeneratePlan} disabled={generating} className="btn-primary w-full flex items-center justify-center gap-2">
                {generating ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating plan…</> : <><Wand2 size={16} /> Generate Study Plan</>}
              </button>
            </div>
          </motion.div>
        )}

        {/* Plans list */}
        {tab === 'plans' && (
          <motion.div key="plans" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
            {plans.length === 0 ? (
              <div className="card p-12 text-center">
                <p className="text-4xl mb-3">📋</p>
                <p className="font-semibold text-slate-600 dark:text-slate-400">No study plans yet</p>
                <p className="text-sm text-slate-400 mt-1">Generate one from the Planner tab</p>
              </div>
            ) : plans.map(p => (
              <div key={p.id} className="card overflow-hidden">
                <button className="w-full flex items-center justify-between p-5 text-left" onClick={() => setExpandedPlan(expandedPlan === p.id ? null : p.id)}>
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{p.title}</p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{p.start_date} → {p.end_date}</p>
                  </div>
                  {expandedPlan === p.id ? <ChevronUp size={18} className="text-slate-400 shrink-0" /> : <ChevronDown size={18} className="text-slate-400 shrink-0" />}
                </button>
                <AnimatePresence>
                  {expandedPlan === p.id && (
                    <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
                      <div className="px-5 pb-5 md-content text-slate-700 dark:text-slate-300 text-sm border-t border-slate-100 dark:border-slate-800 pt-4">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{p.content}</ReactMarkdown>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </motion.div>
        )}

        {/* Pomodoro */}
        {tab === 'pomodoro' && (
          <motion.div key="pomodoro" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <PomodoroTimer />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
