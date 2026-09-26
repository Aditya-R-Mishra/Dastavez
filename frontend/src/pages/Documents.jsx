import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud, FileText, Image, CheckCircle,
  AlertCircle, Clock, FolderOpen, Sparkles, X, Loader2, Check
} from 'lucide-react'

// ── Dummy existing docs ──────────────────────────────────────────────────────
const INITIAL_DOCS = [
  {
    id: 1,
    name: 'HR_Policy.pdf',
    pages: 42,
    status: 'processed',
  },
  {
    id: 2,
    name: 'scanned_claim_form.jpg',
    pages: 3,
    status: 'processing',
    progress: 65,
    stage: 'Generating embeddings',
    steps: [
      { label: 'Layout Analysis & OCR', status: 'completed' },
      { label: 'Generating Embeddings', status: 'in-progress' },
      { label: 'Vector Indexing', status: 'pending' },
    ],
  },
  {
    id: 3,
    name: 'circular_marathi.jpg',
    pages: 2,
    status: 'processing',
    progress: 30,
    stage: 'Running OCR (Sarvam Vision)',
    steps: [
      { label: 'File Validation', status: 'completed' },
      { label: 'Running OCR (Sarvam Vision)', status: 'in-progress' },
      { label: 'Embedding & Indexing', status: 'pending' },
    ],
  },
  {
    id: 4,
    name: 'old_form.png',
    pages: 1,
    status: 'failed',
    error: 'OCR failed on page 1',
  },
]

