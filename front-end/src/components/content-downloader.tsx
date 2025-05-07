'use client'

import html2canvas from 'html2canvas'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

interface ContentDownloaderProps {
  cardRefs: (HTMLDivElement | null)[]
  filePrefix?: string
  buttonText?: string
}

export function ContentDownloader({
  cardRefs,
  filePrefix = 'content-card',
  buttonText = '전체 다운로드',
}: ContentDownloaderProps) {
  async function handleDownloadAll() {
    const zip = new JSZip()
    for (let i = 0; i < cardRefs.length; i++) {
      const card = cardRefs[i]
      if (!card) continue
      
      const canvas = await html2canvas(card, {
        backgroundColor: null,
        scale: 2, // 고해상도 캡처
        useCORS: true, // 외부 이미지 리소스 허용
        allowTaint: true, // 크로스 도메인 이미지 허용
        logging: false,
        imageTimeout: 0,
        onclone: (document, element) => {
          // 이미지가 로드될 때까지 대기를 위한 작업
          const images = element.querySelectorAll('img');
          if (images.length) {
            Array.from(images).forEach(img => {
              // 이미 캐시된 이미지는 완료 상태이므로 다시 로드하지 않음
              if (!img.complete) {
                img.setAttribute('crossorigin', 'anonymous');
              }
            });
          }
          
          // 백그라운드 이미지가 있는 모든 div 요소 처리
          const bgElements = element.querySelectorAll('div[style*="background-image"]');
          bgElements.forEach(el => {
            // 명시적으로 스타일 유지 (추가 처리가 필요한 경우)
            const style = window.getComputedStyle(el);
            const bgImage = style.backgroundImage;
            
            // 명시적 스타일 설정으로 캡처 품질 개선
            if (bgImage && bgImage !== 'none') {
              (el as HTMLElement).style.backgroundImage = bgImage;
              (el as HTMLElement).style.backgroundSize = 'cover';
              (el as HTMLElement).style.backgroundPosition = 'center';
            }
          });
        }
      })
      
      const blob = await new Promise<Blob | null>(resolve =>
        canvas.toBlob(resolve, 'image/png', 1.0) // 최고 품질로 저장
      )
      
      if (blob) zip.file(`${filePrefix}-${i + 1}.png`, blob)
    }
    const zipBlob = await zip.generateAsync({ type: 'blob' })
    saveAs(zipBlob, `${filePrefix}s.zip`)
  }

  return (
    <button
      type="button"
      className="btn-submit px-6 py-3 text-base font-semibold rounded-full"
      onClick={handleDownloadAll}
    >
      {buttonText}
    </button>
  )
} 