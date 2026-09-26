import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import { Send, FileText, ChevronDown, Sparkles, Bot, User, Plus, MessageSquare, Mic, MicOff, Globe2, Paperclip, Loader2, CheckCircle, X } from 'lucide-react'
import Logo from '../components/Logo'

// ── Dummy conversations ───────────────────────────────────────────────────────
const CONVERSATIONS = [
  { id: 1, title: 'Hotel allowance policy',                timestamp: '2 hours ago'  },
  { id: 2, title: 'Eligibility criteria for Marathi circular', timestamp: 'Yesterday'    },
  { id: 3, title: 'Conflicting age limits',                timestamp: '2 days ago'   },
]

// ── Conversations sidebar ─────────────────────────────────────────────────────
const ConvSidebar = ({ activeId, onSelect, onNew }) => (
  <aside className="flex flex-col w-64 shrink-0 bg-navy-900 border-r border-navy-700 h-full">
    {/* New chat button */}
    <div className="p-3 border-b border-navy-700">
      <button
        onClick={onNew}
        className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg
          bg-gradient-to-r from-brand-500 to-brand-400 hover:from-brand-400 hover:to-brand-500
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
        Recent
      </p>
      {CONVERSATIONS.map((conv) => {
        const isActive = conv.id === activeId
        return (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={[
              'w-full text-left flex flex-col gap-0.5 px-3 py-2.5 rounded-lg transition-all duration-200 cursor-pointer',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
              isActive
                ? 'bg-brand-500/15 border border-brand-500/30'
                : 'border border-transparent hover:bg-navy-800 hover:border-navy-700',
            ].join(' ')}
          >
            <div className="flex items-center gap-2 min-w-0">
              <MessageSquare
                size={13}
                className={`shrink-0 ${isActive ? 'text-brand-400' : 'text-gray-500'}`}
              />
              <span
                className={`text-sm font-medium truncate ${
                  isActive ? 'text-brand-400' : 'text-gray-300'
                }`}
              >
                {conv.title}
              </span>
            </div>
            <span className="text-xs text-gray-500 pl-5">{conv.timestamp}</span>
          </button>
        )
      })}
    </nav>
  </aside>
)

// ── Dummy conversation ───────────────────────────────────────────────────────
const INITIAL_MESSAGES = [
  {
    id: 1,
    role: 'user',
    text: 'What is the hotel allowance for official travel?',
  },
  {
    id: 2,
    role: 'ai',
    text: "Employees can claim **₹3,000 per day** for hotel accommodation during official travel. This limit applies to domestic travel only.\n\nFor international travel, a separate allowance schedule applies based on the destination country.",
    confidence: 'supported',
    sources: [
      {
        id: 's1',
        file: 'Travel_Policy.pdf',
        page: 7,
        section: 'Accommodation',
        snippet:
          'Hotel reimbursement is capped at ₹3000 per day for domestic travel. Employees must obtain prior approval from their reporting manager for stays exceeding this limit.',
      },
      {
        id: 's2',
        file: 'Expense_Policy.pdf',
        page: 12,
        section: 'Required Documents',
        snippet:
          'Employees must submit the hotel invoice and travel authorization form within 7 working days of trip completion for reimbursement processing.',
      },
    ],
  },
]

