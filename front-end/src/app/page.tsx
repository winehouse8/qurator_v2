import { Logo } from '../components/ui/logo'
import { TopicInput } from '../components/topic-input'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-row items-center ">
      <div className="h-screen p-[24px] flex flex-col items-center">
        <Logo />
      </div>
      <div className="flex-1 w-full flex flex-col items-center justify-center gap-12 px-4">
        <h1 className="text-[28px] font-semibold tracking-tighter text-center">
          오늘은 어떤 콘텐츠를 만들까요?
        </h1>
        <TopicInput />
      </div>
    </main>
  )
} 