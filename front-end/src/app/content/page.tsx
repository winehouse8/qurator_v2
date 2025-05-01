import { Logo } from '../../components/ui/logo'
import { TopicSearchBar } from '../../components/topic-search-bar'
import { ContentGrid } from '../../components/content-grid'

export default function ContentPage() {
  return (
    <main className="flex min-h-screen">
      {/* Sidebar */}
      <div className="h-screen p-6 flex flex-col items-center">
        <Logo />
      </div>

      {/* Main Content */}
      <div className="flex-1 py-12 px-4">
        <div className="max-w-[1100px] mx-auto space-y-12">
          {/* Search Bar */}
          <TopicSearchBar />
          
          {/* Content Section */}
          <ContentGrid />
        </div>
      </div>
    </main>
  )
} 