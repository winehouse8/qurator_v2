'use client'
import { useState } from 'react'
import Image from 'next/image'
import { Input } from './ui/input'
import { Button } from './ui/button'

const RECOMMENDATIONS = [
    '2025 FW 패션 트렌드',
    '썸녀와 잘 되는 법',
    '직장인 점심 메뉴 추천',  // Adding more recommendations for rotation
    '주말 데이트 코스',
    '재테크 초보 투자 방법',
]

export function TopicInput() {
  const [topic, setTopic] = useState('')
  const [startIndex, setStartIndex] = useState(0)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle topic submission
    console.log('Submitted topic:', topic)
  }

  const rotateRecommendations = () => {
    setStartIndex((prevIndex) => (prevIndex + 2) % RECOMMENDATIONS.length)
  }

  const visibleRecommendations = [
    RECOMMENDATIONS[startIndex],
    RECOMMENDATIONS[(startIndex + 1) % RECOMMENDATIONS.length]
  ]

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-[400px] space-y-3">
      <Input
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="주제를 입력해주세요."
      />
      <div className="flex justify-between items-end px-1.5">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-medium text-muted">추천:</span>
          {visibleRecommendations.map((recommendation) => (
            <Button
              key={recommendation}
              onClick={() => setTopic(recommendation)}
              type="button"
            >
              {recommendation}
            </Button>
          ))}
          <Button 
            variant="icon" 
            // type="button" 
            // aria-label="새로고침"
            onClick={rotateRecommendations}
          >
            <Image
              src="/assets/refresh-icon.svg"
              alt=""
              width={28}
              height={28}
            //   className="[&>path]:stroke-muted group-hover:[&>path]:stroke-background"
            />
          </Button>
        </div>
        <Button variant="submit" type="submit" aria-label="제출" className="p-1 bg-foreground rounded-full">
          <div className="w-6 h-6 relative">
            <Image
              src="/assets/submit-arrow1.svg"
              alt=""
              fill
              className="object-contain [&>path]:stroke-background"
            />
          </div>
        </Button>
      </div>
    </form>
  )
} 