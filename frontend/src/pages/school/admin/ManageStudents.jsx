import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, Users, Search, Filter } from 'lucide-react'
import { listStudents } from '../../../api/school'

export default function ManageStudents() {
  const navigate = useNavigate()
  const [gradeFilter, setGradeFilter] = useState('')
  const [search, setSearch] = useState('')

  const { data: students = [], isLoading } = useQuery({
    queryKey: ['students', gradeFilter],
    queryFn: () => listStudents(gradeFilter || null),
  })

  const filtered = students.filter(s =>
    !search || (s.full_name || s.username).toLowerCase().includes(search.toLowerCase())
  )

  // Group by grade
  const byGrade = {}
  filtered.forEach(s => {
    if (!byGrade[s.grade]) byGrade[s.grade] = []
    byGrade[s.grade].push(s)
  })

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold flex-1">Students ({students.length})</h1>
        </div>
        {/* Filters */}
        <div className="max-w-4xl mx-auto px-6 pb-4 flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              value={search} onChange={e => setSearch(e.target.value)}
              placeholder="Search by name…"
              className="w-full bg-white/5 border border-white/15 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <select
            value={gradeFilter} onChange={e => setGradeFilter(e.target.value)}
            className="bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="" className="bg-slate-800">All Grades</option>
            {[6,7,8,9,10,11,12].map(g => <option key={g} value={g} className="bg-slate-800">Grade {g}</option>)}
          </select>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-6 space-y-6">
        {isLoading ? (
          <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-14 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <Users className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No students found</p>
          </div>
        ) : (
          Object.entries(byGrade).sort(([a],[b]) => Number(a)-Number(b)).map(([grade, gradeStudents]) => (
            <div key={grade}>
              <h3 className="text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-indigo-500/15 text-indigo-400 text-xs flex items-center justify-center font-bold">{grade}</span>
                Grade {grade} · {gradeStudents.length} student{gradeStudents.length !== 1 ? 's' : ''}
              </h3>
              <div className="space-y-1.5">
                {gradeStudents.map((s, i) => (
                  <motion.div
                    key={s.id}
                    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.02 }}
                    className="flex items-center gap-3 bg-white/3 border border-white/5 rounded-lg px-4 py-3"
                  >
                    <div className="w-8 h-8 rounded-full bg-indigo-500/15 flex items-center justify-center flex-shrink-0">
                      <span className="text-indigo-400 text-sm font-bold">{(s.full_name || s.username)[0].toUpperCase()}</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-white">{s.full_name || s.username}</p>
                      <p className="text-xs text-slate-500">@{s.username}{s.email ? ` · ${s.email}` : ''}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
