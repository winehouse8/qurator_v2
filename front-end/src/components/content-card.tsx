import { ReactNode, forwardRef } from 'react'
import cn from 'classnames'

interface ContentCardProps {
  children: ReactNode
  isNew?: boolean
  className?: string
}

export const ContentCard = forwardRef<HTMLDivElement, ContentCardProps>(
  function ContentCard({ children, isNew, className }, ref) {
    return (
      <div
        ref={ref}
        className={cn(
          'shadow-[0_24px_48px_rgba(0,0,0,0.20)] overflow-hidden flex flex-col items-center justify-center bg-background',
          isNew ? 'rounded-2xl shadow-transparent border-8 border-dashed border-border' : 'border-transparent',
          className
        )}
        style={{
          width: 1080,
          height: 1350,
          background: isNew
            ? 'white'
            : 'linear-gradient(180deg, #FFF 40%, #000 100%)',
        }}
      >
        <div className="h-[1080px] p-[64px] flex items-end justify-center">
          <p className={cn(
            "text-[84px] leading-[1.4] font-bold tracking-[-0.04em] text-left break-keep select-none",
            isNew ? 'text-muted' : 'text-background',
            className)}>
            {children}
          </p>
        </div>
      </div>
    )
  }
) 