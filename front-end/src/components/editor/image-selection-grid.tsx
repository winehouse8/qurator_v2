import Image from 'next/image'

interface ImageSelectionGridProps {
  imageUrls: string[]
  selectedImageIndex: number
  onSelect: (index: number) => void
}

export function ImageSelectionGrid({
  imageUrls,
  selectedImageIndex,
  onSelect,
}: ImageSelectionGridProps) {
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
            return (
              <div
                key={actualIndex}
                className={`relative overflow-hidden cursor-pointer rounded-xl w-full border-2 flex-shrink-0 ${selectedImageIndex === actualIndex ? 'border-active' : 'border-transparent'}`}
                onClick={() => onSelect(actualIndex)}
              >
                <img
                  src={imageUrl}
                  alt="Background image"
                  className="w-full h-auto object-cover"
                />
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
} 