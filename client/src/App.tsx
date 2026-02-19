import { useState } from 'react'
import { UploadZone } from './components/UploadZone'
import { Dashboard } from './components/Dashboard'
import { useAppStore } from './store'
import { Activity, Moon, Sun } from 'lucide-react'

function App() {
  const { graphData } = useAppStore()
  const [isDark, setIsDark] = useState(false)

  return (
    <div className={`min-h-screen ${isDark ? 'dark bg-slate-950 text-slate-50' : 'bg-gradient-to-b from-blue-50 to-white text-foreground'} font-sans transition-colors duration-300`}>
      {/* Navigation */}
      <nav className={`border-b ${isDark ? 'border-slate-700 bg-slate-900/50' : 'border-slate-200 bg-white/50'} backdrop-blur-sm sticky top-0 z-40 transition-colors duration-300`}>
        <div className="max-w-7xl mx-auto px-6 md:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-gradient-to-br from-blue-600 to-blue-500 rounded-lg shadow-md">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <span className={`text-lg font-bold ${isDark ? 'text-slate-50' : 'text-slate-900'}`}>FinForensics</span>
          </div>
          <div className="flex items-center gap-6">
            <button
              onClick={() => setIsDark(!isDark)}
              className={`p-2 rounded-lg transition-colors ${isDark ? 'bg-slate-800 text-yellow-300 hover:bg-slate-700' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'}`}
              title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <div className={`text-xs ${isDark ? 'text-slate-400' : 'text-slate-500'} hidden sm:block`}>
              <p>v1.0.0 — Evaluation Build</p>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto space-y-8 p-6 md:p-8">

        {/* Header */}
        <header className={`pt-8 space-y-3 border-b ${isDark ? 'border-slate-700' : 'border-slate-200'} pb-8 transition-colors duration-300`}>
          <div className="space-y-1">
            <h1 className={`text-6xl font-extrabold ${isDark ? 'text-slate-50' : 'text-slate-900'}`}>Financial Forensics Engine</h1>
            <p className={`insight-line ${isDark ? 'dark-insight' : ''}`}>Fraud doesn't hide in transactions — it hides in relationships.</p>
            <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Internal Graph-Based Engine for Identifying Coordinated Fraud Networks</p>
          </div>
          <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'} max-w-2xl`}>Upload transaction data to detect money-muling rings using advanced forensic analysis.</p>
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
