import React, { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { Check } from 'lucide-react'
import { getProfile, updateProfile } from '../api/user'
import { getCategories, getCourses, getStreams } from '../api/study'

const BOARDS = ['CBSE', 'ICSE', 'State Board', 'ISC', 'IB', 'Cambridge', 'General']

export default function Settings() {
  const queryClient = useQueryClient()
  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile })

  const [category, setCategory] = useState('')
  const [course, setCourse] = useState('')
  const [stream, setStream] = useState('')
  const [board, setBoard] = useState('')
  const [categories, setCategories] = useState([])
  const [courses, setCourses] = useState([])
  const [streams, setStreams] = useState([])
  const [saving, setSaving] = useState(false)

  // Seed local state from the saved profile once it loads
  useEffect(() => {
    if (profile) {
      setCategory(profile.category || '')
      setCourse(profile.course || '')
      setStream(profile.stream || '')
      setBoard(profile.board || '')
    }
  }, [profile])

  useEffect(() => { getCategories().then(setCategories).catch(() => {}) }, [])

  useEffect(() => {
    if (!category) { setCourses([]); return }
    getCourses(category).then(setCourses).catch(() => setCourses([]))
  }, [category])

  useEffect(() => {
    if (!category || !course) { setStreams([]); return }
    getStreams(category, course).then(setStreams).catch(() => setStreams([]))
  }, [category, course])

  const handleCategoryChange = (value) => {
    setCategory(value)
    setCourse('')
    setStream('')
  }

  const handleCourseChange = (value) => {
    setCourse(value)
    setStream('')
  }

  const isDirty = profile && (
    category !== (profile.category || '') ||
    course !== (profile.course || '') ||
    stream !== (profile.stream || '') ||
    board !== (profile.board || '')
  )

  const handleSave = async () => {
    if (!category || !course) return toast.error('Please select a category and course')
    setSaving(true)
    try {
      await updateProfile({ category, course, stream: stream || 'General', board: board || 'General' })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      toast.success('Study profile updated!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Switch your course, grade, or stream at any time — your progress stays intact.</p>
      </div>

      <div className="card p-6 space-y-5">
        <h2 className="font-semibold text-slate-900 dark:text-white">Study Profile</h2>

        <div>
          <label className="label">Education Category</label>
          <select className="input text-sm" value={category} onChange={e => handleCategoryChange(e.target.value)}>
            <option value="">Select category</option>
            {categories.map(c => <option key={c}>{c}</option>)}
          </select>
        </div>

        <div>
          <label className="label">Course / Grade</label>
          <select className="input text-sm" value={course} onChange={e => handleCourseChange(e.target.value)} disabled={!category}>
            <option value="">Select course</option>
            {courses.map(c => <option key={c}>{c}</option>)}
          </select>
        </div>

        {streams.length > 0 && (
          <div>
            <label className="label">Stream</label>
            <select className="input text-sm" value={stream} onChange={e => setStream(e.target.value)}>
              <option value="">Select stream</option>
              {streams.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
        )}

        <div>
          <label className="label">Board / Curriculum</label>
          <div className="flex flex-wrap gap-2">
            {BOARDS.map(b => (
              <button key={b} onClick={() => setBoard(b)} type="button"
                className={`px-3 py-1.5 rounded-lg border text-sm font-medium transition-all ${board === b ? 'border-navy-500 bg-navy-50 dark:bg-navy-800 text-navy-700 dark:text-navy-300' : 'border-slate-200 dark:border-navy-700 text-slate-600 dark:text-slate-400 hover:border-navy-300'}`}>
                {b}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-2 border-t border-slate-100 dark:border-navy-700">
          <button onClick={handleSave} disabled={saving || !isDirty} className="btn-primary flex items-center gap-2 disabled:opacity-50">
            {saving ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Check size={16} />}
            Save Changes
          </button>
          {!isDirty && profile && <p className="text-xs text-slate-400 dark:text-slate-500 mt-2">No changes to save yet.</p>}
        </div>
      </div>
    </div>
  )
}
