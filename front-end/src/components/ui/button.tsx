import { forwardRef } from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'small' | 'icon' | 'submit'
  className?: string
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, className = '', children, ...props }, ref) => {
    const baseClass = variant ? `btn-${variant}` : 'btn-small'
    
    return (
      <button
        ref={ref}
        className={`${baseClass} ${className}`}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button } 