// ── Confidence badge config with subtle border opacity ────────────────────────
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
          <span className="text-gray-500 shrink-0 hidden sm:inline">· {source.section}</span>
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
              "{source.snippet}"
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
    <div className="w-7 h-7 rounded-full bg-navy-800 border border-navy-700
      flex items-center justify-center shrink-0">
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
  const conf = CONFIDENCE_MAP[msg.confidence] ?? CONFIDENCE_MAP.insufficient
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="flex items-end gap-3 mb-6"
    >
      {/* Avatar */}
      <div className="w-7 h-7 rounded-full bg-brand-500/20 border border-brand-500/30
        flex items-center justify-center shrink-0 mb-0.5">
        <Bot size={13} className="text-brand-400" />
      </div>

      <div className="flex flex-col gap-2 max-w-[80%]">
        {/* Bubble */}
        <div className="bg-navy-800 border border-navy-700 rounded-2xl rounded-bl-sm px-4 py-3
          text-gray-200 text-sm leading-relaxed prose prose-invert prose-sm max-w-none">
          <ReactMarkdown>{msg.text}</ReactMarkdown>
        </div>

        {/* Confidence badge */}
        <span className={`self-start inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${conf.cls}`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70" />
          {conf.label}
        </span>

        {/* Sources */}
        {msg.sources?.length > 0 && (
          <div className="flex flex-col gap-1.5">
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
              Sources ({msg.sources.length})
            </p>
            {msg.sources.map((src) => (
              <SourceCard key={src.id} source={src} />
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
    <div className="max-w-[75%] bg-gradient-to-r from-brand-500 to-brand-400 rounded-2xl rounded-br-sm px-4 py-3
      text-white text-sm leading-relaxed shadow-sm shadow-brand-500/20">
      {msg.text}
    </div>
    <div className="w-7 h-7 rounded-full bg-navy-800 border border-navy-700
      flex items-center justify-center shrink-0 mb-0.5">
      <User size={13} className="text-gray-300" />
    </div>
  </motion.div>
)

// ── Main Chat page ────────────────────────────────────────────────────────────
const Chat = () => {
  const [messages, setMessages]   = useState(INITIAL_MESSAGES)
  const [input, setInput]         = useState('')
  const [isTyping, setIsTyping]   = useState(false)
  const [activeConvId, setActiveConvId] = useState(CONVERSATIONS[0].id)
  const bottomRef                 = useRef(null)
  const textareaRef               = useRef(null)
  const fileInputRef              = useRef(null)

  // File attach state
  const [attachedFile, setAttachedFile] = useState(null)

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setAttachedFile({ name: file.name, isUploading: true })
    setTimeout(() => {
      setAttachedFile((prev) => (prev ? { ...prev, isUploading: false } : null))
    }, 2500)
    e.target.value = ''
  }

  const handleRemoveFile = () => {
    setAttachedFile(null)
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const sendMessage = (e) => {
    e?.preventDefault()
    const trimmed = input.trim()
    if (!trimmed && !attachedFile) return

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: 'user', text: trimmed || (attachedFile ? `[Attached File: ${attachedFile.name}]` : '') },
    ])
    setInput('')
    setAttachedFile(null)

    setIsTyping(true)
    setTimeout(() => setIsTyping(false), 2000)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Voice input state
  const [isRecording,    setIsRecording]    = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [detectedLang,   setDetectedLang]   = useState(null)
  const micTimerRef = useRef(null)

  const SAMPLE_TRANSCRIPT = 'इन सभी दस्तावेज़ों में पात्रता की शर्तें क्या हैं?'

  const handleMic = () => {
    if (isRecording) {
      setIsRecording(false)
      setIsTranscribing(true)
      micTimerRef.current = setTimeout(() => {
        setInput(SAMPLE_TRANSCRIPT)
        setDetectedLang('Hindi')
        setIsTranscribing(false)
        textareaRef.current?.focus()
      }, 1500)
    } else {
      clearTimeout(micTimerRef.current)
      setIsRecording(true)
      setDetectedLang(null)
    }
  }

  useEffect(() => () => clearTimeout(micTimerRef.current), [])

  const handleNewChat = () => {
    setMessages([])
    setActiveConvId(null)
    setInput('')
    setAttachedFile(null)
  }

  return (
    <div className="flex h-screen bg-navy-950 overflow-hidden">

      {/* ── Conversations sidebar ─────────────────────────────────────────── */}
      <ConvSidebar
        activeId={activeConvId}
        onSelect={(id) => setActiveConvId(id)}
        onNew={handleNewChat}
      />

      {/* ── Chat column (header + messages + input) ───────────────────────── */}
      <div className="flex flex-col flex-1 min-w-0 h-screen">

        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-navy-700 bg-navy-950/90 backdrop-blur shrink-0">
          <Logo size="md" showText={false} />
          <div>
            <h1 className="text-sm font-semibold text-white">Dastavez Chat</h1>
            <p className="text-xs text-gray-500">Ask anything about your documents</p>
          </div>
          {/* Live dot */}
          <div className="ml-auto flex items-center gap-1.5 text-xs text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Ready
          </div>
        </div>

        {/* ── Messages area ────────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto px-4 md:px-10 pt-6 pb-2">
          <div className="max-w-3xl mx-auto">

            {/* Empty state */}
            {messages.length === 0 && !isTyping && (
              <div className="flex flex-col items-center justify-center h-64 text-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-navy-900 border border-navy-700
                  flex items-center justify-center">
                  <Bot size={24} className="text-brand-400" />
                </div>
                <p className="text-gray-300 font-medium">Ask me anything about your documents</p>
                <p className="text-gray-500 text-sm">I'll find the answer and show you the sources.</p>
              </div>
            )}

            {/* Message list */}
            <AnimatePresence initial={false}>
              {messages.map((msg) =>
                msg.role === 'user'
                  ? <UserBubble key={msg.id} msg={msg} />
                  : <AIBubble   key={msg.id} msg={msg} />
              )}
            </AnimatePresence>

            {/* Typing indicator */}
            <AnimatePresence>
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
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

            {/* Uploading / Attached file chip */}
            <AnimatePresence>
              {attachedFile && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 4 }}
                  transition={{ duration: 0.2 }}
                  className="mb-2.5 flex items-center justify-between bg-navy-800 border border-navy-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 shadow-sm"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <FileText size={15} className="text-brand-400 shrink-0" />
                    <span className="font-medium truncate max-w-xs text-gray-200">{attachedFile.name}</span>
                    {attachedFile.isUploading ? (
                      <span className="flex items-center gap-1.5 text-xs text-amber-400 bg-amber-400/10 border border-amber-400/20 px-2 py-0.5 rounded-full shrink-0 ml-1">
                        <Loader2 size={12} className="animate-spin text-amber-400 shrink-0" />
                        Uploading...
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2 py-0.5 rounded-full shrink-0 ml-1">
                        <CheckCircle size={12} className="text-emerald-400 shrink-0" />
                        Ready
                      </span>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={handleRemoveFile}
                    title="Remove file"
                    className="ml-2 text-gray-400 hover:text-white p-0.5 rounded-md hover:bg-navy-700 transition-colors duration-200 cursor-pointer"
                  >
                    <X size={15} />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

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
                  <span className="text-xs text-brand-400 font-medium">Detected: {detectedLang}</span>
                  <span className="text-xs text-gray-500">· Edit your message before sending</span>
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

            {/* Listening indicator */}
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
                    {isRecording ? 'Listening…' : 'Transcribing…'}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Text input row */}
            <form
              onSubmit={sendMessage}
              className="flex items-end gap-2"
            >
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileSelect}
                className="hidden"
              />

              {/* Attach file button (Left of textarea) */}
              <button
                id="attach-file-btn"
                type="button"
                onClick={() => fileInputRef.current?.click()}
                title="Attach document (.pdf, .png, .jpg, .jpeg)"
                className="flex items-center justify-center w-11 h-11 rounded-xl bg-navy-900 border border-navy-700 hover:border-brand-500/50 hover:bg-navy-800 text-gray-400 hover:text-white transition-all duration-200 shrink-0 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
              >
                <Paperclip size={17} />
              </button>
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  id="chat-input"
                  rows={1}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={isRecording ? '' : 'Ask about your documents…'}
                  disabled={isRecording}
                  className={[
                    'w-full bg-navy-900 border text-gray-100 text-sm',
                    'rounded-xl px-4 py-3 placeholder-gray-500 resize-none',
                    'focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent',
                    'transition-all duration-200 leading-relaxed max-h-40 overflow-y-auto',
                    isRecording
                      ? 'border-red-500/50 bg-navy-900/60 cursor-not-allowed'
                      : 'border-navy-700',
                  ].join(' ')}
                  style={{ fieldSizing: 'content' }}
                />

                {isRecording && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <motion.div
                      className="flex items-center gap-2"
                      animate={{ opacity: [1, 0.4, 1] }}
                      transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                    >
                      <Mic size={16} className="text-red-400" />
                      <span className="text-sm text-red-400 font-medium">Listening…</span>
                    </motion.div>
                  </div>
                )}
              </div>

              {/* Mic button */}
              <button
                id="mic-btn"
                type="button"
                onClick={handleMic}
                disabled={isTranscribing}
                title={isRecording ? 'Stop recording' : 'Start voice input'}
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
                disabled={!input.trim() || isRecording}
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
              · <kbd className="bg-navy-900 border border-navy-700 rounded px-1 text-gray-400 font-mono">🎤</kbd> for voice
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat
