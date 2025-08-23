import * as React from "react"
import { cn } from "@/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Разрешить только латинские буквы (A-Z, a-z). Все остальные символы отфильтровываются на вводе.
   */
  onlyLatin?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, onChange, onlyLatin, ...props }, ref) => {
    const handleChange = React.useCallback(
      (e: React.ChangeEvent<HTMLInputElement>) => {
        if (onlyLatin) {
          const sanitized = e.target.value.replace(/[^A-Za-z]/g, "")
          if (sanitized !== e.target.value) {
            e.target.value = sanitized
          }
        }
        onChange?.(e)
      },
      [onChange, onlyLatin]
    )

    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        onChange={handleChange}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

export { Input }