// ── Helpers ───────────────────────────────────────────────────────────────────
const isPdf   = (name) => name.toLowerCase().endsWith('.pdf')
const fmtSize = (bytes) => {
  if (bytes < 1024)      return `${bytes} B`
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

// ── File icon ─────────────────────────────────────────────────────────────────
const FileIcon = ({ name }) =>
  isPdf(name) ? (
    <div className="w-10 h-10 rounded-lg bg-brand-500/15 border border-brand-500/30 flex items-center justify-center shrink-0">
      <FileText size={20} className="text-brand-400" />
    </div>
  ) : (
    <div className="w-10 h-10 rounded-lg bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center shrink-0">
      <Image size={20} className="text-cyan-400" />
    </div>
  )

// ── Status badge with subtle border opacity ──────────────────────────────────
const StatusBadge = ({ status }) => {
  const map = {
    processed:  { label: 'Processed',  cls: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30', dot: 'bg-emerald-400', pulse: false, icon: <CheckCircle size={11} /> },
    processing: { label: 'Processing', cls: 'bg-amber-500/15  text-amber-400  border-amber-500/30',   dot: 'bg-amber-400',   pulse: true,  icon: <Clock size={11} />       },
    failed:     { label: 'Failed',     cls: 'bg-red-500/15    text-red-400    border-red-500/30',     dot: 'bg-red-400',     pulse: false, icon: <AlertCircle size={11} /> },
  }
  const { label, cls, dot, pulse, icon } = map[status] ?? map.failed
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot} ${pulse ? 'animate-pulse' : ''}`} />
      {icon}
      {label}
    </span>
  )
}

// ── Animated upload progress bar ──────────────────────────────────────────────
const UploadProgressBar = ({ progress, color = 'bg-brand-500' }) => (
  <div className="w-full h-1.5 bg-navy-950 rounded-full overflow-hidden">
    <motion.div
      className={`h-full ${color} rounded-full`}
      initial={{ width: 0 }}
      animate={{ width: `${progress}%` }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    />
  </div>
)

// ── Upload queue row ──────────────────────────────────────────────────────────
const UploadQueueItem = ({ item, onCancel }) => {
  const done    = item.progress >= 100
  const isError = item.progress === -1
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0, marginBottom: 0 }}
      transition={{ duration: 0.2 }}
      className="flex items-center gap-3 bg-navy-900 border border-navy-700 rounded-xl px-4 py-3"
    >
      <FileIcon name={item.name} />

      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <p className="text-xs font-medium text-gray-300 truncate">{item.name}</p>
          <span className="text-xs text-gray-500 shrink-0 ml-2">{fmtSize(item.size)}</span>
        </div>

        {isError ? (
          <p className="text-xs text-red-400">Upload failed — please retry</p>
        ) : done ? (
          <p className="text-xs text-emerald-400 flex items-center gap-1">
            <CheckCircle size={11} /> Uploaded — processing…
          </p>
        ) : (
          <div className="flex items-center gap-2">
            <UploadProgressBar
              progress={item.progress}
              color={isPdf(item.name) ? 'bg-brand-500' : 'bg-cyan-500'}
            />
            <span className="text-xs text-gray-500 shrink-0 w-9 text-right">{item.progress}%</span>
          </div>
        )}
      </div>

      {!done && !isError && (
        <button
          onClick={() => onCancel(item.id)}
          className="text-gray-500 hover:text-gray-300 transition-colors duration-200 shrink-0"
          title="Cancel upload"
        >
          <X size={14} />
        </button>
      )}
    </motion.div>
  )
}

// ── Card animation variants ────────────────────────────────────────────────────
const cardVariants = {
  hidden:  { opacity: 0, y: 16 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.3, ease: 'easeOut' } }),
}

// ── Main component ────────────────────────────────────────────────────────────
const Documents = () => {
  const [docs,     setDocs]     = useState(INITIAL_DOCS)
  const [queue,    setQueue]    = useState([])
  const [dragOver, setDragOver] = useState(false)
  const inputRef                = useRef(null)
  const cancelsRef              = useRef({})

  const enqueueFiles = (files) => {
    Array.from(files).forEach((file) => {
      if (!file) return
      const id = Date.now() + Math.random()
      setQueue((q) => [...q, { id, name: file.name, size: file.size, progress: 0 }])

      let pct = 0
      const timer = setInterval(() => {
        pct = Math.min(100, pct + Math.round(Math.random() * 15 + 10))
        setQueue((q) => q.map((item) => item.id === id ? { ...item, progress: pct } : item))
        if (pct >= 100) {
          clearInterval(timer)
          setTimeout(() => {
            setQueue((q) => q.filter((item) => item.id !== id))
            setDocs((d) => [
              {
                id,
                name: file.name,
                pages: '—',
                status: 'processing',
                progress: 20,
                stage: 'File validation & layout analysis',
                steps: [
                  { label: 'File Validation', status: 'in-progress' },
                  { label: 'OCR & Layout Analysis', status: 'pending' },
                  { label: 'Vector Indexing', status: 'pending' },
                ],
              },
              ...d,
            ])
          }, 600)
        }
      }, 180)
      cancelsRef.current[id] = () => clearInterval(timer)
    })
  }

  const cancelUpload = (id) => {
    cancelsRef.current[id]?.()
    delete cancelsRef.current[id]
    setQueue((q) => q.filter((item) => item.id !== id))
  }

  const totalCount = docs.length + queue.length

  return (
    <div className="min-h-full bg-navy-950 p-6 md:p-8 space-y-6">
      {/* ── Page header ──────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={16} className="text-brand-400" />
          <span className="text-xs font-semibold text-brand-400 uppercase tracking-widest">Documents</span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-white">Your Documents</h1>
        <p className="text-gray-400 mt-1 text-sm">Upload files and track their processing status.</p>
      </div>

      {/* ── Upload zone ──────────────────────────────────────────────────── */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); enqueueFiles(e.dataTransfer.files) }}
        onClick={() => inputRef.current?.click()}
        className={[
          'relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed',
          'px-6 py-12 cursor-pointer select-none transition-all duration-200',
          dragOver
            ? 'border-brand-500 bg-brand-500/10'
            : 'border-navy-700 bg-navy-900 hover:border-brand-500/60 hover:bg-navy-800/80',
        ].join(' ')}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          multiple
          className="hidden"
          onChange={(e) => { enqueueFiles(e.target.files); e.target.value = '' }}
        />

        <div className={[
          'w-14 h-14 rounded-2xl flex items-center justify-center transition-colors duration-200',
          dragOver ? 'bg-brand-500/20' : 'bg-navy-800 border border-navy-700',
        ].join(' ')}>
          <UploadCloud size={26} className={dragOver ? 'text-brand-400' : 'text-gray-400'} />
        </div>

        <div className="text-center">
          <p className={`text-sm font-semibold transition-colors duration-200 ${dragOver ? 'text-brand-400' : 'text-gray-200'}`}>
            {dragOver ? 'Drop files to upload' : 'Drag & drop files here or click to browse'}
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF, PNG, JPG, JPEG · Max 50 MB per file</p>
        </div>
      </div>

      {/* ── Upload queue ─────────────────────────────────────────────────── */}
      <AnimatePresence initial={false}>
        {queue.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex flex-col gap-2 overflow-hidden"
          >
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-1">
              Uploading {queue.length} {queue.length === 1 ? 'file' : 'files'}…
            </p>
            <AnimatePresence>
              {queue.map((item) => (
                <UploadQueueItem key={item.id} item={item} onCancel={cancelUpload} />
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Section label ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between pt-2">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Uploaded Files</h2>
        <span className="text-xs text-gray-400 bg-navy-900 border border-navy-700 rounded-full px-2.5 py-0.5">
          {totalCount} {totalCount === 1 ? 'file' : 'files'}
        </span>
      </div>

      {/* ── Document cards grid ───────────────────────────────────────────── */}
      {docs.length === 0 && queue.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-navy-900 border border-navy-700 flex items-center justify-center mb-4">
            <FolderOpen size={28} className="text-gray-500" />
          </div>
          <h3 className="text-gray-300 font-semibold">No documents yet</h3>
          <p className="text-gray-500 text-sm mt-1">Upload a file above to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <AnimatePresence>
            {docs.map((doc, i) => (
              <motion.div
                key={doc.id}
                layout
                custom={i}
                variants={cardVariants}
                initial="hidden"
                animate="visible"
                exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.15 } }}
                className="bg-navy-900 border border-navy-700 rounded-xl p-4 flex flex-col justify-between gap-3
                  hover:border-gray-700 hover:-translate-y-0.5 transition-all duration-200 group"
              >
                <div>
                  {/* Icon + badge */}
                  <div className="flex items-start justify-between mb-3">
                    <FileIcon name={doc.name} />
                    <StatusBadge status={doc.status} />
                  </div>

                  {/* Name + pages */}
                  <div>
                    <p className="text-sm font-semibold text-gray-200 truncate group-hover:text-white transition-colors duration-200" title={doc.name}>
                      {doc.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {doc.pages === '—' ? 'Counting pages…' : `${doc.pages} ${doc.pages === 1 ? 'page' : 'pages'}`}
                    </p>
                  </div>
                </div>

                {/* Footer / Status details */}
                <div className="pt-2 border-t border-navy-700 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className={`self-start text-xs font-medium px-2 py-0.5 rounded-md ${
                      isPdf(doc.name) ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20' : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    }`}>
                      {isPdf(doc.name) ? 'PDF' : 'Image'}
                    </span>

                    {/* Progress percentage if processing */}
                    {doc.status === 'processing' && doc.progress !== undefined && (
                      <span className="text-xs font-semibold text-brand-400">
                        {doc.progress}%
                      </span>
                    )}
                  </div>

                  {/* Processing progress bar & step-by-step pipeline checklist */}
                  {doc.status === 'processing' && (
                    <div className="flex flex-col gap-2.5 mt-1">
                      <div className="w-full h-1.5 bg-navy-950 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-brand-500 to-brand-cyan rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${doc.progress ?? 0}%` }}
                          transition={{ duration: 0.5, ease: 'easeOut' }}
                        />
                      </div>

                      {/* Step-by-step pipeline checklist */}
                      {doc.steps && doc.steps.length > 0 && (
                        <div className="bg-navy-950 border border-navy-700/60 rounded-lg p-2.5 space-y-1.5 text-xs">
                          {doc.steps.map((step, sIdx) => {
                            const isDone    = step.status === 'completed'
                            const isInProg  = step.status === 'in-progress'
                            return (
                              <div key={sIdx} className="flex items-center gap-2">
                                {isDone ? (
                                  <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                                    <Check size={10} />
                                  </div>
                                ) : isInProg ? (
                                  <Loader2 size={12} className="text-brand-400 animate-spin shrink-0" />
                                ) : (
                                  <div className="w-3.5 h-3.5 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center shrink-0">
                                    <Clock size={8} className="text-gray-600" />
                                  </div>
                                )}
                                <span className={
                                  isDone
                                    ? 'text-gray-400 line-through decoration-gray-600'
                                    : isInProg
                                      ? 'text-brand-400 font-medium'
                                      : 'text-gray-600'
                                }>
                                  {step.label}
                                </span>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Error text if failed */}
                  {doc.status === 'failed' && doc.error && (
                    <div className="flex items-start gap-1.5 text-xs text-red-400 bg-red-500/10 border border-red-500/25 rounded-lg p-2 mt-0.5">
                      <AlertCircle size={13} className="shrink-0 mt-0.5" />
                      <span className="truncate" title={doc.error}>{doc.error}</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}

export default Documents
