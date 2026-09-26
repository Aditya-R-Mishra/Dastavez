import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import {
  Send,
  FileText,
  ChevronDown,
  Sparkles,
  Bot,
  User,
  Plus,
  MessageSquare,
  Mic,
  MicOff,
  Globe2,
  Trash2,
  Filter,
} from 'lucide-react'
import toast from 'react-hot-toast'
import Logo from '../components/Logo'
import api from '../lib/api'

// ── Conversations sidebar ─────────────────────────────────────────────────────
const ConvSidebar = ({ conversations, activeId, onSelect, onNew, onDelete }) => (
  <aside className="flex flex-col w-64 shrink-0 bg-navy-900 border-r border-navy-700 h-full">
    {/* New chat button */}
    <div className="p-3 border-b border-navy-700">
      <button
        onClick={onNew}
        className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg
          bg-gradient-to-r from-brand-500 to-cyan-500 hover:from-brand-400 hover:to-cyan-400
          text-white text-sm font-medium transition-all duration-200 cursor-pointer
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400 shadow-md shadow-brand-500/20"
      >
        <Plus size={16} />
        New Chat
      </button>
    </div>

    {/* Conversation list */}
    <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-0.5">
      <p className="text-xs text-gray-500 font-semibold uppercase tracking-widest px-2 py-1.5">
        Conversations
      </p>
      {conversations.length === 0 ? (
        <p className="text-xs text-gray-500 px-3 py-4 text-center">No chat history yet</p>
      ) : (
        conversations.map((conv) => {
          const isActive = conv.id === activeId
          return (
            <div
              key={conv.id}
              className={[
                'group w-full flex items-center justify-between px-3 py-2.5 rounded-lg transition-all duration-200 cursor-pointer',
                isActive
                  ? 'bg-brand-500/15 border border-brand-500/30'
                  : 'border border-transparent hover:bg-navy-800 hover:border-navy-700',
              ].join(' ')}
              onClick={() => onSelect(conv.id)}
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                <MessageSquare
                  size={14}
                  className={`shrink-0 ${isActive ? 'text-brand-400' : 'text-gray-500'}`}
                />
                <span
                  className={`text-sm truncate ${
                    isActive ? 'text-brand-400 font-medium' : 'text-gray-300'
                  }`}
                >
                  {conv.title || 'Untitled Chat'}
                </span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(conv.id)
                }}
                title="Delete thread"
                className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 rounded transition-opacity"
              >
                <Trash2 size={12} />
              </button>
            </div>
          )
        })
      )}
    </nav>
  </aside>
)

// ── Confidence badge config ───────────────────────────────────────────────────
const CONFIDENCE_MAP = {
  supported: {
    label: 'Well Supported',
    cls: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  },
  conflicting: {
    label: 'Conflicting Sources',
    cls: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
  },
  insufficient: {
    label: 'Insufficient Evidence',
    cls: 'bg-red-500/15 text-red-400 border-red-500/30',
  },
}

// ── Source accordion card ─────────────────────────────────────────────────────
const SourceCard = ({ source }) => {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-navy-700 rounded-lg overflow-hidden text-xs">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 bg-navy-800
          hover:bg-navy-700 transition-colors text-left cursor-pointer"
      >
        <div className="flex items-center gap-2 min-w-0">
          <FileText size={12} className="text-brand-400 shrink-0" />
          <span className="text-gray-300 font-medium truncate">{source.file}</span>
          <span className="text-gray-500 shrink-0">p.{source.page}</span>
          {source.section && (
            <span className="text-gray-500 shrink-0 hidden sm:inline">· {source.section}</span>
          )}
        </div>
        <motion.div
          animate={{ rotate: open ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="shrink-0"
        >
          <ChevronDown size={13} className="text-gray-400" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <p className="px-3 py-2.5 text-gray-400 leading-relaxed border-t border-navy-700 bg-navy-950/60 italic">
              "{source.snippet || `Source verification chunk on Page ${source.page}`}"
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── Typing indicator ──────────────────────────────────────────────────────────
const TypingIndicator = () => (
  <div className="flex items-end gap-3 mb-6">
    <div className="w-7 h-7 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center shrink-0">
      <Bot size={13} className="text-brand-400" />
    </div>
    <div className="bg-navy-800 border border-navy-700 rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-1.5">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="w-1.5 h-1.5 rounded-full bg-gray-500"
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
        />
      ))}
    </div>
  </div>
)

// ── AI message bubble ─────────────────────────────────────────────────────────
const AIBubble = ({ msg }) => {
  const conf = CONFIDENCE_MAP[msg.confidence] ?? CONFIDENCE_MAP.supported
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="flex items-end gap-3 mb-6"
    >
      <div className="w-7 h-7 rounded-full bg-brand-500/20 border border-brand-500/30 flex items-center justify-center shrink-0 mb-0.5">
        <Bot size={13} className="text-brand-400" />
      </div>

      <div className="flex flex-col gap-2 max-w-[80%]">
        <div className="bg-navy-800 border border-navy-700 rounded-2xl rounded-bl-sm px-4 py-3 text-gray-200 text-sm leading-relaxed prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{msg.text}</ReactMarkdown>
        </div>

        {/* Confidence badge */}
        <span
          className={`self-start inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${conf.cls}`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70" />
          {conf.label}
        </span>

        {/* Sources */}
        {msg.sources?.length > 0 && (
          <div className="flex flex-col gap-1.5 mt-1">
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
              Verified Sources ({msg.sources.length})
            </p>
            {msg.sources.map((src, idx) => (
              <SourceCard key={src.id || idx} source={src} />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}

// ── User message bubble ───────────────────────────────────────────────────────
const UserBubble = ({ msg }) => (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.25, ease: 'easeOut' }}
    className="flex items-end justify-end gap-3 mb-6"
  >
    <div className="max-w-[75%] bg-gradient-to-r from-brand-500 to-cyan-500 rounded-2xl rounded-br-sm px-4 py-3 text-white text-sm leading-relaxed shadow-sm shadow-brand-500/20">
      {msg.text}
    </div>
    <div className="w-7 h-7 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center shrink-0 mb-0.5">
      <User size={13} className="text-gray-300" />
    </div>
  </motion.div>
)

// ── Main Chat Component ───────────────────────────────────────────────────────
const Chat = () => {
  const [conversations, setConversations] = useState([])
  const [activeConvId, setActiveConvId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [availableDocs, setAvailableDocs] = useState([])
  const [selectedDocId, setSelectedDocId] = useState('')

  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  // Voice recording state
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [detectedLang, setDetectedLang] = useState(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // Load document list for document filter dropdown
  useEffect(() => {
    async function loadDocs() {
      try {
        const res = await api.documents.list({ limit: 50 })
        setAvailableDocs(res.documents || [])
      } catch (err) {
        console.error('Failed to load documents for chat filter:', err)
      }
    }
    loadDocs()
  }, [])

  // Load conversation threads
  const loadConversations = useCallback(async () => {
    try {
      const res = await api.chat.listConversations({ limit: 30 })
      const list = res.conversations || []
      setConversations(list)
      if (list.length > 0 && !activeConvId) {
        setActiveConvId(list[0].id)
      }
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }, [activeConvId])

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  // Load conversation messages when activeConvId changes
  useEffect(() => {
    if (!activeConvId) {
      setMessages([])
      return
    }

    async function loadThread() {
      try {
        const data = await api.chat.getConversation(activeConvId)
        const msgs = (data.messages || []).map((m) => {
          const isUser = m.role === 'user'
          let confidence = 'supported'
          if (!isUser) {
            if (m.content.toLowerCase().includes('insufficient information')) {
              confidence = 'insufficient'
            } else if (m.content.toLowerCase().includes('conflict')) {
              confidence = 'conflicting'
            }
          }
          return {
            id: m.id,
            role: isUser ? 'user' : 'ai',
            text: m.content,
            confidence,
            sources: [],
          }
        })
        setMessages(msgs)
      } catch (err) {
        console.error('Failed to load thread messages:', err)
      }
    }

    loadThread()
  }, [activeConvId])

  // Determine response confidence
  const evaluateConfidence = (answer, sources) => {
    if (answer.toLowerCase().includes('insufficient information')) return 'insufficient'
    if (answer.toLowerCase().includes('conflict') || answer.toLowerCase().includes('differing')) return 'conflicting'
    return sources?.length > 0 ? 'supported' : 'insufficient'
  }

  // Handle sending a text message
  const handleSendMessage = async (e) => {
    e?.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || isTyping) return

    const userMsgId = `user-${Date.now()}`
    const userMsg = { id: userMsgId, role: 'user', text: trimmed }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    try {
      const documentIds = selectedDocId ? [selectedDocId] : null
      const res = await api.chat.sendMessage({
        message: trimmed,
        conversationId: activeConvId,
        documentIds,
      })

      const newConvId = res.conversation_id
      if (newConvId && newConvId !== activeConvId) {
        setActiveConvId(newConvId)
        loadConversations()
      }

      if (res.detected_language && res.detected_language !== 'en') {
        setDetectedLang(res.detected_language)
      }

      const sources = (res.sources || []).map((s, idx) => ({
        id: s.chunk_id || `src-${idx}`,
        file: s.document,
        page: s.page,
        section: s.section || 'General',
        snippet: `Grounded evidence cited from Page ${s.page} of ${s.document}`,
      }))

      const aiMsg = {
        id: `ai-${Date.now()}`,
        role: 'ai',
        text: res.answer,
        confidence: evaluateConfidence(res.answer, sources),
        sources,
      }

      setMessages((prev) => [...prev, aiMsg])
    } catch (err) {
      toast.error(err.message || 'Error generating answer')
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-err-${Date.now()}`,
          role: 'ai',
          text: `⚠️ An error occurred while communicating with the document intelligence engine: ${err.message}`,
          confidence: 'insufficient',
          sources: [],
        },
      ])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Voice recording handlers using MediaRecorder API
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioChunksRef.current = []
      const recorder = new MediaRecorder(stream)

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        stream.getTracks().forEach((track) => track.stop())
        await processVoiceBlob(audioBlob)
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
      setDetectedLang(null)
    } catch (err) {
      toast.error(`Microphone access denied: ${err.message}`)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsTranscribing(true)
    }
  }

  const handleMicClick = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const processVoiceBlob = async (audioBlob) => {
    try {
      const res = await api.chat.sendVoice({
        audioBlob,
        conversationId: activeConvId,
      })

      if (res.transcript) {
        setMessages((prev) => [
          ...prev,
          { id: `user-voice-${Date.now()}`, role: 'user', text: res.transcript },
        ])
      }

      if (res.detected_language) {
        setDetectedLang(res.detected_language)
      }

      const sources = (res.sources || []).map((s, idx) => ({
        id: s.chunk_id || `vsrc-${idx}`,
        file: s.document,
        page: s.page,
        section: s.section || 'General',
        snippet: `Spoken query verified against Page ${s.page} of ${s.document}`,
      }))

      setMessages((prev) => [
        ...prev,
        {
          id: `ai-voice-${Date.now()}`,
          role: 'ai',
          text: res.answer,
          confidence: evaluateConfidence(res.answer, sources),
          sources,
        },
      ])

      toast.success('Voice query transcribed and answered!')
    } catch (err) {
      toast.error(`Voice query failed: ${err.message}`)
    } finally {
      setIsTranscribing(false)
    }
  }

  const handleNewChat = () => {
    setActiveConvId(null)
    setMessages([])
    setInput('')
    setDetectedLang(null)
  }

  const handleDeleteConversation = async (convId) => {
    if (!confirm('Are you sure you want to delete this conversation?')) return
    try {
      await api.chat.deleteConversation(convId)
      setConversations((prev) => prev.filter((c) => c.id !== convId))
      if (activeConvId === convId) {
        handleNewChat()
      }
      toast.success('Conversation deleted')
    } catch (err) {
      toast.error(err.message || 'Failed to delete conversation')
    }
  }

  return (
    <div className="flex h-screen bg-navy-950 overflow-hidden">
      {/* ── Conversations sidebar ─────────────────────────────────────────── */}
      <ConvSidebar
        conversations={conversations}
        activeId={activeConvId}
        onSelect={(id) => setActiveConvId(id)}
        onNew={handleNewChat}
        onDelete={handleDeleteConversation}
      />

      {/* ── Chat column (header + messages + input) ───────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 h-screen">
        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between gap-3 px-6 py-4 border-b border-navy-700 bg-navy-950/90 backdrop-blur shrink-0">
          <div className="flex items-center gap-3">
            <Logo size="sm" showText={false} />
            <div>
              <h1 className="text-sm font-semibold text-white">Dastavez RAG Chat</h1>
              <p className="text-xs text-gray-500">
                Evidence-grounded conversational search with citations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Document Filter Dropdown */}
            <div className="flex items-center gap-1.5 bg-navy-900 border border-navy-700 rounded-lg px-2.5 py-1.5 text-xs text-gray-300">
              <Filter size={13} className="text-gray-400" />
              <select
                value={selectedDocId}
                onChange={(e) => setSelectedDocId(e.target.value)}
                className="bg-transparent text-gray-200 outline-none cursor-pointer max-w-[150px] truncate"
              >
                <option value="" className="bg-navy-900 text-white">
                  All Documents ({availableDocs.length})
                </option>
                {availableDocs.map((d) => (
                  <option key={d.id} value={d.id} className="bg-navy-900 text-white truncate">
                    {d.filename}
                  </option>
                ))}
              </select>
            </div>

            {/* Live Indicator */}
            <div className="flex items-center gap-1.5 text-xs text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Online
            </div>
          </div>
        </div>

        {/* ── Messages area ────────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto px-4 md:px-10 pt-6 pb-2">
          <div className="max-w-3xl mx-auto">
            {/* Empty state */}
            {messages.length === 0 && !isTyping && (
              <div className="flex flex-col items-center justify-center h-64 text-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-navy-900 border border-navy-700 flex items-center justify-center">
                  <Bot size={24} className="text-brand-400" />
                </div>
                <p className="text-gray-300 font-medium">
                  Ask questions about your uploaded documents
                </p>
                <p className="text-gray-500 text-sm">
                  Dastavez uses hybrid search and LLM reasoning with page-level citations.
                </p>
              </div>
            )}

            {/* Message list */}
            <AnimatePresence initial={false}>
              {messages.map((msg) =>
                msg.role === 'user' ? (
                  <UserBubble key={msg.id} msg={msg} />
                ) : (
                  <AIBubble key={msg.id} msg={msg} />
                )
              )}
            </AnimatePresence>

            {/* Typing indicator */}
            <AnimatePresence>
              {isTyping && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <TypingIndicator />
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={bottomRef} />
          </div>
        </div>

        {/* ── Input bar ────────────────────────────────────────────────────── */}
        <div className="shrink-0 border-t border-navy-700 bg-navy-950/90 backdrop-blur px-4 md:px-10 py-4">
          <div className="max-w-3xl mx-auto">
            {/* Detected language badge */}
            <AnimatePresence>
              {detectedLang && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 4 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-center gap-1.5 mb-2"
                >
                  <Globe2 size={12} className="text-brand-400" />
                  <span className="text-xs text-brand-400 font-medium">
                    Language: {detectedLang.toUpperCase()}
                  </span>
                  <button
                    type="button"
                    onClick={() => setDetectedLang(null)}
                    className="ml-auto text-gray-500 hover:text-gray-300 text-xs transition-colors duration-200"
                  >
                    ✕
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Listening / Transcribing indicator */}
            <AnimatePresence>
              {(isRecording || isTranscribing) && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center gap-2 mb-2"
                >
                  <motion.span
                    className="w-2 h-2 rounded-full bg-red-500"
                    animate={{ scale: [1, 1.4, 1], opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'easeInOut' }}
                  />
                  <span className="text-xs text-red-400 font-medium">
                    {isRecording ? 'Listening (click mic to stop and submit)…' : 'Transcribing via Sarvam Saaras…'}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Text input row */}
            <form onSubmit={handleSendMessage} className="flex items-end gap-2">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  id="chat-input"
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    isRecording
                      ? 'Listening to microphone...'
                      : selectedDocId
                      ? 'Ask about selected document...'
                      : 'Ask about all uploaded documents…'
                  }
                  disabled={isRecording || isTranscribing}
                  className={[
                    'w-full bg-navy-900 border text-gray-100 text-sm',
                    'rounded-xl px-4 py-3 placeholder-gray-500 resize-none',
                    'focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent',
                    'transition-all duration-200 leading-relaxed max-h-40 overflow-y-auto',
                    isRecording
                      ? 'border-red-500/50 bg-navy-900/60 cursor-not-allowed'
                      : 'border-navy-700',
                  ].join(' ')}
                />
              </div>

              {/* Mic button */}
              <button
                id="mic-btn"
                type="button"
                onClick={handleMicClick}
                disabled={isTranscribing}
                title={isRecording ? 'Stop recording & send' : 'Ask using voice'}
                className={[
                  'flex items-center justify-center w-11 h-11 rounded-xl shrink-0 cursor-pointer',
                  'transition-all duration-200 focus-visible:outline-none focus-visible:ring-2',
                  isRecording
                    ? 'bg-red-600 hover:bg-red-500 focus-visible:ring-red-500 shadow-lg shadow-red-600/30'
                    : isTranscribing
                    ? 'bg-navy-800 cursor-not-allowed opacity-60'
                    : 'bg-navy-900 border border-navy-700 hover:border-brand-500/50 hover:bg-navy-800 focus-visible:ring-brand-500',
                ].join(' ')}
              >
                {isRecording ? (
                  <motion.div
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity, ease: 'easeInOut' }}
                  >
                    <MicOff size={17} className="text-white" />
                  </motion.div>
                ) : (
                  <Mic size={17} className={isTranscribing ? 'text-gray-500' : 'text-gray-400'} />
                )}
              </button>

              {/* Send button */}
              <button
                id="send-btn"
                type="submit"
                disabled={!input.trim() || isRecording || isTyping}
                className="flex items-center justify-center w-11 h-11 rounded-xl bg-brand-500
                  hover:bg-brand-400 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer
                  transition-all duration-200 shadow-lg shadow-brand-500/25 active:scale-95 shrink-0
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-400"
              >
                <Send size={17} className="text-white" />
              </button>
            </form>

            <p className="text-center text-xs text-gray-500 mt-2.5">
              Press <kbd className="bg-navy-900 border border-navy-700 rounded px-1 text-gray-400 font-mono">Enter</kbd> to send
              · <kbd className="bg-navy-900 border border-navy-700 rounded px-1 text-gray-500 font-mono">Shift+Enter</kbd> for new line
              · <kbd className="bg-navy-900 border border-navy-700 rounded px-1 text-gray-400 font-mono">🎤</kbd> for voice query
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat
