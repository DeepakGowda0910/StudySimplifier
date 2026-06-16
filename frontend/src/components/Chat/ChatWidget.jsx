import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import ReactMarkdown from 'react-markdown'
import { MessageCircle, X, Send, Trash2, Bot, User, HelpCircle, MessageSquare } from 'lucide-react'
import { chat } from '../../api/study'

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [socratic, setSocratic] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\'m StudyBot 🤖 Your personal AI tutor. Ask me anything about your subjects!' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const sendMessage = async () => {
    const msg = input.trim()
    if (!msg || loading) return
    setInput('')
    const userMsg = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)
    try {
      const history = messages.filter(m => m.role !== 'system').slice(-10)
      const data = await chat({ message: msg, history, socratic_mode: socratic })
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I ran into an error. Please try again!' }])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: socratic
        ? 'Socratic mode activated! 🧠 I\'ll guide you with questions instead of giving direct answers. What would you like to explore?'
        : 'Chat cleared! What would you like to study?'
    }])
  }

  const toggleSocratic = () => {
    const next = !socratic
    setSocratic(next)
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: next
        ? '🧠 **Socratic mode ON** — I\'ll now guide you with questions instead of direct answers. Great for deep learning!'
        : '💬 **Normal mode ON** — Back to direct answers. Ask away!'
    }])
  }

  return (
    <>
      <motion.button
        onClick={() => setOpen(o => !o)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-600 to-violet-700 text-white shadow-xl flex items-center justify-center z-50"
      >
        <AnimatePresence mode="wait">
          {open
            ? <motion.div key="close" initial={{ scale: 0, rotate: -90 }} animate={{ scale: 1, rotate: 0 }} exit={{ scale: 0 }}><X size={22} /></motion.div>
            : <motion.div key="open" initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}><MessageCircle size={22} /></motion.div>
          }
        </AnimatePresence>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed bottom-24 right-6 w-80 sm:w-96 h-[520px] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-800 flex flex-col z-50 overflow-hidden"
          >
            {/* Header */}
            <div className={`flex items-center gap-3 p-4 border-b border-slate-100 dark:border-slate-800 rounded-t-2xl text-white transition-colors ${socratic ? 'bg-gradient-to-r from-violet-700 to-purple-800' : 'bg-gradient-to-r from-blue-600 to-violet-700'}`}>
              <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                {socratic ? <HelpCircle size={18} /> : <Bot size={18} />}
              </div>
              <div className="flex-1">
                <p className="font-semibold text-sm">{socratic ? 'Socratic Tutor' : 'StudyBot'}</p>
                <p className={`text-xs ${socratic ? 'text-purple-200' : 'text-blue-200'}`}>
                  {socratic ? 'Guides with questions' : 'AI Tutor • Always here'}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={toggleSocratic}
                  title={socratic ? 'Switch to normal mode' : 'Switch to Socratic mode'}
                  className={`p-1.5 rounded-lg transition-colors ${socratic ? 'bg-white/30' : 'hover:bg-white/20'}`}
                >
                  {socratic ? <MessageSquare size={14} /> : <HelpCircle size={14} />}
                </button>
                <button onClick={clearChat} className="p-1.5 hover:bg-white/20 rounded-lg transition-colors" title="Clear chat">
                  <Trash2 size={14} />
                </button>
              </div>
            </div>

            {/* Mode badge */}
            {socratic && (
              <div className="px-4 py-2 bg-violet-50 dark:bg-violet-950/40 text-xs text-violet-700 dark:text-violet-300 font-medium border-b border-violet-100 dark:border-violet-900">
                🧠 Socratic mode: I'll ask guiding questions to help you discover answers yourself
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((m, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-2 ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${m.role === 'user' ? 'bg-blue-500' : socratic ? 'bg-gradient-to-br from-violet-700 to-purple-800' : 'bg-gradient-to-br from-violet-500 to-blue-600'}`}>
                    {m.role === 'user' ? <User size={14} className="text-white" /> : socratic ? <HelpCircle size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
                  </div>
                  <div className={`max-w-[75%] rounded-2xl px-3 py-2.5 text-sm leading-relaxed ${
                    m.role === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-sm'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-sm'
                  }`}>
                    {m.role === 'assistant' ? (
                      <div className="md-content text-inherit [&_p]:mb-1 [&_p:last-child]:mb-0 [&_ul]:mb-1 [&_li]:mb-0">
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                      </div>
                    ) : m.content}
                  </div>
                </motion.div>
              ))}
              {loading && (
                <div className="flex gap-2">
                  <div className={`w-7 h-7 rounded-full flex items-center justify-center ${socratic ? 'bg-gradient-to-br from-violet-700 to-purple-800' : 'bg-gradient-to-br from-violet-500 to-blue-600'}`}>
                    {socratic ? <HelpCircle size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
                    {[0, 0.15, 0.3].map((d, i) => (
                      <motion.div key={i} className="w-2 h-2 bg-slate-400 rounded-full"
                        animate={{ y: [0, -6, 0] }} transition={{ duration: 0.7, delay: d, repeat: Infinity }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-t border-slate-100 dark:border-slate-800">
              <div className="flex gap-2">
                <input
                  className="input text-sm flex-1 py-2"
                  placeholder={socratic ? 'Ask a question to explore…' : 'Ask anything…'}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                />
                <button onClick={sendMessage} disabled={!input.trim() || loading}
                  className={`p-2.5 rounded-xl shrink-0 text-white transition-colors ${socratic ? 'bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300' : 'btn-primary'}`}>
                  <Send size={16} />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
