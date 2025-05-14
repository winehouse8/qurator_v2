'use client'

import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'next/navigation'
import { Logo } from '../../components/ui/logo'
import { TopicSearchBar } from '../../components/topic-search-bar'
import { ContentGrid } from '../../components/content-grid'
import { SidePanel } from '../../components/ui/side-panel'
import { Editor } from '../../components/editor'
import { useGenerateContent } from '../../hooks/useGenerateContent'
import SkeletonLoading from '../../components/skeleton-loading'

// Add mock image URLs in case they're not in the mock data
const mockImageUrls = [
  'https://placekitten.com/600/400',
  'https://placekitten.com/601/401',
  'https://placekitten.com/602/402',
  'https://placekitten.com/603/403',
  'https://placekitten.com/604/404',
  'https://placekitten.com/605/405',
];

export default function ContentPage() {
   /* ────── URL 파라미터 → topic ────── */
  const searchParams = useSearchParams();
  const topic = searchParams.get('topic') ?? ''

  /* ────── API 호출 (React Query) ────── */
  const { 
    data, 
    isPending, 
    isFetching, 
    isError,
    refetch,
  } = useGenerateContent(topic)

   /* ────── 카드 데이터 가공 ────── */
  const cards = useMemo(() => {
    if (!data?.success) return []

    return data.data.cards.map((card: any) => ({
      ...card,
      img_urls: card.img_urls
        ? card.img_urls
        : card.imageUrl
        ? [card.imageUrl, ...mockImageUrls.slice(1)]
        : [...mockImageUrls],
    }))
  }, [data])

  /* ────── 선택 이미지 인덱스 관리 ────── */ 
  const [selectedImageIndices, setSelectedImageIndices] = 
  useState<number[]>(() => []);
  useEffect(() => {
      setSelectedImageIndices(Array(cards.length).fill(0))
  }, [cards.length]);

  /* ────── 편집 중인 카드 인덱스 ────── */
  const [editingIndex, setEditingIndex] = useState<number | null>(null)

  /* ────── 데이터가 로드되지 않았다면 로딩 상태 표시 ────── */

  if (isError) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center gap-6">
        <p className="text-lg font-semibold">콘텐츠를 불러오지 못했습니다.</p>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-foreground text-background rounded-lg"
        >
          다시 시도
        </button>
      </main>
    )
  }
  // 데이터가 로드되지 않았다면 로딩 상태 표시
  if (isPending || isFetching) {
    return (
      <main className="flex min-h-screen">
        <SidePanel>
          <Logo />
        </SidePanel>
        <div className="flex-1 py-12 px-4">
          <div className="w-full max-w-[1100px] mx-auto space-y-12">
            <TopicSearchBar />
            <SkeletonLoading />
          </div>
        </div>
      </main>
    );
  }

  const category = data?.data?.topic || topic
  
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
              category={category || searchParams.get('topic') || ''} 
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