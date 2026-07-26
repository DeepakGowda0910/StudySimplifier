import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, GraduationCap, Trash2 } from 'lucide-react'
import { listTeachers, removeTeacher } from '../../../api/school'
import toast from 'react-hot-toast'

export default function ManageTeachers() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: teachers = [], isLoading } = useQuery({ queryKey: ['teachers'], queryFn: listTeachers })

  const remove = useMutation({
    mutationFn: (id) => removeTeacher(id),
    onSuccess: () => { qc.invalidateQueries(['teachers']); toast.success('Teacher removed') },
    onError: e => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const confirmRemove = (teacher) => {
    if (window.confirm(`Remove ${teacher.full_name || teacher.username}? They will lose access to the school.`)) {
      remove.mutate(teacher.id)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold flex-1">Teachers ({teachers.length})</h1>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6">
        {isLoading ? (
          <div className="space-y-2">{[...Array(4)].map((_, i) => <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : teachers.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <GraduationCap className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No teachers yet</p>
            <p className="text-xs mt-1">Generate a teacher invite code from the Admin Dashboard to add teachers</p>
          </div>
        ) : (
          <div className="space-y-2">
            {teachers.map((t, i) => (
              <motion.div
                key={t.id}
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }}
                className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl px-4 py-3"
              >
                <div className="w-9 h-9 rounded-full bg-teal-500/15 flex items-center justify-center flex-shrink-0">
                  <span className="text-teal-400 font-bold">{(t.full_name || t.username)[0].toUpperCase()}</span>
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium">{t.full_name || t.username}</p>
                  <p className="text-xs text-slate-500">@{t.username}{t.email ? ` · ${t.email}` : ''}</p>
                </div>
                <button
                  onClick={() => confirmRemove(t)}
                  disabled={remove.isPending}
                  className="text-slate-600 hover:text-red-400 transition p-1.5 rounded-lg hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
