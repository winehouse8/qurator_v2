'use client'

import Image from 'next/image'
import { useRouter,useSearchParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Input } from './ui/input'

export function TopicSearchBar() {
    const router = useRouter()
    const searchParams = useSearchParams()
    const [topic, setTopic] = useState('')
  
    // URL의 topic 파라미터가 변경될 때 input 값 업데이트
    useEffect(() => {
      setTopic(searchParams.get('topic') || '')
    }, [searchParams])
  
    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault()
      if (topic.trim()) {
        router.push(`/content?topic=${encodeURIComponent(topic.trim())}`)
      }
    }
  
    return (
      <form onSubmit={handleSubmit} className="flex items-center gap-3 justify-center">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-[400px]"
        />
        <Button variant="submit" type="submit" aria-label="제출" className="p-2 bg-foreground rounded-full">
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