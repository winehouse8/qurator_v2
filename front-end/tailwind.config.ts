import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/skeleton-loading.tsx',
  ],
  theme: {
    fontSize: {
      // Completely replacing default sizes
      'xs': ['12px', '16px'],      // [fontSize, lineHeight]
      'sm': ['13px', '1.5'],
      'base': ['16px', '1.5'],
      'lg': ['18px', '1.5'],
      'xl': ['20px', '32px'],
      // Add custom named sizes
      'title': ['28px', '34px'],
      'menu': ['15px', '22px'],
    },
    extend: {
      colors: {
        foreground: 'var(--foreground)',
        background: 'var(--background)',
        muted: 'var(--muted)',
        border: 'var(--border)',
        'input-bg': 'var(--input-bg)',
        hover: 'var(--hover)',
        active: 'var(--active)',
      },
      letterSpacing: {
        tighter: '-0.02em',
      },
      keyframes: {
        flash: {
          '0%, 100%': { backgroundPosition: '0% 0%' },
          '50%': { backgroundPosition: '100% 0%' },
        },
      },
      animation: {
        'flash': 'flash 1.2s linear infinite',
      },
    },
  },
  plugins: [],
}

export default config 