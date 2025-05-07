import { Logo } from '../components/ui/logo'
import { SidePanel } from '../components/ui/side-panel'
import { TopicInput } from '../components/topic-input'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-row items-center ">
      <SidePanel>
        <Logo />
      </SidePanel>
      <div className="flex-1 w-full flex flex-col items-center justify-center gap-12">
        <h1 className="text-title font-semibold tracking-tighter text-center">
          오늘은 어떤 콘텐츠를 만들까요?
        </h1>
        <TopicInput />
        <div className="h-[34px] w-full" /> 
      </div>
    </main>
  )
} 