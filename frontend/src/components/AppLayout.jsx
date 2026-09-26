import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Home, FileText, MessageSquare } from 'lucide-react'
import Logo from './Logo'

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

  return (
    <div className="flex h-screen bg-navy-950 text-gray-100 overflow-hidden">
      {/* ── Sidebar ── */}
      <aside className="flex flex-col w-60 min-w-[15rem] bg-navy-900 border-r border-navy-700">
        {/* Logo */}
        <div className="flex items-center px-5 py-5 border-b border-navy-700">
          <Logo size="md" />
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

        {/* Footer */}
        <div className="px-5 py-4 border-t border-navy-700">
          <p className="text-xs text-gray-500">Dastavez v1.0</p>
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
