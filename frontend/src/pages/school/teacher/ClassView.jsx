import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Users, BarChart3, Plus, CheckCircle2, Calendar } from 'lucide-react'
import { getClassStudents, getClassProgress, createAssignment, getMyClasses } from '../../../api/school'
import { getCurriculum } from '../../../api/curriculum'
import ClassProgressHeatmap from '../../../components/school/ClassProgressHeatmap'
import toast from 'react-hot-toast'

export default function ClassView() {
  const { classId } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [tab, setTab] = useState('students')
  const [showAssign, setShowAssign] = useState(false)
  const [assignForm, setAssignForm] = useState({ lesson_id: '', due_date: '', instructions: '' })

  const { data: students = [] } = useQuery({
    queryKey: ['class-students', classId],
    queryFn: () => getClassStudents(classId),
  })

  const { data: progressData } = useQuery({
    queryKey: ['class-progress', classId],
    queryFn: () => getClassProgress(classId),
    enabled: tab === 'progress',
  })

  const assign = useMutation({
    mutationFn: () => createAssignment({
      class_section_id: parseInt(classId),
      lesson_id: parseInt(assignForm.lesson_id),
      due_date: assignForm.due_date || null,
      instructions: assignForm.instructions || null,
    }),
    onSuccess: () => {
      toast.success('Assignment created!')
      setShowAssign(false)
      setAssignForm({ lesson_id: '', due_date: '', instructions: '' })
    },
    onError: e => toast.error(e.response?.data?.detail || 'Failed'),
  })

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold flex-1">Grade Class View</h1>
          <button
            onClick={() => setShowAssign(true)}
            className="flex items-center gap-1.5 bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium px-3 py-1.5 rounded-lg transition"
          >
            <Plus className="w-4 h-4" /> Assign Lesson
          </button>
        </div>
        {/* Tabs */}
        <div className="max-w-4xl mx-auto px-6 flex gap-1 pb-0">
          {[['students', Users, 'Students'], ['progress', BarChart3, 'Progress']].map(([t, Icon, label]) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
                tab === t ? 'border-teal-400 text-teal-400' : 'border-transparent text-slate-500 hover:text-slate-300'
              }`}
            >
              <Icon className="w-4 h-4" />{label}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-6">
        {tab === 'students' && (
          <div className="space-y-2">
            {students.length === 0 ? (
              <div className="text-center py-12 text-slate-500">
                <Users className="w-10 h-10 mx-auto mb-3 opacity-30" />
                <p>No students enrolled in this class yet</p>
              </div>
            ) : (
              students.map((s, i) => (
                <motion.div
                  key={s.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="flex items-center gap-4 bg-white/5 border border-white/10 rounded-xl px-4 py-3 cursor-pointer hover:border-teal-500/30 transition"
                  onClick={() => navigate(`/school/teacher/student/${s.id}`)}
                >
                  <div className="w-9 h-9 rounded-full bg-teal-500/15 flex items-center justify-center">
                    <span className="text-teal-400 font-bold text-sm">{(s.full_name || s.username)[0].toUpperCase()}</span>
                  </div>
                  <div className="flex-1">
                    <p className="text-white font-medium text-sm">{s.full_name || s.username}</p>
                    <p className="text-xs text-slate-500">@{s.username} · Grade {s.grade}</p>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-slate-600" />
                </motion.div>
              ))
            )}
          </div>
        )}

        {tab === 'progress' && (
          <div>
            <p className="text-sm text-slate-500 mb-4">Each cell shows lesson completion status for each student</p>
            <ClassProgressHeatmap data={progressData} />
          </div>
        )}
      </div>

      {/* Assign lesson modal */}
      {showAssign && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-900 border border-white/15 rounded-2xl p-6 w-full max-w-md"
          >
            <h3 className="text-white font-semibold mb-4">Assign Lesson</h3>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Lesson ID</label>
                <input
                  type="number" placeholder="Enter lesson ID"
                  value={assignForm.lesson_id} onChange={e => setAssignForm(f => ({ ...f, lesson_id: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block flex items-center gap-1"><Calendar className="w-3 h-3" />Due Date (optional)</label>
                <input
                  type="datetime-local"
                  value={assignForm.due_date} onChange={e => setAssignForm(f => ({ ...f, due_date: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>
              <div>
                <label className="text-xs text-slate-400 mb-1 block">Instructions (optional)</label>
                <textarea
                  rows={3} placeholder="Any specific instructions…"
                  value={assignForm.instructions} onChange={e => setAssignForm(f => ({ ...f, instructions: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2.5 text-white text-sm focus:outline-none focus:border-teal-500 resize-none"
                />
              </div>
              <div className="flex gap-3">
                <button onClick={() => setShowAssign(false)} className="flex-1 bg-white/5 hover:bg-white/10 text-slate-300 py-2.5 rounded-lg text-sm transition">Cancel</button>
                <button
                  onClick={() => assign.mutate()}
                  disabled={!assignForm.lesson_id || assign.isPending}
                  className="flex-1 bg-teal-600 hover:bg-teal-500 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg text-sm transition"
                >
                  {assign.isPending ? 'Assigning…' : 'Assign'}
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
