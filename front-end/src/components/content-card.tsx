import { forwardRef } from 'react'
import cn from 'classnames'

interface ContentCardProps {
  card: {
    title?: string
    sub_title?: string
    body?: string
    img_urls?: string[]
    isNew?: boolean
  }
  category?: string
  className?: string
  isNew?: boolean
  selectedImageIndex?: number
}

export const ContentCard = forwardRef<HTMLDivElement, ContentCardProps>(
  function ContentCard({ card, category = 'text', className, isNew, selectedImageIndex = 0 }, ref) {
    // Category-based style map
    const categoryStyles = {
      text: {
        title: 'text-[96px] leading-1.5 font-semibold text-background break-keep',
        sub_title: 'text-[64px] font-semibold text-background break-keep',
        body: 'text-[48px] leading-2 text-background break-keep mt-12',
      },
      news: {
        title: 'text-[96px] leading-1.5 font-semibold text-background break-keep',
        body: 'text-[48px] leading-2 text-background break-keep mt-12',
      },
      place: {
        title: 'text-[96px] leading-1.5 font-semibold text-background break-keep',
        sub_title: 'text-[64px] font-semibold text-background break-keep',
        body: 'text-[48px] leading-2 text-background break-keep mt-12',
      }
    }
    const styles = categoryStyles[category] || categoryStyles.text

    // Get the background image URL using the selectedImageIndex
    const backgroundImageUrl = card.img_urls && card.img_urls.length > 0 
      ? card.img_urls[selectedImageIndex] 
      : undefined;

    return (
      <div
        ref={ref}
        className={cn(
          'relative shadow-[0_24px_48px_rgba(0,0,0,0.20)] overflow-hidden flex flex-col items-center justify-center bg-background transition-all duration-0',
          isNew
            ? 'rounded-2xl shadow-transparent border-8 border-dashed border-border text-foreground'
            : 'border-transparent hover:outline hover:outline-8 hover:outline-muted',
          className
        )}
        style={{
          width: 1080,
          height: 1350,
          background: 'transparent',
        }}
      >
        {/* Background Image */}
        {!isNew && backgroundImageUrl && (
          <div
            className="absolute inset-0 w-full h-full z-0 pointer-events-none"
            style={{
              backgroundImage: `url(${backgroundImageUrl})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              backgroundRepeat: 'no-repeat'
            }}
          />
        )}
        {/* Overlay */}
        {!isNew && backgroundImageUrl && (
          <div
            className="absolute inset-0 z-10 bg-[linear-gradient(180deg,_rgba(0,0,0,0)_40%,_rgba(0,0,0,0.9)_100%)] pointer-events-none"
          />
        )}
        {/* Content */}
        <div className="relative z-20 h-[1080px] p-[64px] flex flex-col items-start justify-end w-full">
          {card.title && <div className={styles.title}>{card.title}</div>}
          {card.sub_title && <div className={styles.sub_title}>{card.sub_title}</div>}
          {card.body && <div className={styles.body}>{card.body}</div>}
        </div>
      </div>
    )
  }
)