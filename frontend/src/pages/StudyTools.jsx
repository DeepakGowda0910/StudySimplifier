import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Zap, FileText, BookOpen, AlignLeft, Bookmark, Brain, HelpCircle, FileQuestion, Upload, Download, Copy, Check } from 'lucide-react'
import { getProfile } from '../api/user'
import { getSubjects, getTopics, getChapters, generate, uploadDocument } from '../api/study'
import QuizModal from '../components/Quiz/QuizModal'

const TOOLS = [
  { id: 'short', label: 'Quick Notes', icon: Zap, color: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400', desc: 'Last-minute revision' },
  { id: 'summary', label: 'Summary', icon: FileText, color: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400', desc: 'Academic overview' },
  { id: 'notes', label: 'Notes', icon: AlignLeft, color: 'bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-400', desc: 'Organized notes' },
  { id: 'detailed', label: 'Detailed', icon: BookOpen, color: 'bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-400', desc: 'In-depth guide' },
  { id: 'revision', label: 'Revision', icon: Bookmark, color: 'bg-pink-100 text-pink-700 dark:bg-pink-950 dark:text-pink-400', desc: 'Exam focused' },
  { id: 'quiz', label: 'Quiz', icon: Brain, color: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400', desc: 'Self-assessment' },
  { id: 'qa', label: 'Q&A', icon: HelpCircle, color: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400', desc: 'Question bank' },
  { id: 'paper', label: 'Question Paper', icon: FileQuestion, color: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400', desc: 'Full exam paper' },
  { id: 'upload', label: 'Upload Doc', icon: Upload, color: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300', desc: 'Analyze document' },
]

const LANGUAGES = ['English', 'Hindi', 'Tamil', 'Telugu', 'Kannada', 'Malayalam', 'Bengali', 'Marathi', 'Gujarati', 'Spanish', 'French', 'German']

export default function StudyTools() {
  const [tool, setTool] = useState('summary')
  const [subject, setSubject] = useState('')
  const [topic, setTopic] = useState('')
  const [chapter, setChapter] = useState('')
  const [language, setLanguage] = useState('English')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [file, setFile] = useState(null)
  const [docAction, setDocAction] = useState('summary')
  const [showQuiz, setShowQuiz] = useState(false)

  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile })
  const { data: subjects = [] } = useQuery({
    queryKey: ['subjects', profile?.category, profile?.course, profile?.stream],
    queryFn: () => getSubjects(profile.category, profile.course, profile.stream || 'General'),
    enabled: !!profile?.category && !!profile?.course,
  })
  const { data: topics = [] } = useQuery({
    queryKey: ['topics', subject],
    queryFn: () => getTopics(profile.category, profile.course, profile.stream || 'General', subject),
    enabled: !!subject && !!profile,
  })
  const { data: chapters = [] } = useQuery({
    queryKey: ['chapters', topic],
    queryFn: () => getChapters(profile.category, profile.course, profile.stream || 'General', subject, topic),
    enabled: !!topic && !!profile,
  })

  const handleGenerate = async () => {
    if (!chapter) return toast.error('Please select a chapter')
    setLoading(true); setResult('')
    try {
      const data = await generate({ tool, chapter, topic, subject, language, course: profile?.course, board: profile?.board, stream: profile?.stream })
      setResult(data.content)
      toast.success(`+${data.xp_awarded} XP earned!`)
    } catch { toast.error('Generation failed. Check your API key.') }
    finally { setLoading(false) }
  }

  const handleUpload = async () => {
    if (!file) return toast.error('Select a file first')
    setLoading(true); setResult('')
    const fd = new FormData()
    fd.append('file', file)
    fd.append('action', docAction)
    fd.append('language', language)
    try {
      const data = await uploadDocument(fd)
      setResult(data.content)
      toast.success('Document analyzed!')
    } catch { toast.error('Upload failed') }
    finally { setLoading(false) }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(result)
    setCopied(true); setTimeout(() => setCopied(false), 2000)
    toast.success('Copied to clipboard!')
  }

  const downloadMd = () => {
    const blob = new Blob([result], { type: 'text/markdown' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${chapter || 'study-notes'}.md`
    a.click()
  }

  return (
    <div className="page-container">
      <AnimatePresence>
        {showQuiz && subject && chapter && result && (
          <QuizModal
            subject={subject}
            chapter={chapter}
            contentSnippet={result.slice(0, 3000)}
            onClose={() => setShowQuiz(false)}
          />
        )}
      </AnimatePresence>
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Left panel */}
        <div className="w-full lg:w-72 shrink-0 space-y-4">
          {/* Tool selector */}
          <div className="card p-4">
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">Select Tool</p>
            <div className="space-y-1">
              {TOOLS.map(t => (
                <button key={t.id} onClick={() => { setTool(t.id); setResult('') }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${tool === t.id ? 'bg-navy-50 dark:bg-navy-700 border border-navy-200 dark:border-navy-600' : 'hover:bg-slate-50 dark:hover:bg-navy-800'}`}>
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${t.color}`}>
                    <t.icon size={16} />
                  </div>
                  <div className="min-w-0">
                    <p className={`text-sm font-medium ${tool === t.id ? 'text-navy-700 dark:text-white' : 'text-slate-700 dark:text-slate-300'}`}>{t.label}</p>
                    <p className="text-xs text-slate-400 dark:text-slate-500">{t.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Language */}
          <div className="card p-4">
            <label className="label">Output Language</label>
            <select className="input text-sm" value={language} onChange={e => setLanguage(e.target.value)}>
              {LANGUAGES.map(l => <option key={l}>{l}</option>)}
            </select>
          </div>
        </div>

        {/* Right panel */}
        <div className="flex-1 space-y-4">
          {tool === 'upload' ? (
            <div className="card p-6 space-y-4">
              <h3 className="font-semibold text-slate-900 dark:text-white">Upload & Analyze Document</h3>
              <div className="border-2 border-dashed border-slate-200 dark:border-navy-600 rounded-xl p-8 text-center">
                <Upload size={32} className="mx-auto text-slate-400 mb-3" />
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Drop a PDF or DOCX file here</p>
                <input type="file" accept=".pdf,.docx,.txt" onChange={e => setFile(e.target.files[0])} className="hidden" id="file-upload" />
                <label htmlFor="file-upload" className="btn-secondary cursor-pointer inline-flex">Browse Files</label>
                {file && <p className="mt-2 text-sm text-navy-600 dark:text-navy-300 font-medium">{file.name}</p>}
              </div>
              <div>
                <label className="label">Analyze As</label>
                <select className="input text-sm" value={docAction} onChange={e => setDocAction(e.target.value)}>
                  {['summary', 'flashcards', 'quiz', 'notes', 'mindmap'].map(a => <option key={a} value={a}>{a.charAt(0).toUpperCase() + a.slice(1)}</option>)}
                </select>
              </div>
              <button onClick={handleUpload} disabled={loading || !file} className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Analyzing…</> : <><Upload size={16} /> Analyze Document</>}
              </button>
            </div>
          ) : (
            <div className="card p-6 space-y-4">
              <h3 className="font-semibold text-slate-900 dark:text-white">Configure</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="label">Subject</label>
                  <select className="input text-sm" value={subject} onChange={e => { setSubject(e.target.value); setTopic(''); setChapter('') }}>
                    <option value="">Select subject</option>
                    {subjects.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Topic</label>
                  <select className="input text-sm" value={topic} onChange={e => { setTopic(e.target.value); setChapter('') }} disabled={!subject}>
                    <option value="">Select topic</option>
                    {topics.map(t => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Chapter</label>
                  <select className="input text-sm" value={chapter} onChange={e => setChapter(e.target.value)} disabled={!topic}>
                    <option value="">Select chapter</option>
                    {chapters.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input className="input text-sm flex-1" placeholder="Or type a chapter name manually…" value={chapter} onChange={e => setChapter(e.target.value)} />
              </div>
              <button onClick={handleGenerate} disabled={loading || !chapter} className="btn-primary flex items-center gap-2">
                {loading ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating…</> : <><Zap size={16} /> Generate</>}
              </button>
            </div>
          )}

          {/* Result */}
          <AnimatePresence>
            {result && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-slate-900 dark:text-white">Result</h3>
                  <div className="flex items-center gap-2">
                    <button onClick={copyToClipboard} className="btn-ghost text-xs flex items-center gap-1.5 py-1.5">
                      {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                    <button onClick={downloadMd} className="btn-ghost text-xs flex items-center gap-1.5 py-1.5">
                      <Download size={14} /> Download
                    </button>
                  </div>
                </div>
                <div className="md-content text-slate-700 dark:text-slate-300">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{result}</ReactMarkdown>
                </div>
                {subject && chapter && !['upload', 'paper'].includes(tool) && (
                  <div className="mt-5 pt-5 border-t border-slate-100 dark:border-navy-700">
                    <button onClick={() => setShowQuiz(true)} className="btn-primary w-full flex items-center justify-center gap-2">
                      <Brain size={16} /> Start Quiz on This Content
                    </button>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {loading && (
            <div className="card p-12 flex flex-col items-center justify-center gap-4">
              <div className="w-12 h-12 border-4 border-navy-200 border-t-navy-600 rounded-full animate-spin" />
              <p className="text-slate-500 dark:text-slate-400 text-sm">AI is generating your content…</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
