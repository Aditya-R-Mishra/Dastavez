import React from 'react'

const Logo = ({ size = 'md', showText = true, className = '' }) => {
  const iconSizes = {
    sm: 'w-7 h-7',
    md: 'w-8 h-8',
    lg: 'w-10 h-10',
  }

  const textSizes = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-xl',
  }

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <div className={`${iconSizes[size] || iconSizes.md} rounded-xl bg-brand-500/20 border border-brand-500/30 flex items-center justify-center p-1 shrink-0 shadow-sm shadow-brand-500/20`}>
        <img src="/logo.png" alt="Dastavez Logo" className="w-full h-full object-contain" />
      </div>
      {showText && (
        <span className={`${textSizes[size] || textSizes.md} font-bold tracking-tight text-white`}>
          Dastavez
        </span>
      )}
    </div>
  )
}

export default Logo
