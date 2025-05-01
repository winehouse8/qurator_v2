import Image from 'next/image'
import Link from 'next/link'

export function Logo() {
  return (
    <Link href="/" className="w-[24px] h-[24px] relative block hover:opacity-80 transition-opacity">
      <Image
        src="/assets/logo.svg"
        alt="Qurator Logo"
        fill
        className="object-contain"
        priority
      />
    </Link>
  )
} 