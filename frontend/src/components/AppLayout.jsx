import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Home, FileText, MessageSquare, LogOut, User } from 'lucide-react'
import Logo from './Logo'
import { authStorage } from '../lib/api'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: Home },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/chat',      label: 'Chat',      icon: MessageSquare },
]

// ── Page fade variant — consistent 200ms across all routes ───────────────────
const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.2, ease: 'easeOut' } },
  exit:    { opacity: 0, y: -4, transition: { duration: 0.15, ease: 'easeIn' } },
}

const AppLayout = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const user = authStorage.getUser()

  const handleLogout = () => {
    authStorage.clear()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-navy-950 text-gray-100 overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="flex flex-col w-60 min-w-[15rem] bg-navy-900 border-r border-navy-700">
        {/* Logo */}
        <div className="flex items-center px-5 py-5 border-b border-navy-700">
          <Logo size="lg" />
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                [
                  'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200',
                  'focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                  isActive
                    ? 'bg-gradient-to-r from-brand-500 to-brand-400 text-white shadow-md shadow-brand-500/25 font-semibold'
                    : 'text-gray-400 hover:text-white hover:bg-navy-800',
                ].join(' ')
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    size={18}
                    className={`transition-colors duration-200 ${isActive ? 'text-white' : 'text-gray-400'}`}
                  />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer / User & Logout */}
        <div className="px-4 py-3 border-t border-navy-700 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-8 h-8 rounded-full bg-brand-500/20 border border-brand-500/40 flex items-center justify-center shrink-0">
              <User size={15} className="text-brand-400" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-gray-200 truncate">
                {user?.name || user?.email?.split('@')[0] || 'User'}
              </p>
              <p className="text-[10px] text-gray-500 truncate">{user?.email || 'Logged In'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log out"
            className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors cursor-pointer"
          >
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* ── Main content with page transition ── */}
      <main className="flex-1 overflow-y-auto">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={location.pathname}
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className="h-full"
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default AppLayout
