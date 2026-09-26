import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  FileText,
  Sparkles,
  Globe,
  Search,
  Bot,
  ShieldCheck,
} from 'lucide-react'

const Login = () => {
  const navigate = useNavigate()
  const [isActive, setIsActive] = useState(false) // false = Login, true = Sign-up

  // Form states
  const [loginData, setLoginData] = useState({ username: '', password: '' })
  const [registerData, setRegisterData] = useState({ username: '', password: '' })

  const handleRegisterClick = () => {
    setIsActive(true) // Switches to Sign-up
  }

  const handleLoginClick = () => {
    setIsActive(false) // Switches to Login
  }

  const handleLoginSubmit = (e) => {
    e.preventDefault()
    navigate('/dashboard')
  }

  const handleRegisterSubmit = (e) => {
    e.preventDefault()
    navigate('/dashboard')
  }

  return (
    <div className="login-page-wrapper">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');

        .login-page-wrapper {
          min-height: 100vh;
          width: 100vw;
          background: #090d16;
          background: radial-gradient(circle at 50% 50%, #111827 0%, #030712 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          font-family: 'Montserrat', sans-serif;
          overflow: hidden;
          padding: 20px;
        }

        .sliding-container {
          background-color: #111827;
          border: 1px solid #1f2937;
          border-radius: 30px;
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(99, 102, 241, 0.25);
          position: relative;
          overflow: hidden;
          width: 820px;
          max-width: 100%;
          min-height: 520px;
        }

        .sliding-container p {
          font-size: 14px;
          line-height: 22px;
          letter-spacing: 0.3px;
          margin: 14px 0;
          color: #9ca3af;
        }

        .sliding-container span {
          font-size: 12px;
          color: #6b7280;
        }

        .sliding-container a.forgot-link {
          color: #818cf8;
          font-size: 13px;
          text-decoration: none;
          margin: 10px 0 6px;
          transition: color 0.2s;
        }

        .sliding-container a.forgot-link:hover {
          color: #a5b4fc;
        }

        .sliding-container button.action-btn {
          background-color: #4f46e5;
          color: #ffffff;
          font-size: 13px;
          padding: 12px 45px;
          border: 1px solid transparent;
          border-radius: 10px;
          font-weight: 600;
          letter-spacing: 0.8px;
          text-transform: uppercase;
          margin-top: 10px;
          cursor: pointer;
          transition: all 0.25s ease;
          box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
        }

        .sliding-container button.action-btn:hover {
          background-color: #4338ca;
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45);
        }

        /* Overlay toggle outline button (renamed from .hidden to avoid Tailwind v4 collision) */
        .sliding-container button.toggle-btn-outline {
          background-color: transparent !important;
          border: 1.5px solid #ffffff !important;
          color: #ffffff !important;
          box-shadow: none !important;
          display: inline-block !important;
        }

        .sliding-container button.toggle-btn-outline:hover {
          background-color: rgba(255, 255, 255, 0.15) !important;
          transform: translateY(-1px);
        }

        .sliding-container form {
          background-color: #111827;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          padding: 0 40px;
          height: 100%;
        }

        .sliding-container form h1 {
          color: #f9fafb;
          font-size: 24px;
          font-weight: 700;
          letter-spacing: -0.5px;
          margin-bottom: 2px;
        }

        .sliding-container input {
          background-color: #1f2937;
          border: 1px solid #374151;
          color: #f3f4f6;
          margin: 6px 0;
          padding: 11px 15px;
          font-size: 13px;
          border-radius: 10px;
          width: 100%;
          outline: none;
          transition: all 0.2s;
        }

        .sliding-container input:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }

        .form-container {
          position: absolute;
          top: 0;
          height: 100%;
          transition: all 0.6s ease-in-out;
        }

        .sign-in {
          left: 0;
          width: 50%;
          z-index: 2;
        }

        .sliding-container.active .sign-in {
          transform: translateX(100%);
        }

        .sign-up {
          left: 0;
          width: 50%;
          opacity: 0;
          z-index: 1;
        }

        .sliding-container.active .sign-up {
          transform: translateX(100%);
          opacity: 1;
          z-index: 5;
          animation: move 0.6s;
        }

        @keyframes move {
          0%, 49.99% {
            opacity: 0;
            z-index: 1;
          }
          50%, 100% {
            opacity: 1;
            z-index: 5;
          }
        }

        .social-icons {
          margin: 12px 0;
          display: flex;
          gap: 10px;
        }

        .social-icons .icon-badge {
          border: 1px solid #374151;
          background-color: #1f2937;
          border-radius: 12px;
          display: inline-flex;
          justify-content: center;
          align-items: center;
          width: 40px;
          height: 40px;
          color: #818cf8;
          transition: all 0.2s;
        }

        .social-icons .icon-badge:hover {
          border-color: #6366f1;
          background-color: rgba(99, 102, 241, 0.15);
          color: #a5b4fc;
          transform: translateY(-2px);
        }

        .toggle-container {
          position: absolute;
          top: 0;
          left: 50%;
          width: 50%;
          height: 100%;
          overflow: hidden;
          transition: all 0.6s ease-in-out;
          border-radius: 150px 0 0 100px;
          z-index: 1000;
        }

        .sliding-container.active .toggle-container {
          transform: translateX(-100%);
          border-radius: 0 150px 100px 0;
        }

        .toggle {
          background: linear-gradient(135deg, #4f46e5 0%, #4338ca 50%, #3730a3 100%);
          color: #ffffff;
          position: relative;
          left: -100%;
          height: 100%;
          width: 200%;
          transform: translateX(0);
          transition: all 0.6s ease-in-out;
        }

        .sliding-container.active .toggle {
          transform: translateX(50%);
        }

        .toggle-panel {
          position: absolute;
          width: 50%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          padding: 0 35px;
          text-align: center;
          top: 0;
          transform: translateX(0);
          transition: all 0.6s ease-in-out;
        }

        .toggle-panel h1 {
          font-size: 26px;
          font-weight: 700;
          margin-bottom: 6px;
          color: #ffffff;
        }

        .toggle-panel p {
          color: #e0e7ff !important;
          font-size: 13px;
        }

        .toggle-left {
          transform: translateX(-200%);
        }

        .sliding-container.active .toggle-left {
          transform: translateX(0);
        }

        .toggle-right {
          right: 0;
          transform: translateX(0);
        }

        .sliding-container.active .toggle-right {
          transform: translateX(200%);
        }

        /* Role Selection Styling */
        .role-dropdown-container {
          width: 100%;
          position: relative;
          margin: 6px 0;
        }

        .role-display-button {
          background-color: #1f2937 !important;
          color: #9ca3af !important;
          border: 1px solid #374151 !important;
          width: 100%;
          padding: 11px 15px !important;
          font-size: 13px !important;
          border-radius: 10px !important;
          font-weight: 400 !important;
          text-transform: none !important;
          text-align: left;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: space-between;
          transition: all 0.2s;
        }

        .role-display-button.selected {
          font-weight: 600 !important;
          color: #f3f4f6 !important;
          border-color: #6366f1 !important;
        }

        .role-options {
          position: absolute;
          top: calc(100% + 4px);
          left: 0;
          width: 100%;
          background-color: #1f2937;
          border: 1px solid #4f46e5;
          border-radius: 10px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
          z-index: 100;
          padding: 6px;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .role-options button {
          background-color: transparent !important;
          color: #d1d5db !important;
          border: none !important;
          width: 100%;
          padding: 9px 12px !important;
          font-size: 13px !important;
          text-transform: none !important;
          text-align: left;
          border-radius: 6px !important;
          margin-top: 0 !important;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .role-options button:hover {
          background-color: #374151 !important;
          color: #818cf8 !important;
        }

        .switch-prompt {
          font-size: 12px;
          color: #9ca3af;
          margin-top: 14px;
        }

        .switch-prompt button {
          background: none;
          border: none;
          color: #818cf8;
          font-weight: 600;
          cursor: pointer;
          margin-left: 4px;
          text-decoration: underline;
        }

        .switch-prompt button:hover {
          color: #a5b4fc;
        }
      `}</style>

      <div className={`sliding-container ${isActive ? 'active' : ''}`} id="container">
        {/* ── Registration Form (Sign-up) ─────────────────────────────────── */}
        <div className="form-container sign-up">
          <form onSubmit={handleRegisterSubmit}>
            <div className="flex items-center gap-2 mb-1">
              <img src="/logo.png" alt="Dastavez Logo" className="w-8 h-8 object-contain rounded-lg drop-shadow" />
              <span className="text-base font-bold text-white tracking-wider">DASTAVEZ</span>
            </div>

            <h1>SIGN UP</h1>

            <div className="social-icons">
              <span className="icon-badge" title="Document Processing">
                <FileText size={17} />
              </span>
              <span className="icon-badge" title="AI Search">
                <Search size={17} />
              </span>
              <span className="icon-badge" title="Regional Languages">
                <Globe size={17} />
              </span>
              <span className="icon-badge" title="Multi-source Evidence">
                <Sparkles size={17} />
              </span>
            </div>

            <input
              type="text"
              placeholder="Username / Email"
              required
              value={registerData.username}
              onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
            />
            <input
              type="password"
              placeholder="Password"
              required
              value={registerData.password}
              onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
            />

            <button type="submit" className="action-btn">
              SIGN UP
            </button>

            <p className="switch-prompt">
              Already have an account?
              <button type="button" onClick={handleLoginClick}>
                Login
              </button>
            </p>
          </form>
        </div>

        {/* ── Login Form (Sign-in) ────────────────────────────────────────── */}
        <div className="form-container sign-in">
          <form onSubmit={handleLoginSubmit}>
            <div className="flex items-center gap-2 mb-1">
              <img src="/logo.png" alt="Dastavez Logo" className="w-8 h-8 object-contain rounded-lg drop-shadow" />
              <span className="text-base font-bold text-white tracking-wider">DASTAVEZ</span>
            </div>

            <h1>Login</h1>

            <div className="social-icons">
              <span className="icon-badge" title="AI Assistant">
                <Bot size={17} />
              </span>
              <span className="icon-badge" title="Multi-Source Search">
                <Search size={17} />
              </span>
              <span className="icon-badge" title="Security Guaranteed">
                <ShieldCheck size={17} />
              </span>
              <span className="icon-badge" title="OCR Text Extraction">
                <FileText size={17} />
              </span>
            </div>

            <span>Enter your credentials</span>

            <input
              type="text"
              placeholder="Username / Email"
              required
              value={loginData.username}
              onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
            />
            <input
              type="password"
              placeholder="Password"
              required
              value={loginData.password}
              onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
            />

            <a href="#" className="forgot-link" onClick={(e) => e.preventDefault()}>
              Forgot Your Password?
            </a>

            <button type="submit" className="action-btn">
              Login
            </button>

            <p className="switch-prompt">
              Don't have an account?
              <button type="button" onClick={handleRegisterClick}>
                Sign up
              </button>
            </p>
          </form>
        </div>

        {/* ── Sliding Toggle Container ────────────────────────────────────── */}
        <div className="toggle-container">
          <div className="toggle">
            {/* Panel visible when showing the LOGIN form (sign-in) */}
            <div className="toggle-panel toggle-left">
              <h1>Welcome Back!</h1>
              <p>Access your Dastavez document intelligence dashboard &amp; AI chat search</p>
              <button type="button" className="action-btn toggle-btn-outline" onClick={handleLoginClick}>
                Login
              </button>
            </div>

            {/* Panel visible when showing the REGISTER form (sign-up) */}
            <div className="toggle-panel toggle-right">
              <h1>Welcome to Dastavez!</h1>
              <p>Smart Document Intelligence, Regional Language Search &amp; RAG Answers</p>
              <button type="button" className="action-btn toggle-btn-outline" onClick={handleRegisterClick}>
                SIGN UP
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
