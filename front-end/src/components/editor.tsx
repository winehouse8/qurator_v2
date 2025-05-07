import React from 'react'
import { ContentCard } from './content-card'
import { Button } from './ui/button'

interface EditorProps {
  cardIndex: number
  card: {
    title?: string
    sub_title?: string
    img_urls?: string[]
    isNew?: boolean
  }
  onBack: () => void
  onNavigate: (newIndex: number) => void
  onImageSelect: (imageIndex: number) => void
  totalCards: number
  selectedImageIndex?: number
}

export function Editor({ 
  cardIndex, 
  card, 
  onBack, 
  onNavigate, 
  onImageSelect, 
  totalCards,
  selectedImageIndex = 0
}: EditorProps) {
  // ContentCard dimensions are 1080x1350, we want to display at 360x450
  const scale = 1/3;
  
  // Calculate the number of editable cards (excluding the "new" card)
  const editableCardCount = totalCards - 1;
  
  // Mock image URLs if none are provided
  const imageUrls = card.img_urls || [
    'https://placekitten.com/600/400',
    'https://placekitten.com/601/401',
    'https://placekitten.com/602/402',
    'https://placekitten.com/603/403',
    'https://placekitten.com/604/404',
    'https://placekitten.com/605/405',
  ];

  const handlePrevious = () => {
    if (cardIndex > 0) {
      onNavigate(cardIndex - 1);
    }
  };

  const handleNext = () => {
    // Only navigate if not on the last editable card
    if (cardIndex < editableCardCount - 1) {
      onNavigate(cardIndex + 1);
    }
  };

  // Handle image selection by index
  const handleImageSelect = (index: number) => {
    onImageSelect(index);
  };

  // If the card has isNew=true, don't render editor
  if (card.isNew) {
    return null;
  }

  return (
    <div className="flex flex-row gap-12 items-start justify-center px-4 py-4">
      {/* Back Button */}
      <Button
        variant='icon'
        onClick={onBack}
        className="h-10"
      >
        <img src="/assets/back-icon.svg" alt="Back" />
      </Button>
      
      {/* Main Editor Area */}
      <div className="flex flex-row gap-12">
        {/* Card Preview Wrapper */}
        <div className="flex flex-col gap-4">
          <div style={{ width: 360, height: 450 }} className="relative overflow-hidden">
            {/* Scaled ContentCard - positioned to center in the container */}
            <div style={{ 
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: `translate(-50%, -50%) scale(${scale})`,
            }}>
              <ContentCard 
                card={card} 
                category="text" 
                selectedImageIndex={selectedImageIndex}
              />
            </div>
          </div>
          <div className="flex flex-row text-sm text-muted items-center justify-between w-full">
            Page {cardIndex + 1} of {editableCardCount}
            <div className="flex gap-2">
              <Button 
                variant="icon"
                aria-label="Previous page"
                onClick={handlePrevious}
                disabled={cardIndex === 0}
                className={cardIndex === 0 ? "opacity-50 cursor-not-allowed" : ""}
              >
                <img src="/assets/left-arrow.svg" alt="Back" />
              </Button>
              <Button 
                variant="icon"
                aria-label="Next page"
                onClick={handleNext}
                disabled={cardIndex === editableCardCount - 1}
                className={cardIndex === editableCardCount - 1 ? "opacity-50 cursor-not-allowed" : ""}
              >
                <img src="/assets/right-arrow.svg" alt="Next" />
              </Button>
            </div>
          </div>
        </div>

        {/* Image Selection Panel */}
        <div className="w-80 flex flex-col gap-6">
          <h3 className="text-lg font-semibold">검색한 이미지</h3>
          
          {/* Image Grid - Pinterest Style */}
          <div className="flex flex-row gap-2 max-h-[450px] overflow-y-auto rounded-xl">
            {/* First Column */}
            <div className="flex flex-col gap-2 flex-1">
              {imageUrls.filter((_, index) => index % 2 === 0).map((imageUrl, colIndex) => {
                // Calculate the actual index in the original array
                const actualIndex = colIndex * 2;
                return (
                  <div 
                    key={actualIndex}
                    className={`relative overflow-hidden cursor-pointer rounded-xl w-full border-2 flex-shrink-0 ${selectedImageIndex === actualIndex ? 'border-foreground' : 'border-transparent'}`}
                    onClick={() => handleImageSelect(actualIndex)}
                  >
                    <img 
                      src={imageUrl} 
                      alt="Background image"
                      className="w-full h-auto object-cover" 
                    />
                  </div>
                );
              })}
            </div>
            
            {/* Second Column */}
            <div className="flex flex-col gap-2 flex-1">
              {imageUrls.filter((_, index) => index % 2 === 1).map((imageUrl, colIndex) => {
                // Calculate the actual index in the original array
                const actualIndex = colIndex * 2 + 1;
                return (
                  <div 
                    key={actualIndex}
                    className={`relative overflow-hidden cursor-pointer rounded-xl w-full border-2 flex-shrink-0 ${selectedImageIndex === actualIndex ? 'border-foreground' : 'border-transparent'}`}
                    onClick={() => handleImageSelect(actualIndex)}
                  >
                    <img 
                      src={imageUrl} 
                      alt="Background image"
                      className="w-full h-auto object-cover" 
                    />
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 