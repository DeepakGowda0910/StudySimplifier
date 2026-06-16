import React, { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { Plus, Trash2, Pin, Search, Wand2, Save, X, FileText } from 'lucide-react'
import { getNotes, createNote, updateNote, deleteNote, enhanceNote } from '../api/notes'

const COLORS = ['blue', 'violet', 'emerald', 'amber', 'rose', 'orange']
const COLOR_MAP = {
  blue: 'bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800',
  violet: 'bg-violet-50 dark:bg-violet-950 border-violet-200 dark:border-violet-800',
  emerald: 'bg-emerald-50 dark:bg-emerald-950 border-emerald-200 dark:border-emerald-800',
  amber: 'bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800',
  rose: 'bg-rose-50 dark:bg-rose-950 border-rose-200 dark:border-rose-800',
  orange: 'bg-orange-50 dark:bg-orange-950 border-orange-200 dark:border-orange-800',
}
const DOT_MAP = {
  blue: 'bg-blue-400', violet: 'bg-violet-400', emerald: 'bg-emerald-400',
  amber: 'bg-amber-400', rose: 'bg-rose-400', orange: 'bg-orange-400',
}

const ENHANCE_ACTIONS = [
  { id: 'improve', label: '✨ Improve' },
  { id: 'expand', label: '📖 Expand' },
  { id: 'summary', label: '📋 Summarize' },
  { id: 'questions', label: '❓ Questions' },
  { id: 'flashcards', label: '🃏 Flashcards' },
]

const EMPTY_FORM = { title: '', content: '', subject: '', chapter: '', color: 'blue', tags: '' }

function NoteForm({ note, onSave, onCancel, onEnhance, enhancing, enhancedContent, onUseEnhanced }) {
  const [local, setLocal] = useState(note || EMPTY_FORM)

  useEffect(() => {
    setLocal(note || EMPTY_FORM)
  }, [note])

  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-slate-900 dark:text-white">{note ? 'Edit Note' : 'New Note'}</h3>
        <button onClick={onCancel} className="btn-ghost p-1"><X size={18} /></button>
      </div>
      <div>
        <label className="label">Title</label>
        <input className="input text-sm" placeholder="Note title…" value={local.title} onChange={e => setLocal(f => ({ ...f, title: e.target.value }))} autoFocus />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Subject</label>
          <input className="input text-sm" placeholder="Subject" value={local.subject || ''} onChange={e => setLocal(f => ({ ...f, subject: e.target.value }))} />
        </div>
        <div>
          <label className="label">Chapter</label>
          <input className="input text-sm" placeholder="Chapter" value={local.chapter || ''} onChange={e => setLocal(f => ({ ...f, chapter: e.target.value }))} />
        </div>
      </div>
      <div>
        <label className="label">Content</label>
        <textarea className="input text-sm resize-none" rows={8} placeholder="Write your notes here…" value={local.content || ''} onChange={e => setLocal(f => ({ ...f, content: e.target.value }))} />
      </div>
      <div>
        <label className="label">Color</label>
        <div className="flex gap-2">
          {COLORS.map(c => (
            <button key={c} type="button" onClick={() => setLocal(f => ({ ...f, color: c }))}
              className={`w-7 h-7 rounded-full ${DOT_MAP[c]} border-2 transition-all ${local.color === c ? 'border-slate-900 dark:border-white scale-110' : 'border-transparent'}`} />
          ))}
        </div>
      </div>

      {note && (
        <div>
          <p className="label">AI Enhance</p>
          <div className="flex flex-wrap gap-2">
            {ENHANCE_ACTIONS.map(a => (
              <button key={a.id} type="button" onClick={() => onEnhance(note.id, a.id)} disabled={enhancing}
                className="btn-secondary text-xs py-1.5 px-3">{a.label}</button>
            ))}
          </div>
          {enhancing && (
            <div className="flex items-center gap-2 mt-2 text-sm text-slate-500">
              <div className="w-4 h-4 border-2 border-blue-200 border-t-blue-500 rounded-full animate-spin" /> Enhancing…
            </div>
          )}
          {enhancedContent && (
            <div className="mt-3 bg-blue-50 dark:bg-blue-950 rounded-xl p-4 text-sm text-slate-700 dark:text-slate-300 max-h-48 overflow-y-auto whitespace-pre-wrap">
              {enhancedContent}
              <button type="button" onClick={() => { setLocal(f => ({ ...f, content: enhancedContent })); onUseEnhanced() }} className="btn-primary text-xs mt-2 block">
                Use this content
              </button>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2">
        <button type="button" onClick={() => onSave(local)} disabled={!local.title} className="btn-primary flex items-center gap-2">
          <Save size={15} /> Save Note
        </button>
        <button type="button" onClick={onCancel} className="btn-secondary">Cancel</button>
      </div>
    </div>
  )
}

function NoteCard({ note, onEdit, onDelete, onPin }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      className={`card border-2 ${COLOR_MAP[note.color] || COLOR_MAP.blue} cursor-pointer group`}
      onClick={onEdit}
    >
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <p className="font-semibold text-slate-900 dark:text-white text-sm truncate pr-2">{note.title}</p>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" onClick={e => e.stopPropagation()}>
            <button type="button" onClick={onPin} className="btn-ghost p-1 text-xs">
              <Pin size={14} className={note.is_pinned ? 'fill-current text-blue-500' : ''} />
            </button>
            <button type="button" onClick={onDelete} className="btn-ghost p-1 text-red-400">
              <Trash2 size={14} />
            </button>
          </div>
        </div>
        {note.subject && <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">{note.subject}{note.chapter ? ` · ${note.chapter}` : ''}</p>}
        <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-4 leading-relaxed">{note.content || 'Empty note'}</p>
        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-black/5 dark:border-white/5">
          <span className="text-xs text-slate-400">{note.word_count} words</span>
          <span className="text-xs text-slate-400 ml-auto">{new Date(note.updated_at || note.created_at).toLocaleDateString()}</span>
        </div>
      </div>
    </motion.div>
  )
}

export default function Notes() {
  const [editing, setEditing] = useState(null)
  const [creating, setCreating] = useState(false)
  const [search, setSearch] = useState('')
  const [enhancing, setEnhancing] = useState(false)
  const [enhancedContent, setEnhancedContent] = useState('')
  const qc = useQueryClient()

  const { data: notes = [], isLoading } = useQuery({ queryKey: ['notes'], queryFn: getNotes })

  const createMut = useMutation({
    mutationFn: createNote,
    onSuccess: () => {
      toast.success('Note saved!')
      setCreating(false)
      qc.invalidateQueries(['notes'])
    }
  })
  const updateMut = useMutation({
    mutationFn: ({ id, data }) => updateNote(id, data),
    onSuccess: () => { toast.success('Note updated!'); setEditing(null); setEnhancedContent(''); qc.invalidateQueries(['notes']) }
  })
  const deleteMut = useMutation({
    mutationFn: deleteNote,
    onSuccess: () => { toast.success('Note deleted'); qc.invalidateQueries(['notes']) }
  })
  const pinMut = useMutation({
    mutationFn: ({ id, pinned }) => updateNote(id, { is_pinned: !pinned }),
    onSuccess: () => qc.invalidateQueries(['notes'])
  })

  const handleEnhance = async (noteId, action) => {
    setEnhancing(true)
    try {
      const data = await enhanceNote(noteId, action)
      setEnhancedContent(data.enhanced_content)
      toast.success('AI enhancement ready!')
    } catch { toast.error('Enhancement failed') }
    finally { setEnhancing(false) }
  }

  const filtered = notes.filter(n =>
    n.title.toLowerCase().includes(search.toLowerCase()) ||
    (n.content || '').toLowerCase().includes(search.toLowerCase()) ||
    (n.subject || '').toLowerCase().includes(search.toLowerCase())
  )

  const pinned = filtered.filter(n => n.is_pinned)
  const unpinned = filtered.filter(n => !n.is_pinned)

  return (
    <div className="page-container space-y-4">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input className="input pl-9 text-sm" placeholder="Search notes…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <button onClick={() => setCreating(true)} className="btn-primary flex items-center gap-2 shrink-0">
          <Plus size={16} /> New Note
        </button>
      </div>

      <AnimatePresence>
        {creating && (
          <motion.div key="create-form" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <NoteForm
              onSave={(data) => createMut.mutate(data)}
              onCancel={() => setCreating(false)}
              onEnhance={handleEnhance}
              enhancing={enhancing}
              enhancedContent={enhancedContent}
              onUseEnhanced={() => setEnhancedContent('')}
            />
          </motion.div>
        )}
        {editing && (
          <motion.div key="edit-form" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            <NoteForm
              note={editing}
              onSave={(data) => updateMut.mutate({ id: editing.id, data })}
              onCancel={() => { setEditing(null); setEnhancedContent('') }}
              onEnhance={handleEnhance}
              enhancing={enhancing}
              enhancedContent={enhancedContent}
              onUseEnhanced={() => setEnhancedContent('')}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="card h-40 shimmer" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <FileText size={40} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
          <p className="font-semibold text-slate-600 dark:text-slate-400">No notes yet</p>
          <p className="text-sm text-slate-400 mt-1">Create your first note to get started</p>
        </div>
      ) : (
        <>
          {pinned.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">📌 Pinned</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {pinned.map(n => (
                  <NoteCard key={n.id} note={n}
                    onEdit={() => setEditing(n)}
                    onDelete={() => deleteMut.mutate(n.id)}
                    onPin={() => pinMut.mutate({ id: n.id, pinned: n.is_pinned })}
                  />
                ))}
              </div>
            </div>
          )}
          {unpinned.length > 0 && (
            <div>
              {pinned.length > 0 && <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 mt-4">All Notes</p>}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {unpinned.map(n => (
                  <NoteCard key={n.id} note={n}
                    onEdit={() => setEditing(n)}
                    onDelete={() => deleteMut.mutate(n.id)}
                    onPin={() => pinMut.mutate({ id: n.id, pinned: n.is_pinned })}
                  />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
