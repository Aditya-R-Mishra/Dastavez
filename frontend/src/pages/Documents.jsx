import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud, FileText, Image, CheckCircle,
  AlertCircle, Clock, FolderOpen, Sparkles, X, Loader2, Check, Trash2, RefreshCw
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../lib/api'

// ── Helpers ───────────────────────────────────────────────────────────────────
const isPdf = (name = '') => name.toLowerCase().endsWith('.pdf')
const fmtSize = (bytes = 0) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
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

// ── Status badge ─────────────────────────────────────────────────────────────
const StatusBadge = ({ status }) => {
  const map = {
    processed:  { label: 'Processed',  cls: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30', dot: 'bg-emerald-400', pulse: false, icon: <CheckCircle size={11} /> },
    processing: { label: 'Processing', cls: 'bg-amber-500/15  text-amber-400  border-amber-500/30',   dot: 'bg-amber-400',   pulse: true,  icon: <Clock size={11} />       },
    failed:     { label: 'Failed',     cls: 'bg-red-500/15    text-red-400    border-red-500/30',     dot: 'bg-red-400',     pulse: false, icon: <AlertCircle size={11} /> },
  }
  const { label, cls, dot, pulse, icon } = map[status] ?? map.processing
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${cls}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot} ${pulse ? 'animate-pulse' : ''}`} />
      {icon}
      {label}
    </span>
  )
}

// ── Upload queue item ────────────────────────────────────────────────────────
const UploadQueueItem = ({ item }) => {
  const done = item.progress >= 100
  const isError = item.error
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
          <p className="text-xs text-red-400">{item.error}</p>
        ) : done ? (
          <p className="text-xs text-emerald-400 flex items-center gap-1">
            <CheckCircle size={11} /> Uploaded — processing started…
          </p>
        ) : (
          <div className="flex items-center gap-2">
            <div className="w-full h-1.5 bg-navy-950 rounded-full overflow-hidden">
              <div
                className={`h-full ${isPdf(item.name) ? 'bg-brand-500' : 'bg-cyan-500'} rounded-full transition-all duration-300`}
                style={{ width: `${item.progress}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 shrink-0 w-9 text-right">{item.progress}%</span>
          </div>
        )}
      </div>
    </motion.div>
  )
}

const cardVariants = {
  hidden:  { opacity: 0, y: 16 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.05, duration: 0.25, ease: 'easeOut' } }),
}

