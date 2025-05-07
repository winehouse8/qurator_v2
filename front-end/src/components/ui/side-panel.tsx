import { ReactNode } from 'react'

interface SidePanelProps {
  children: ReactNode
  className?: string
}

export function SidePanel({ children, className }: SidePanelProps) {
  return (
    <aside className={`h-screen p-6 flex flex-col items-center bg-background  ${className ?? ''}`}>
      {children}
    </aside>
  )
} 