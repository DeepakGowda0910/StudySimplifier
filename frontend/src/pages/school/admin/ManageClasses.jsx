import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, BookOpen, Plus } from 'lucide-react'
import { listClasses, createClass, listTeachers } from '../../../api/school'
import toast from 'react-hot-toast'

export default function ManageClasses() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ grade: 6, section_name: 'A', teacher_id: '', academic_year: '2025-26' })

  const { data: classes = [], isLoading } = useQuery({ queryKey: ['classes'], queryFn: listClasses })
  const { data: teachers = [] } = useQuery({ queryKey: ['teachers'], queryFn: listTeachers })

  const create = useMutation({
    mutationFn: () => createClass({
      grade: parseInt(form.grade),
      section_name: form.section_name,
      teacher_id: form.teacher_id ? parseInt(form.teacher_id) : null,
      academic_year: form.academic_year,
    }),
    onSuccess: () => {
      qc.invalidateQueries(['classes'])
      toast.success('Class created!')
      setShowForm(false)
      setForm({ grade: 6, section_name: 'A', teacher_id: '', academic_year: '2025-26' })
    },
    onError: e => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const byGrade = {}
  classes.forEach(c => {
    if (!byGrade[c.grade]) byGrade[c.grade] = []
    byGrade[c.grade].push(c)
  })

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold flex-1">Classes ({classes.length})</h1>
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition"
          >
            <Plus className="w-4 h-4" /> New Class
          </button>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {isLoading ? (
          <div className="space-y-2">{[...Array(4)].map((_, i) => <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : classes.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <BookOpen className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No classes yet</p>
          </div>
        ) : (
          Object.entries(byGrade).sort(([a],[b]) => Number(a)-Number(b)).map(([grade, gradeClasses]) => (
            <div key={grade}>
              <h3 className="text-sm font-medium text-slate-400 mb-2">Grade {grade}</h3>
              <div className="space-y-2">
                {gradeClasses.map((c, i) => {
                  const teacher = teachers.find(t => t.id === c.teacher_id)
                  return (
                    <motion.div
                      key={c.id}
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
                      className="flex items-center gap-4 bg-white/5 border border-white/10 rounded-xl px-4 py-3"
                    >
                      <div className="w-10 h-10 rounded-full bg-purple-500/15 flex items-center justify-center font-bold text-purple-400">
                        {c.section_name}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium">Grade {c.grade} — {c.section_name}</p>
                        <p className="text-xs text-slate-500">
                          {c.academic_year}
                          {teacher ? ` · ${teacher.full_name || teacher.username}` : ' · No teacher assigned'}
                        </p>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create class modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-900 border border-white/15 rounded-2xl p-6 w-full max-w-md"
          >
            <h3 className="text-white font-semibold mb-5">Create New Class</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Grade</label>
                  <select value={form.grade} onChange={e => setForm(f => ({ ...f, grade: e.target.value }))}
                    className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
                  >
                    {[6,7,8,9,10,11,12].map(g => <option key={g} value={g} className="bg-slate-800">Grade {g}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs text-slate-400 mb-1 block">Section</label>
                  <input value={form.section_name} onChange={e => setForm(f => ({ ...f, section_name: e.target.value }))}
                    className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
                    placeholder="A" maxLength={5}
                  />
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Assign Teacher (optional)</label>
                <select value={form.teacher_id} onChange={e => setForm(f => ({ ...f, teacher_id: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
                >
                  <option value="" className="bg-slate-800">No teacher yet</option>
                  {teachers.map(t => <option key={t.id} value={t.id} className="bg-slate-800">{t.full_name || t.username}</option>)}
                </select>
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Academic Year</label>
                <input value={form.academic_year} onChange={e => setForm(f => ({ ...f, academic_year: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-indigo-500"
                  placeholder="2025-26"
                />
              </div>
              <div className="flex gap-3 pt-1">
                <button onClick={() => setShowForm(false)} className="flex-1 bg-white/5 hover:bg-white/10 text-slate-300 py-2.5 rounded-lg text-sm transition">Cancel</button>
                <button onClick={() => create.mutate()} disabled={create.isPending}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg text-sm transition"
                >
                  {create.isPending ? 'Creating…' : 'Create Class'}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
