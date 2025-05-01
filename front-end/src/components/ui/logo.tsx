import Image from 'next/image'

export function Logo() {
  return (
    <div className="w-[24px] h-[24px] relative">
      <Image
        src="/assets/logo.svg"
        alt="Qurator Logo"
        fill
        className="object-contain"
        priority
      />
    </div>
  )
} 