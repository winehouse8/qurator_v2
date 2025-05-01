export function ContentGrid() {
  return (
    <div className="space-y-12">
      {/* Label */}
      <div className="flex flex-col items-start gap-1.5">
        <h2 className="text-lg font-semibold tracking-tighter">콘텐츠</h2>
        <span className="text-sm text-muted">1080 × 1350</span>
      </div>

      {/* Grid */}
      <div className="flex gap-3 overflow-x-auto pb-6">
        {/* Placeholder Cards */}
        {[...Array(6)].map((_, i) => (
            <div 
            key={i} 
            className={`
            flex-shrink-0 w-[240px] h-[300px] flex flex-col justify-center border-2
            ${i === 5 ? 'border-dashed border-border' : 'border-transparent'} 
            bg-background shadow-lg overflow-hidden`}>
                <div
                    className={`
                    flex-shrink-0 w-[240px] h-[240px]
                    bg-background overflow-hidden
                    `}
                >
                    <div className="h-full p-[22px] flex items-end">
                    <p className="text-[18.67px] leading-[1.3] font-bold tracking-[-0.04em] text-foreground">
                        {i === 5 ? '새로운 콘텐츠' : '미·우크라, 30일 휴전 합의·미 군사지원 재개…러시아 수락 변수 부각'}
                    </p>
                    </div>
                </div>
          </div>
        ))}
      </div>
    </div>
  )
} 