import React from 'react'

/** Shown while a screen's data loads. */
export const LoadingView: React.FC<{ label?: string }> = ({ label = 'Loading…' }) => (
  <div role="status" className="flex-1 flex items-center justify-center p-10 text-[14px] text-[#5A6A60]">
    <span className="w-2 h-2 rounded-full bg-[#3E6B53] animate-pulse mr-2" />
    {label}
  </div>
)

/** Shown when a screen's data failed to load. */
export const ErrorView: React.FC<{ message: string; onRetry?: () => void }> = ({ message, onRetry }) => (
  <div role="alert" className="m-6 p-4 rounded-[20px] bg-[#FDE8E4] text-[#A02A1C] flex flex-col gap-2">
    <p className="m-0 text-[14px] leading-relaxed">{message}</p>
    {onRetry && (
      <button
        type="button"
        onClick={onRetry}
        className="self-start min-h-[40px] px-4 rounded-[12px] bg-white border border-[#E8B4AC] text-[14px] font-semibold text-[#A02A1C] cursor-pointer"
      >
        Try again
      </button>
    )}
  </div>
)
