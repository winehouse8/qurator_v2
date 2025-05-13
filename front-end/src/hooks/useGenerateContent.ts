import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { generateContent } from '../app/api/api'

export const useGenerateContent = (topic?: string | null) =>
    useQuery({
      queryKey: ['content', topic],
      queryFn: () => generateContent(topic!), // topic이 있을 때만 호출
      enabled: !!topic,
      staleTime: 5 * 60 * 1000,              // 5 분 캐싱
      /**
       * v5 방식 ─ 두 가지 중 하나 선택
       * 1) placeholderData: keepPreviousData       ← 헬퍼 함수 사용
       * 2) placeholderData: (prev) => prev         ← 아이덴티티 함수
       */
      placeholderData: keepPreviousData,
      // placeholderData: (prev) => prev,
    })