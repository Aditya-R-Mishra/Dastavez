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
import Logo from '../components/Logo'

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
          background: #070B14;
          background: radial-gradient(circle at 50% 50%, #0D1524 0%, #070B14 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-direction: column;
          font-family: 'Montserrat', sans-serif;
          overflow: hidden;
          padding: 20px;
        }

        .sliding-container {
          background-color: #0D1524;
          border: 1px solid #162238;
          border-radius: 30px;
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.7), 0 0 30px rgba(37, 99, 235, 0.2);
          position: relative;
          overflow: hidden;
          width: 840px;
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
          color: #3B82F6;
          font-size: 13px;
          text-decoration: none;
          margin: 10px 0 6px;
          transition: color 0.2s;
        }

        .sliding-container a.forgot-link:hover {
          color: #60A5FA;
        }

        .sliding-container button.action-btn {
          background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
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
          box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        }

        .sliding-container button.action-btn:hover {
          background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
          transform: translateY(-1px);
          box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45);
        }

        .sliding-container form {
          background-color: #0D1524;
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
          background-color: #111B2B;
          border: 1px solid #162238;
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
          border-color: #2563EB;
          box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
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
          border: 1px solid #162238;
          background-color: #111B2B;
          border-radius: 12px;
          display: inline-flex;
          justify-content: center;
          align-items: center;
          width: 40px;
          height: 40px;
          color: #3B82F6;
          transition: all 0.2s;
        }

        .social-icons .icon-badge:hover {
          border-color: #2563EB;
          background-color: rgba(37, 99, 235, 0.15);
          color: #60A5FA;
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
          background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 50%, #0F172A 100%);
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
          margin-bottom: 12px;
          color: #ffffff;
          line-height: 1.3;
        }

        .toggle-panel p {
          color: #DBEAFE !important;
          font-size: 13.5px;
          line-height: 1.6;
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

        .switch-prompt {
          font-size: 12px;
          color: #9ca3af;
          margin-top: 14px;
        }

        .switch-prompt button {
          background: none;
          border: none;
          color: #3B82F6;
          font-weight: 600;
          cursor: pointer;
          margin-left: 4px;
          text-decoration: underline;
        }

        .switch-prompt button:hover {
          color: #60A5FA;
        }
      `}</style>

      <div className={`sliding-container ${isActive ? 'active' : ''}`} id="container">
        {/* ── Registration Form (Sign-up) ─────────────────────────────────── */}
        <div className="form-container sign-up">
          <form onSubmit={handleRegisterSubmit}>
            <div className="mb-2">
              <Logo size="sm" />
            </div>

            <h1>Create your Dastavez account</h1>

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
              CREATE ACCOUNT
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
            <div className="mb-2">
              <Logo size="sm" />
            </div>

            <h1>Welcome back</h1>

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
            {/* Left overlay panel (evergreen copy) */}
            <div className="toggle-panel toggle-left">
              <h1>Your documents. One intelligent workspace.</h1>
              <p>Upload documents, search across sources, and get evidence-backed answers with AI.</p>
            </div>

            {/* Right overlay panel (evergreen copy) */}
            <div className="toggle-panel toggle-right">
              <h1>Your documents. One intelligent workspace.</h1>
              <p>Upload documents, search across sources, and get evidence-backed answers with AI.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
