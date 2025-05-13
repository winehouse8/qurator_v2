import type { Metadata } from 'next'
import { Pretendard } from '../lib/fonts'
import './globals.css'
import Providers from './providers'

export const metadata: Metadata = {
  title: 'Qurator',
  description: 'AI-powered content creation assistant',
  icons: {
    icon: '/assets/favicon.ico',
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={Pretendard.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
} 