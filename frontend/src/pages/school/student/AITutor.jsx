import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Send, Brain, Loader2, Sparkles, User } from 'lucide-react'
import { askTutor } from '../../../api/curriculum'
import { useAuthStore } from '../../../store/authStore'

const SUGGESTIONS = [
  'What is the difference between AI and a regular computer program?',
  'Can you explain how a neural network learns?',
  'What is overfitting and how do I avoid it?',
  'Explain gradient descent in simple terms',
  'How does Python\'s list differ from a dictionary?',
]

export default function AITutor() {
  const navigate = useNavigate()
  const { fullName, username } = useAuthStore()
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: `Hi ${fullName || username}! I'm your AI tutor 🤖\n\nI'm here to help you understand AI, machine learning, and programming concepts. Ask me anything — I'll guide you through it using questions so you truly understand, not just memorise!\n\nWhat are you curious about today?`,
    model: null,
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const question = text || input.trim()
    if (!question || loading) return
    setInput('')
    setMessages(m => [...m, { role: 'user', content: question }])
    setLoading(true)
    try {
      const res = await askTutor({ question })
      setMessages(m => [...m, { role: 'assistant', content: res.answer, model: res.model_used }])
    } catch (e) {
      setMessages(m => [...m, { role: 'assistant', content: 'Sorry, I had trouble connecting. Please try again!', model: null }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      {/* Header */}
      <div className="bg-slate-950/90 backdrop-blur border-b border-white/10 flex-shrink-0">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
            <Brain className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">AI Tutor</p>
            <p className="text-xs text-slate-500">Socratic mode — I'll help you think, not just answer</p>
          </div>
          <Sparkles className="w-4 h-4 text-indigo-400 ml-auto" />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-2xl mx-auto px-6 py-6 space-y-4">
          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                    <Brain className="w-3.5 h-3.5 text-white" />
                  </div>
                )}
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-white/8 border border-white/10 text-slate-200'} rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap`}>
                  {msg.content}
                  {msg.model && (
                    <p className="text-xs text-slate-500 mt-2 border-t border-white/10 pt-1">{msg.model}</p>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 mt-1">
                    <User className="w-3.5 h-3.5 text-slate-300" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <div className="flex gap-3">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <Brain className="w-3.5 h-3.5 text-white" />
              </div>
              <div className="bg-white/8 border border-white/10 rounded-2xl px-4 py-3">
                <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Suggestions (only when first message) */}
      {messages.length === 1 && (
        <div className="flex-shrink-0 px-6 pb-2 max-w-2xl mx-auto w-full">
          <p className="text-xs text-slate-600 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.slice(0, 3).map(s => (
              <button
                key={s}
                onClick={() => send(s)}
                className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-slate-200 px-3 py-1.5 rounded-full transition"
              >
                {s.length > 50 ? s.slice(0, 50) + '…' : s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 border-t border-white/10 bg-slate-950">
        <div className="max-w-2xl mx-auto px-6 py-4">
          <div className="flex gap-3">
            <input
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), send())}
              placeholder="Ask anything about AI, ML, or coding…"
              className="flex-1 bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 transition"
            />
            <button
              onClick={() => send()}
              disabled={!input.trim() || loading}
              className="w-11 h-11 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 rounded-xl flex items-center justify-center transition flex-shrink-0"
            >
              <Send className="w-4 h-4 text-white" />
            </button>
          </div>
          <p className="text-xs text-slate-600 mt-2 text-center">Only AI, ML & coding questions — other topics are outside my expertise</p>
        </div>
      </div>
    </div>
  )
}
