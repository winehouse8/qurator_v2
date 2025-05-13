'use client'

import Image from 'next/image'
import { useRouter,useSearchParams } from 'next/navigation'
import { useState, useEffect, useTransition } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'
// import { useGenerateContent } from '../hooks/useGenerateContent'
// import { generateContent } from '../app/api/api'

export function TopicSearchBar() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [topic, setTopic] = useState('')
    const [loading, setLoading] = useState(false)
    const [isPending, startTransition] = useTransition()
  
    // URL의 topic 파라미터가 변경될 때 input 값 업데이트
    useEffect(() => {
      setTopic(searchParams.get('topic') || '')
    }, [searchParams])
  
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault()

      if (!topic.trim()) return
      
      setLoading(true)
      
      startTransition(() => {
        // 백엔드 API 호출
        // const response = await generateContent(topic.trim())
        // console.log('API Response:', response)
        
        // 응답에 관계없이 결과 페이지로 이동 또는 갱신
        router.push(`/content?topic=${encodeURIComponent(topic.trim())}`)
      })
    }
  
    return (
      <form onSubmit={handleSubmit} className="flex items-center gap-3 justify-center">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-[400px]"
          disabled={isPending}
        />
        <Button 
          variant="submit" 
          type="submit" 
          aria-label="제출" 
          className="p-2 bg-foreground rounded-full"
          disabled={isPending}
        >
          <div className="w-6 h-6 relative">
            <Image
              src="/assets/submit-icon.svg"
              alt=""
              fill
              className="object-contain [&>path]:stroke-background"
            />
          </div>
        </Button>
      </form>
    )
  }