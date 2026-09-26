import React from 'react'

const Logo = ({ size = 'md', showText = true, className = '' }) => {
  const iconSizes = {
    sm: 'w-8 h-8 p-1',
    md: 'w-10 h-10 p-1.5',
    lg: 'w-12 h-12 p-1.5',
    xl: 'w-16 h-16 p-2',
  }

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl',
  }

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className={`${iconSizes[size] || iconSizes.md} rounded-xl bg-brand-500/20 border border-brand-500/35 flex items-center justify-center shrink-0 shadow-md shadow-brand-500/25`}>
        <img src="/logo.png" alt="Dastavez Logo" className="w-full h-full object-contain drop-shadow" />
      </div>
      {showText && (
        <span className={`${textSizes[size] || textSizes.md} font-extrabold tracking-wide text-white uppercase`}>
          Dastavez
        </span>
      )}
    </div>
  )
}

export default Logo
