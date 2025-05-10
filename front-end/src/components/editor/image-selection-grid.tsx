import Image from 'next/image'
import { useState } from 'react'

interface ImageSelectionGridProps {
  imageUrls: string[]
  refUrls?: string[]
  imgDescs?: string[]
  selectedImageIndex: number
  onSelect: (index: number) => void
}

export function ImageSelectionGrid({
  imageUrls,
  refUrls = [],
  imgDescs = [],
  selectedImageIndex,
  onSelect,
}: ImageSelectionGridProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  // Split images into two columns
  const columns = [[], []] as string[][]
  imageUrls.forEach((url, idx) => columns[idx % 2].push(url))

  return (
    <div className="flex flex-row gap-2 max-h-[450px] overflow-y-auto rounded-xl">
      {columns.map((col, colIdx) => (
        <div className="flex flex-col gap-2 flex-1" key={colIdx}>
          {col.map((imageUrl, rowIdx) => {
            // Calculate the actual index in the original array
            const actualIndex = colIdx === 0 ? rowIdx * 2 : rowIdx * 2 + 1
            const hasSourceInfo = refUrls[actualIndex] || imgDescs[actualIndex]
            
            return (
              <div
                key={actualIndex}
                className={`relative overflow-hidden cursor-pointer rounded-xl w-full border-2 flex-shrink-0 group ${selectedImageIndex === actualIndex ? 'border-active' : 'border-transparent'}`}
                onClick={() => onSelect(actualIndex)}
                onMouseEnter={() => setHoveredIndex(actualIndex)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <img
                  src={imageUrl}
                  alt={imgDescs[actualIndex] || "Background image"}
                  className="w-full h-auto object-cover"
                />
                
                {/* 출처 정보 (Source info) - only show on hover */}
                {hasSourceInfo && hoveredIndex === actualIndex && (
                  <div className="absolute bottom-0 left-0 right-0 bg-[linear-gradient(180deg,_rgba(0,0,0,0)_0%,_rgba(0,0,0,1)_100%)] text-white p-3 pt-8 flex flex-col gap-2 text-xs transition-all duration-200">
                    {refUrls[actualIndex] && (
                      <div className="flex items-center gap-1">
                        <span>출처:</span>
                        <img 
                          src={`https://www.google.com/s2/favicons?domain=${new URL(refUrls[actualIndex]).hostname}&sz=16`}
                          alt=""
                          className="w-4 h-4"
                        />
                        <a 
                          href={refUrls[actualIndex]} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline truncate hover:text-blue-300"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {new URL(refUrls[actualIndex]).hostname.replace(/^www\./, '')}
                        </a>
                      </div>
                    )}
                    {imgDescs[actualIndex] && (
                      <p className="line-clamp-2 text-xs font-semibold">{imgDescs[actualIndex]}</p>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
} 