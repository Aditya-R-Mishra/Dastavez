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
} from 'lucide-react'

// ── Dummy data (replace with lib/api.js calls later) ──────────────────────────
const STATS = [
  {
    id: 'total',
    label: 'Total Documents',
    value: 5,
    icon: FileText,
    iconBg: 'bg-indigo-500/15',
    iconColor: 'text-indigo-400',
    border: 'border-indigo-500/20',
  },
  {
    id: 'processed',
    label: 'Processed',
    value: 4,
    icon: CheckCircle,
    iconBg: 'bg-emerald-500/15',
    iconColor: 'text-emerald-400',
    border: 'border-emerald-500/20',
  },
  {
    id: 'processing',
    label: 'Processing',
    value: 1,
    icon: Loader,
    iconBg: 'bg-amber-500/15',
    iconColor: 'text-amber-400',
    border: 'border-amber-500/20',
  },
  {
    id: 'failed',
    label: 'Failed',
    value: 0,
    icon: AlertCircle,
    iconBg: 'bg-red-500/15',
    iconColor: 'text-red-400',
    border: 'border-red-500/20',
  },
]

const Dashboard = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-full bg-gray-950 p-6 md:p-8">
      {/* ── Greeting ─────────────────────────────────────────────────────── */}
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-1">
          <Sparkles size={16} className="text-indigo-400" />
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">
            Dashboard
          </span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-white">
          Welcome back
        </h1>
        <p className="text-gray-400 mt-1 text-sm">
          Here's what's happening with your documents today.
        </p>
      </div>

      {/* ── Stat cards ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {STATS.map(({ id, label, value, icon: Icon, iconBg, iconColor, border }) => (
          <div
            key={id}
            className={`bg-gray-900 border ${border} rounded-xl p-5 flex flex-col gap-4
              hover:border-gray-600 transition-all duration-200 hover:-translate-y-0.5
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500`}
          >
            <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center`}>
              <Icon size={18} className={iconColor} />
            </div>
            <div>
              <p className="text-3xl font-bold text-white">{value}</p>
              <p className="text-xs text-gray-500 mt-0.5 font-medium">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Action cards ─────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Upload document */}
        <button
          onClick={() => navigate('/documents')}
          className="group text-left bg-gray-900 border border-gray-800 rounded-xl p-6
            hover:border-indigo-500/50 hover:bg-gray-800/60 hover:scale-[1.015]
            transition-all duration-200 active:scale-100
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30
              flex items-center justify-center group-hover:bg-indigo-600/30 transition-colors">
              <Upload size={22} className="text-indigo-400" />
            </div>
            <ArrowRight
              size={16}
              className="text-gray-600 group-hover:text-indigo-400 group-hover:translate-x-1
                transition-all duration-200 mt-1"
            />
          </div>
          <h2 className="text-base font-semibold text-white mb-1.5">
            Upload New Document
          </h2>
          <p className="text-sm text-gray-500 leading-relaxed">
            Upload PDFs, images, or scanned documents. Dastavez will process and index them for smart search and chat.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-indigo-400
            group-hover:text-indigo-300 transition-colors">
            Go to Documents
            <ArrowRight size={12} />
          </div>
        </button>

        {/* Start chatting */}
        <button
          onClick={() => navigate('/chat')}
          className="group text-left bg-gray-900 border border-gray-800 rounded-xl p-6
            hover:border-violet-500/50 hover:bg-gray-800/60 hover:scale-[1.015]
            transition-all duration-200 active:scale-100
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-violet-600/20 border border-violet-500/30
              flex items-center justify-center group-hover:bg-violet-600/30 transition-colors">
              <MessageSquare size={22} className="text-violet-400" />
            </div>
            <ArrowRight
              size={16}
              className="text-gray-600 group-hover:text-violet-400 group-hover:translate-x-1
                transition-all duration-200 mt-1"
            />
          </div>
          <h2 className="text-base font-semibold text-white mb-1.5">
            Start Chatting
          </h2>
          <p className="text-sm text-gray-500 leading-relaxed">
            Ask questions about your documents in plain English. Get instant, AI-powered answers with source references.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-violet-400
            group-hover:text-violet-300 transition-colors">
            Open Chat
            <ArrowRight size={12} />
          </div>
        </button>
      </div>
    </div>
  )
}

export default Dashboard
