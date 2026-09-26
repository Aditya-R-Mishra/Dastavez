import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import AppLayout from './components/AppLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Documents from './pages/Documents'
import Chat from './pages/Chat'

function App() {
  return (
    <BrowserRouter>
      {/* ── Global toast notifications ── */}
      <Toaster
        position="top-right"
        gutter={8}
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1f2937',   // gray-800
            color: '#f9fafb',        // gray-50
            border: '1px solid #374151', // gray-700
            borderRadius: '0.75rem',
            fontSize: '0.875rem',
            boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
          },
          success: {
            iconTheme: { primary: '#34d399', secondary: '#1f2937' }, // emerald-400
          },
          error: {
            iconTheme: { primary: '#f87171', secondary: '#1f2937' }, // red-400
          },
        }}
      />

      <Routes>
        {/* Standalone — no sidebar */}
        <Route path="/login" element={<Login />} />

        {/* App shell — sidebar + content */}
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/chat" element={<Chat />} />
        </Route>

        {/* Fallback */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
