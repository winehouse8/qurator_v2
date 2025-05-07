'use client'

import { useState } from 'react'
import { Logo } from '../../components/ui/logo'
import { TopicSearchBar } from '../../components/topic-search-bar'
import { ContentGrid } from '../../components/content-grid'
import { SidePanel } from '../../components/ui/side-panel'
import { Editor } from '../../components/editor'
import { mocking_function } from '../api/mock-api'

// Add mock image URLs in case they're not in the mock data
const mockImageUrls = [
  'https://placekitten.com/600/400',
  'https://placekitten.com/601/401',
  'https://placekitten.com/602/402',
  'https://placekitten.com/603/403',
  'https://placekitten.com/604/404',
  'https://placekitten.com/605/405',
];

const CARD_DATA = JSON.parse(mocking_function());

// Ensure all cards have img_urls
const cardsWithImages = CARD_DATA.cards.map(card => ({
  ...card,
  img_urls: card.img_urls || [...mockImageUrls]
}));

// Add the "new content" card
const allCards = [
  ...cardsWithImages
];

export default function ContentPage() {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  
  // Create a state to manage cards without modifying their original structure
  const [cards] = useState(allCards);
  
  // Track selected image index for each card separately
  const [selectedImageIndices, setSelectedImageIndices] = useState<number[]>(
    Array(cards.length).fill(0) // Default to first image (index 0) for all cards
  );

  const handleNavigate = (newIndex: number) => {
    setEditingIndex(newIndex);
  };

  // Function to update the selected image index for a card
  const handleImageSelect = (cardIndex: number, imageIndex: number) => {
    setSelectedImageIndices(prevIndices => {
      const newIndices = [...prevIndices];
      newIndices[cardIndex] = imageIndex;
      return newIndices;
    });
  };

  return (
    <main className="flex min-h-screen">
      {/* Sidebar */}
      <SidePanel>
        <Logo />
      </SidePanel>

      {/* Main Content */}
      <div className="flex-1 py-12 px-4">
        <div className="w-full max-w-[1100px] mx-auto space-y-12">
          {/* Search Bar */}
          <TopicSearchBar />
          
          {/* Content Section */}
          {editingIndex === null ? (
            <ContentGrid 
              onEdit={setEditingIndex} 
              category={CARD_DATA.category} 
              cards={cards} 
              selectedImageIndices={selectedImageIndices}
            />
          ) : (
            <Editor 
              cardIndex={editingIndex} 
              card={cards[editingIndex]} 
              onBack={() => setEditingIndex(null)} 
              onNavigate={handleNavigate}
              onImageSelect={(imageIndex: number) => handleImageSelect(editingIndex, imageIndex)}
              totalCards={cards.length}
              selectedImageIndex={selectedImageIndices[editingIndex]}
            />
          )}
        </div>
      </div>
    </main>
  )
} 