// ── Main component ────────────────────────────────────────────────────────────
const Documents = () => {
  const [docs, setDocs] = useState([])
  const [queue, setQueue] = useState([])
  const [loading, setLoading] = useState(true)
  const [dragOver, setDragOver] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  const inputRef = useRef(null)

  const mapBackendStatus = (backendStatus) => {
    const s = (backendStatus || '').toUpperCase()
    if (s === 'COMPLETED') return 'processed'
    if (s === 'FAILED') return 'failed'
    return 'processing'
  }

  const buildPipelineSteps = (stage, progress) => [
    {
      label: 'File Extraction & Layout',
      status: progress >= 30 ? 'completed' : progress > 0 ? 'in-progress' : 'pending',
    },
    {
      label: 'OCR & Text Normalization',
      status: progress >= 60 ? 'completed' : progress >= 30 ? 'in-progress' : 'pending',
    },
    {
      label: 'Dense Embedding & Vector Indexing',
      status: progress >= 100 ? 'completed' : progress >= 60 ? 'in-progress' : 'pending',
    },
  ]

  // Fetch documents from backend
  const fetchDocuments = useCallback(async (showToast = false) => {
    try {
      const res = await api.documents.list({ limit: 50 })
      const backendDocs = res.documents || []
      const formatted = backendDocs.map((d) => ({
        id: d.id,
        name: d.filename,
        pages: d.page_count ?? '—',
        status: mapBackendStatus(d.status),
        rawStatus: d.status,
        progress: d.status === 'COMPLETED' ? 100 : 40,
        createdAt: d.created_at,
        steps: buildPipelineSteps('', d.status === 'COMPLETED' ? 100 : 40),
      }))
      setDocs(formatted)
      if (showToast) toast.success('Documents updated')
    } catch (err) {
      toast.error(err.message || 'Failed to fetch documents')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
  }, [fetchDocuments])

  // Polling for any processing documents
  useEffect(() => {
    const hasProcessing = docs.some((d) => d.status === 'processing')
    if (!hasProcessing) return

    const interval = setInterval(async () => {
      let anyChanged = false
      const updated = await Promise.all(
        docs.map(async (doc) => {
          if (doc.status !== 'processing') return doc
          try {
            const statusRes = await api.documents.getStatus(doc.id)
            const mapped = mapBackendStatus(statusRes.status)
            if (mapped !== doc.status || statusRes.progress !== doc.progress) {
              anyChanged = true
              return {
                ...doc,
                status: mapped,
                rawStatus: statusRes.status,
                progress: statusRes.progress ?? doc.progress,
                stage: statusRes.current_stage,
                error: statusRes.error_message,
                steps: buildPipelineSteps(statusRes.current_stage, statusRes.progress),
              }
            }
          } catch {
            // Keep existing state on transient poll failure
          }
          return doc
        })
      )
      if (anyChanged) {
        setDocs(updated)
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [docs])

  // Handle uploading files
  const enqueueFiles = async (files) => {
    const fileList = Array.from(files).filter(Boolean)
    if (!fileList.length) return

    for (const file of fileList) {
      const tempId = `upload-${Date.now()}-${Math.random()}`
      setQueue((q) => [...q, { id: tempId, name: file.name, size: file.size, progress: 30 }])

      try {
        setQueue((q) => q.map((item) => (item.id === tempId ? { ...item, progress: 70 } : item)))
        const res = await api.documents.upload(file)

        setQueue((q) => q.map((item) => (item.id === tempId ? { ...item, progress: 100 } : item)))
        toast.success(`Uploaded ${file.name}! Processing started.`)

        setTimeout(() => {
          setQueue((q) => q.filter((item) => item.id !== tempId))
          setDocs((prev) => [
            {
              id: res.document_id,
              name: res.filename,
              pages: '—',
              status: 'processing',
              progress: 20,
              stage: 'Starting pipeline...',
              steps: buildPipelineSteps('UPLOADED', 20),
            },
            ...prev,
          ])
        }, 800)
      } catch (err) {
        setQueue((q) =>
          q.map((item) =>
            item.id === tempId
              ? { ...item, error: err.message || 'Upload failed', progress: -1 }
              : item
          )
        )
        toast.error(`Failed to upload ${file.name}: ${err.message}`)
      }
    }
  }

  // Handle deleting document
  const handleDelete = async (docId, docName) => {
    if (!confirm(`Are you sure you want to delete "${docName}"?`)) return
    setDeletingId(docId)
    try {
      await api.documents.delete(docId)
      setDocs((prev) => prev.filter((d) => d.id !== docId))
      toast.success(`Deleted ${docName}`)
    } catch (err) {
      toast.error(err.message || 'Failed to delete document')
    } finally {
      setDeletingId(null)
    }
  }

  const totalCount = docs.length + queue.length

  return (
    <div className="min-h-full bg-navy-950 p-6 md:p-8 space-y-6">
      {/* ── Page header ──────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles size={16} className="text-brand-400" />
            <span className="text-xs font-semibold text-brand-400 uppercase tracking-widest">
              Documents
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">Your Documents</h1>
          <p className="text-gray-400 mt-1 text-sm">Upload files and track their processing status.</p>
        </div>
        <button
          onClick={() => fetchDocuments(true)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-navy-900 border border-navy-700 text-xs text-gray-300 hover:text-white hover:border-gray-600 transition-colors"
          title="Refresh document list"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* ── Upload zone ──────────────────────────────────────────────────── */}
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          enqueueFiles(e.dataTransfer.files)
        }}
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
          accept=".pdf,.png,.jpg,.jpeg,.docx,.csv,.txt"
          multiple
          className="hidden"
          onChange={(e) => {
            enqueueFiles(e.target.files)
            e.target.value = ''
          }}
        />

        <div
          className={[
            'w-14 h-14 rounded-2xl flex items-center justify-center transition-colors duration-200',
            dragOver ? 'bg-brand-500/20' : 'bg-navy-800 border border-navy-700',
          ].join(' ')}
        >
          <UploadCloud size={26} className={dragOver ? 'text-brand-400' : 'text-gray-400'} />
        </div>

        <div className="text-center">
          <p
            className={`text-sm font-semibold transition-colors duration-200 ${
              dragOver ? 'text-brand-400' : 'text-gray-200'
            }`}
          >
            {dragOver ? 'Drop files to upload' : 'Drag & drop files here or click to browse'}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            PDF, DOCX, CSV, TXT, PNG, JPG, JPEG · Ingestion & Vector Indexing
          </p>
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
                <UploadQueueItem key={item.id} item={item} />
              ))}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Section label ─────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between pt-2">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">
          Indexed Documents
        </h2>
        <span className="text-xs text-gray-400 bg-navy-900 border border-navy-700 rounded-full px-2.5 py-0.5">
          {totalCount} {totalCount === 1 ? 'file' : 'files'}
        </span>
      </div>

      {/* ── Document cards grid ───────────────────────────────────────────── */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="text-brand-400 animate-spin" />
        </div>
      ) : docs.length === 0 && queue.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-navy-900 border border-navy-700 flex items-center justify-center mb-4">
            <FolderOpen size={28} className="text-gray-500" />
          </div>
          <h3 className="text-gray-300 font-semibold">No documents indexed yet</h3>
          <p className="text-gray-500 text-sm mt-1">Upload a PDF or document above to begin indexing.</p>
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
                  hover:border-gray-700 hover:-translate-y-0.5 transition-all duration-200 group relative"
              >
                <div>
                  {/* Icon + badge */}
                  <div className="flex items-start justify-between mb-3">
                    <FileIcon name={doc.name} />
                    <div className="flex items-center gap-2">
                      <StatusBadge status={doc.status} />
                      <button
                        onClick={() => handleDelete(doc.id, doc.name)}
                        disabled={deletingId === doc.id}
                        title="Delete document"
                        className="text-gray-500 hover:text-red-400 p-1 rounded hover:bg-red-500/10 transition-colors"
                      >
                        {deletingId === doc.id ? (
                          <Loader2 size={14} className="animate-spin text-red-400" />
                        ) : (
                          <Trash2 size={14} />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Name + pages */}
                  <div>
                    <p
                      className="text-sm font-semibold text-gray-200 truncate group-hover:text-white transition-colors duration-200"
                      title={doc.name}
                    >
                      {doc.name}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {doc.pages === '—'
                        ? 'Processing pages…'
                        : `${doc.pages} ${doc.pages === 1 ? 'page' : 'pages'}`}
                    </p>
                  </div>
                </div>

                {/* Footer / Status details */}
                <div className="pt-2 border-t border-navy-700 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span
                      className={`self-start text-xs font-medium px-2 py-0.5 rounded-md ${
                        isPdf(doc.name)
                          ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20'
                          : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                      }`}
                    >
                      {isPdf(doc.name) ? 'PDF' : 'Document'}
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
                          className="h-full bg-gradient-to-r from-brand-500 to-cyan-400 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${doc.progress ?? 0}%` }}
                          transition={{ duration: 0.5, ease: 'easeOut' }}
                        />
                      </div>

                      {/* Step-by-step pipeline checklist */}
                      {doc.steps && doc.steps.length > 0 && (
                        <div className="bg-navy-950 border border-navy-700/60 rounded-lg p-2.5 space-y-1.5 text-xs">
                          {doc.steps.map((step, sIdx) => {
                            const isDone = step.status === 'completed'
                            const isInProg = step.status === 'in-progress'
                            return (
                              <div key={sIdx} className="flex items-center gap-2">
                                {isDone ? (
                                  <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                                    <Check size={10} />
                                  </div>
                                ) : isInProg ? (
                                  <Loader2
                                    size={12}
                                    className="text-brand-400 animate-spin shrink-0"
                                  />
                                ) : (
                                  <div className="w-3.5 h-3.5 rounded-full bg-navy-800 border border-navy-700 flex items-center justify-center shrink-0">
                                    <Clock size={8} className="text-gray-600" />
                                  </div>
                                )}
                                <span
                                  className={
                                    isDone
                                      ? 'text-gray-400 line-through decoration-gray-600'
                                      : isInProg
                                      ? 'text-brand-400 font-medium'
                                      : 'text-gray-600'
                                  }
                                >
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
                      <span className="truncate" title={doc.error}>
                        {doc.error}
                      </span>
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
