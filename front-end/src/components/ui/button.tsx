import { forwardRef } from 'react'
import cn from 'classnames'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'small' | 'icon' | 'submit'
  className?: string
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant, className = '', children, ...props }, ref) => {
    const variantClasses = {
      small: 'bg-input-bg text-sm text-muted font-medium rounded-[8px] py-1 px-2 border-[1px] border-border transition-colors duration-100 hover:bg-hover active:bg-[#DFDFDF]',
      icon: 'inline-flex items-center justify-center rounded-lg p-1.5 transition-colors duration-100 hover:bg-[#EEEEEE] active:bg-[#DFDFDF] gap-2.5',
      submit: 'bg-foreground rounded-full flex items-center justify-center'
    }
    
    const baseClass = variant ? variantClasses[variant] : variantClasses.small
    
    return (
      <button
        ref={ref}
        className={cn(baseClass, className)}
        {...props}
      >
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button } 