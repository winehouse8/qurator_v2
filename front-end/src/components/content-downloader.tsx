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
      })
      const blob = await new Promise<Blob | null>(resolve =>
        canvas.toBlob(resolve, 'image/png')
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