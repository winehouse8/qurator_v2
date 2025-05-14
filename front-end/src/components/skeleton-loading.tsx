'use client'

/**
 * loading.tsx
 * ---------------------------------------------
 * 검색 결과를 기다리는 동안 ContentGrid 자리에 보여줄 Skeleton UI
 * - 상단 라벨 "카드 뉴스 생성 중…" 에 번쩍이는 그라디언트 효과
 * - 실제 카드와 동일한 크기·스케일로 회색 플래이스홀더 5장
 * Tailwind CSS 사용 (animate-pulse + 커스텀 keyframe)
 */

import React from 'react'

export default function SkeletonLoading() {
  /* ContentGrid 와 같은 축소 비율 */
  const scale = 1 / 4.5
  const skeletonCards = Array.from({ length: 5 })

  return (
    <div className="space-y-6">
      {/* 라벨 */}
      <div className="flex flex-col items-start gap-1.5">
        <h2
          className="
            text-lg font-semibold tracking-tighter
            text-transparent bg-clip-text
            bg-gradient-to-r from-muted via-foreground/30 to-muted
            bg-[length:200%_100%] animate-flash"
        >
          카드 뉴스 생성 중…
        </h2>
        <span className="text-sm text-muted">1080 × 1350</span>
      </div>

      {/* 스켈레톤 카드 그리드 */}
      <div
        className="overflow-x-auto pb-6 px-4 custom-scrollbar"
        style={{ overflowY: 'visible' }}
      >
        <div
          className="flex gap-3 py-6"
          style={{ overflow: 'visible' }}
        >
          {skeletonCards.map((_, i) => (
            <div
              key={i}
              className="inline-block"
              style={{
                width: 240,
                height: 300,
                // transform: `scale(${scale})`,
                // transformOrigin: 'top left',
              }}
            >
              <div className="w-full h-full rounded-sm bg-gray-300 animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}