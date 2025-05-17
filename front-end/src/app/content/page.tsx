/* ---------------------------------------------------------------------
   /front-end/src/app/content/page.tsx
   한 파일 전체 복사‧붙여넣기용
--------------------------------------------------------------------- */

'use client'

import { Suspense, useMemo, useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'

/* --- UI / 컴포넌트 --- */
import { Logo } from '../../components/ui/logo'
import { TopicSearchBar } from '../../components/topic-search-bar'
import { ContentGrid } from '../../components/content-grid'
import { SidePanel } from '../../components/ui/side-panel'
import { Editor } from '../../components/editor'
import SkeletonLoading from '../../components/skeleton-loading'

/* --- 데이터 훅 --- */
import { useGenerateContent } from '../../hooks/useGenerateContent'

/* --- 목업 이미지 (카드에 기본 이미지가 없을 때 사용) --- */
const mockImageUrls = [
  'https://placekitten.com/600/400',
  'https://placekitten.com/601/401',
  'https://placekitten.com/602/402',
  'https://placekitten.com/603/403',
  'https://placekitten.com/604/404',
  'https://placekitten.com/605/405',
]

/* ------------------------------------------------------------------ */
/* 1) Suspense Wrapper – useSearchParams() 가 이 안에서만 호출됨     */
/* ------------------------------------------------------------------ */
export default function ContentPageWrapper() {
  return (
    <Suspense fallback={<div className="flex min-h-screen items-center justify-center">
      Loading…
    </div>}>
      <ContentPage /> {/* 👈 실제 페이지 컴포넌트 */}
    </Suspense>
  )
}

/* ------------------------------------------------------------------ */
/* 2) 실제 페이지 – 기존 로직 그대로                                  */
/* ------------------------------------------------------------------ */
function ContentPage() {
  /* ────── URL 파라미터 → topic ────── */
  const searchParams = useSearchParams()
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
    useState<number[]>([])

  useEffect(() => {
    setSelectedImageIndices(Array(cards.length).fill(0))
  }, [cards.length])

  /* ────── 편집 중인 카드 인덱스 ────── */
  const [editingIndex, setEditingIndex] = useState<number | null>(null)

  /* ────── 로딩 / 오류 처리 ────── */
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
    )
  }

  /* 실제 카테고리 (백엔드 응답 or fallback) */
  const category = data?.data?.topic || topic

  /* 카드 내부 이미지 선택 콜백 */
  const handleImageSelect = (cardIndex: number, imageIndex: number) => {
    setSelectedImageIndices(prev => {
      const next = [...prev]
      next[cardIndex] = imageIndex
      return next
    })
  }

  /* 페이지 이동(에디터) */
  const handleNavigate = (newIndex: number) => setEditingIndex(newIndex)

  /* ------------- 실제 출력 ------------- */
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
              category={category}
              cards={cards}
              selectedImageIndices={selectedImageIndices}
            />
          ) : (
            <Editor
              cardIndex={editingIndex}
              card={cards[editingIndex]}
              onBack={() => setEditingIndex(null)}
              onNavigate={handleNavigate}
              onImageSelect={(idx: number) => handleImageSelect(editingIndex, idx)}
              totalCards={cards.length}
              selectedImageIndex={selectedImageIndices[editingIndex]}
            />
          )}
        </div>
      </div>
    </main>
  )
}
