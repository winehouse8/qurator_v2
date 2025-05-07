'use client'

import { useRef } from 'react'
import { ContentCard } from './content-card'
import { ContentDownloader } from './content-downloader'

interface ContentGridProps {
  onEdit: (index: number) => void
  category: string
  cards: any[]
  selectedImageIndices?: number[]
}

export function ContentGrid({ onEdit, category, cards, selectedImageIndices = [] }: ContentGridProps) {
  const cardRefs = useRef<(HTMLDivElement | null)[]>([])
  const hiddenCardRefs = useRef<(HTMLDivElement | null)[]>([])

  const scale = 1/4.5;

  const handleCardClick = (index: number, isNew: boolean) => {
    // Don't allow editing if the card is marked as new
    if (!isNew) {
      onEdit(index);
    }
  };

  return (
    <div className="space-y-6">
      {/* Label */}
      <div className="flex flex-col items-start gap-1.5">
        <h2 className="text-lg font-semibold tracking-tighter">카드 뉴스</h2>
        <span className="text-sm text-muted">1080 × 1350</span>
      </div>
      {/* Grid */}
      <div className="overflow-x-auto pb-6 px-4 custom-scrollbar" style={{ overflowY: 'visible' }}>
        <div className="flex gap-3 py-6" style={{ overflow: 'visible' }}>
          {cards.map((card, i) => (
            <div
              key={i}
              className={`inline-block ${!card.isNew ? 'cursor-pointer' : 'cursor-default'}`}
              style={{
                width: 240,
                height: 300,
                transform: `scale(${scale})`,
                transformOrigin: 'top left',
              }}
              onClick={() => handleCardClick(i, !!card.isNew)}
            >
              <ContentCard
                ref={el => { cardRefs.current[i] = el }}
                card={card}
                category={category}
                isNew={!!card.isNew}
                selectedImageIndex={selectedImageIndices[i] || 0}
              />
            </div>
          ))}
        </div>
      </div>      
      {/* Hidden cards for download */}
      <div style={{ position: 'absolute', left: '-9999px', top: 0 }}>
        {cards.map((card, i) => (
          <ContentCard
            key={i}
            ref={el => { hiddenCardRefs.current[i] = el }}
            card={card}
            category={category}
            selectedImageIndex={selectedImageIndices[i] || 0}
          />
        ))}
      </div>
      {/* Download Button */}
      <div className="flex justify-center pt-4">
        <ContentDownloader cardRefs={hiddenCardRefs.current} />
      </div>
    </div>
  )
}