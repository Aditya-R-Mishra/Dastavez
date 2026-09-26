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
} from 'lucide-react'

// ── Dummy stats data ──────────────────────────────────────────────────────────
const STATS = [
  {
    id: 'total',
    label: 'Total Documents',
    value: 5,
    icon: FileText,
    iconBg: 'bg-brand-500/15',
    iconColor: 'text-brand-400',
    border: 'border-brand-500/30',
  },
  {
    id: 'processed',
    label: 'Processed',
    value: 4,
    icon: CheckCircle,
    iconBg: 'bg-emerald-500/15',
    iconColor: 'text-emerald-400',
    border: 'border-emerald-500/30',
  },
  {
    id: 'processing',
    label: 'Processing',
    value: 1,
    icon: Loader,
    iconBg: 'bg-amber-500/15',
    iconColor: 'text-amber-400',
    border: 'border-amber-500/30',
  },
  {
    id: 'failed',
    label: 'Failed',
    value: 0,
    icon: AlertCircle,
    iconBg: 'bg-red-500/15',
    iconColor: 'text-red-400',
    border: 'border-red-500/30',
  },
]

// ── Dummy recent activity data ───────────────────────────────────────────────
const RECENT_ACTIVITY = [
  { file: 'HR_Policy.pdf', status: 'Processing completed', type: 'success', time: '2 min ago' },
  { file: 'scanned_claim_form.jpg', status: 'OCR processing', type: 'processing', time: '5 min ago' },
  { file: 'Expense_Policy.pdf', status: 'Uploaded', type: 'uploaded', time: '12 min ago' },
]

const Dashboard = () => {
  const navigate = useNavigate()

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
          Welcome back
        </h1>
        <p className="text-gray-400 mt-1 text-sm">
          Here's what's happening with your documents today.
        </p>
      </div>

      {/* ── Stat cards ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STATS.map(({ id, label, value, icon: Icon, iconBg, iconColor, border }) => (
          <div
            key={id}
            className={`bg-navy-900 border ${border} rounded-xl p-5 flex flex-col gap-4
              hover:border-navy-700 transition-all duration-200 hover:-translate-y-0.5`}
          >
            <div className={`w-10 h-10 rounded-lg ${iconBg} flex items-center justify-center`}>
              <Icon size={18} className={iconColor} />
            </div>
            <div>
              <p className="text-3xl font-bold text-white">{value}</p>
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
            Upload PDFs, images, or scanned documents. Dastavez will process and index them for smart search and chat.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-brand-400
            group-hover:text-brand-cyan transition-colors">
            Go to Documents
            <ArrowRight size={12} />
          </div>
        </button>

        {/* Start chatting */}
        <button
          onClick={() => navigate('/chat')}
          className="group text-left bg-navy-900 border border-navy-700 rounded-xl p-6
            hover:border-brand-cyan/50 hover:bg-navy-800 hover:scale-[1.01]
            transition-all duration-200 active:scale-100 cursor-pointer
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-cyan"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-brand-cyan/15 border border-brand-cyan/30
              flex items-center justify-center group-hover:bg-brand-cyan/25 transition-colors">
              <MessageSquare size={22} className="text-brand-cyan" />
            </div>
            <ArrowRight
              size={16}
              className="text-gray-500 group-hover:text-brand-cyan group-hover:translate-x-1
                transition-all duration-200 mt-1"
            />
          </div>
          <h2 className="text-base font-semibold text-white mb-1.5">
            Start Chatting
          </h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            Ask questions about your documents in plain English. Get instant, AI-powered answers with source references.
          </p>
          <div className="mt-4 flex items-center gap-1.5 text-xs font-medium text-brand-cyan
            group-hover:text-white transition-colors">
            Open Chat
            <ArrowRight size={12} />
          </div>
        </button>
      </div>

      {/* ── Recent Activity section ──────────────────────────────────────── */}
      <div className="bg-navy-900 border border-navy-700 rounded-xl p-6">
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-white">Recent Activity</h2>
          <p className="text-sm text-gray-400 mt-0.5">Latest updates across your documents</p>
        </div>

        <div className="space-y-2.5">
          {RECENT_ACTIVITY.map((item, index) => {
            const dotColor =
              item.type === 'success'
                ? 'bg-emerald-400'
                : item.type === 'processing'
                  ? 'bg-amber-400 animate-pulse'
                  : 'bg-brand-400'

            return (
              <div
                key={index}
                className="bg-navy-800 border border-navy-700/60 rounded-xl px-4 py-3.5 flex items-center justify-between
                  hover:border-navy-700 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${dotColor}`} />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-200 truncate">{item.file}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{item.status}</p>
                  </div>
                </div>

                <div className="flex items-center gap-1.5 text-xs text-gray-500 shrink-0 ml-4">
                  <Clock size={12} className="text-gray-600" />
                  <span>{item.time}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
