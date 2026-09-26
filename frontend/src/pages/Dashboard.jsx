import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  CheckCircle,
  Loader,
  AlertCircle,
  Upload,
  MessageSquare,
  ArrowRight,
  Sparkles,
  Clock,
  Loader2,
} from 'lucide-react'
import api, { authStorage } from '../lib/api'

// Helper to format timestamps to relative time strings
function formatRelativeTime(dateStr) {
  if (!dateStr) return 'Recently'
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000)
    if (diffSec < 60) return 'Just now'
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)} min ago`
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} hours ago`
    return `${Math.floor(diffSec / 86400)} days ago`
  } catch {
    return 'Recently'
  }
}

const Dashboard = () => {
  const navigate = useNavigate()
  const user = authStorage.getUser()

  const [loading, setLoading] = useState(true)
  const [documents, setDocuments] = useState([])
  const [stats, setStats] = useState({
    total: 0,
    processed: 0,
    processing: 0,
    failed: 0,
  })

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const res = await api.documents.list({ limit: 20 })
        const docs = res.documents || []
        setDocuments(docs)

        const total = docs.length
        const processed = docs.filter((d) => d.status === 'COMPLETED').length
        const failed = docs.filter((d) => d.status === 'FAILED').length
        const processing = docs.filter((d) => d.status === 'PROCESSING' || d.status === 'PENDING').length

        setStats({ total, processed, processing, failed })
      } catch (err) {
        console.error('Failed to load dashboard stats:', err)
      } finally {
        setLoading(false)
      }
    }
    loadDashboardData()
  }, [])

  const STATS_CARDS = [
    {
      id: 'total',
      label: 'Total Documents',
      value: stats.total,
      icon: FileText,
      iconBg: 'bg-brand-500/15',
      iconColor: 'text-brand-400',
      border: 'border-brand-500/30',
    },
    {
      id: 'processed',
      label: 'Processed & Indexed',
      value: stats.processed,
      icon: CheckCircle,
      iconBg: 'bg-emerald-500/15',
      iconColor: 'text-emerald-400',
      border: 'border-emerald-500/30',
    },
    {
      id: 'processing',
      label: 'In Ingestion Pipeline',
      value: stats.processing,
      icon: Loader,
      iconBg: 'bg-amber-500/15',
      iconColor: 'text-amber-400',
      border: 'border-amber-500/30',
    },
    {
      id: 'failed',
      label: 'Failed Jobs',
      value: stats.failed,
      icon: AlertCircle,
      iconBg: 'bg-red-500/15',
      iconColor: 'text-red-400',
      border: 'border-red-500/30',
    },
  ]

  return (
    <div className="min-h-full bg-navy-950 p-6 md:p-8 space-y-8">
      {/* ── Greeting ─────────────────────────────────────────────────────── */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={16} className="text-brand-400" />
          <span className="text-xs font-semibold text-brand-400 uppercase tracking-widest">
            Dashboard
          </span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-white">
          Welcome back{user?.name ? `, ${user.name}` : ''}
        </h1>
        <p className="text-gray-400 mt-1 text-sm">
          Here's what's happening with your documents and RAG knowledge base today.
        </p>
      </div>

      {/* ── Stat cards ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS_CARDS.map(({ id, label, value, icon: Icon, iconBg, iconColor, border }) => (
          <div
            key={id}
            className={`bg-navy-900 border ${border} rounded-xl p-5 flex flex-col gap-4
              hover:border-navy-700 transition-all duration-200 hover:-translate-y-0.5`}
          >
            <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center`}>
              <Icon size={18} className={iconColor} />
            </div>
            <div>
              <p className="text-3xl font-bold text-white">{loading ? '—' : value}</p>
              <p className="text-xs text-gray-400 mt-0.5 font-medium">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Action cards ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Upload document */}
        <button
          onClick={() => navigate('/documents')}
          className="group text-left bg-navy-900 border border-navy-700 rounded-xl p-6
            hover:border-brand-500/50 hover:bg-navy-800 hover:scale-[1.01]
            transition-all duration-200 active:scale-100 cursor-pointer
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-brand-500/20 border border-brand-500/30
              flex items-center justify-center group-hover:bg-brand-500/30 transition-colors">
              <Upload size={22} className="text-brand-400" />
            </div>
            <ArrowRight
              size={16}
              className="text-gray-500 group-hover:text-brand-400 group-hover:translate-x-1
                transition-all duration-200 mt-1"
            />
          </div>
          <h2 className="text-base font-semibold text-white mb-1.5">
            Upload New Document
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            Upload PDFs, scanned forms, images, or documents. Dastavez parses text & tables, generates dense vectors, and indexes them for multi-source RAG.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-brand-400
            group-hover:text-cyan-400 transition-colors">
            Go to Documents
            <ArrowRight size={12} />
          </div>
        </button>

        {/* Start chatting */}
        <button
          onClick={() => navigate('/chat')}
          className="group text-left bg-navy-900 border border-navy-700 rounded-xl p-6
            hover:border-cyan-500/50 hover:bg-navy-800 hover:scale-[1.01]
            transition-all duration-200 active:scale-100 cursor-pointer
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/15 border border-cyan-500/30
              flex items-center justify-center group-hover:bg-cyan-500/25 transition-colors">
              <MessageSquare size={22} className="text-cyan-400" />
            </div>
            <ArrowRight
              size={16}
              className="text-gray-500 group-hover:text-cyan-400 group-hover:translate-x-1
                transition-all duration-200 mt-1"
            />
          </div>
          <h2 className="text-base font-semibold text-white mb-1.5">
            Start Conversational RAG Chat
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            Ask questions about your uploaded documents with source citations, page-level verification, and multi-turn context.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-cyan-400
            group-hover:text-white transition-colors">
            Open Chat
            <ArrowRight size={12} />
          </div>
        </button>
      </div>

      {/* ── Recent Activity section ──────────────────────────────────────── */}
      <div className="bg-navy-900 border border-navy-700 rounded-xl p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">Recent Documents</h2>
          <p className="text-sm text-gray-400 mt-0.5">Latest indexed documents in your repository</p>
        </div>

        {loading ? (
          <div className="py-8 flex items-center justify-center text-gray-500">
            <Loader2 size={24} className="animate-spin text-brand-400" />
          </div>
        ) : documents.length === 0 ? (
          <div className="py-8 text-center text-gray-500 text-sm">
            No recent activity yet. Upload a document to start indexing!
          </div>
        ) : (
          <div className="space-y-2.5">
            {documents.slice(0, 5).map((doc) => {
              const isCompleted = doc.status === 'COMPLETED'
              const isProcessing = doc.status === 'PROCESSING' || doc.status === 'PENDING'
              const isFailed = doc.status === 'FAILED'

              const dotColor = isCompleted
                ? 'bg-emerald-400'
                : isProcessing
                ? 'bg-amber-400 animate-pulse'
                : 'bg-red-400'

              const statusText = isCompleted
                ? `Processed (${doc.page_count ?? 1} pages)`
                : isProcessing
                ? 'Processing pipeline...'
                : 'Processing failed'

              return (
                <div
                  key={doc.id}
                  className="bg-navy-800 border border-navy-700/60 rounded-xl px-4 py-3.5 flex items-center justify-between
                    hover:border-navy-700 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${dotColor}`} />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-200 truncate">{doc.filename}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{statusText}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-gray-500 shrink-0 ml-4">
                    <Clock size={12} className="text-gray-600" />
                    <span>{formatRelativeTime(doc.created_at)}</span>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
