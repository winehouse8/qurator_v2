/**
 * 백엔드 API와 통신하기 위한 클라이언트 유틸리티 함수들
 */

type ApiResponse = {
  success: boolean;
  data?: any;
  error?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

/**
 * 주제를 기반으로 콘텐츠를 생성하는 API 요청
 */
export async function generateContent(query: string, range: string = 'None'): Promise<ApiResponse> {
  try {
    const response = await fetch(`${API_URL}/generate?q=${encodeURIComponent(query)}&range=${encodeURIComponent(range)}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'X-Api-Key': API_KEY,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Error: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: true,
      data,
    };
  } catch (error) {
    console.error('API request failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
} 