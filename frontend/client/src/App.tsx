import { UploadZone } from './components/UploadZone'
import { Dashboard } from './components/Dashboard'
import { useAppStore } from '@/store/index.ts'
import { Activity } from 'lucide-react'

function App() {
  const { graphData } = useAppStore()

  return (
    <div className="min-h-screen bg-background text-foreground font-sans p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Header */}
        <header className="flex items-center justify-between border-b border-border pb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Activity className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Financial Forensics Engine</h1>
              <p className="text-sm text-muted-foreground">Advanced Money Muling Detection System</p>
            </div>
          </div>
          <div className="text-xs text-muted-foreground text-right hidden sm:block">
            <p>v1.0.0 // RIFT Hackathon</p>
            <p className="font-mono">SECURE_ENV</p>
          </div>
        </header>

        {/* Main Content */}
        <main>
          {!graphData ? (
            <UploadZone />
          ) : (
            <Dashboard />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
