'use client'

import { useRef } from 'react'
import { ContentCard } from './content-card'
import html2canvas from 'html2canvas'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { ContentDownloader } from './content-downloader'

const CARD_TEXT =
  '미·우크라, 30일 휴전 합의·미 군사지원 재개…러시아 수락 변수 부각'

export function ContentGrid() {
  const cardRefs = useRef<(HTMLDivElement | null)[]>([])
  const hiddenCardRefs = useRef<(HTMLDivElement | null)[]>([])

  // 카드 데이터
  const cards = [
    ...Array(5).fill(CARD_TEXT),
    '새로운 콘텐츠'
  ]

  return (
    <div className="space-y-6">
      {/* Label */}
      <div className="flex flex-col items-start gap-1.5">
        <h2 className="text-lg font-semibold tracking-tighter">콘텐츠</h2>
        <span className="text-sm text-muted">1080 × 1350</span>
      </div>
      {/* Grid */}
      <div className="overflow-x-auto pb-6 px-4" style={{ overflowY: 'visible' }}>
        <div className="flex gap-3 py-6" style={{ overflow: 'visible' }}>
          {cards.map((text, i) => (
            <div
              key={i}
              className="inline-block"
              style={{
                width: 240,
                height: 300,
                transform: 'scale(0.222)',
                transformOrigin: 'top left',
              }}
            >
              <ContentCard
                ref={el => { cardRefs.current[i] = el }}
                isNew={i === cards.length - 1}
              >
                {text}
              </ContentCard>
            </div>
          ))}
        </div>
      </div>      
      {/* Hidden cards for download */}
      <div style={{ position: 'absolute', left: '-9999px', top: 0 }}>
        {cards.slice(0, -1).map((text, i) => (
          <ContentCard
            key={i}
            ref={el => { hiddenCardRefs.current[i] = el }}
          >
            {text}
          </ContentCard>
        ))}
      </div>
      {/* Download Button */}
      <div className="flex justify-center pt-4">
        <ContentDownloader cardRefs={hiddenCardRefs.current} />
      </div>
    </div>
  )
}