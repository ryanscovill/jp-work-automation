import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DynamicConfigEditor } from "@/components/config/DynamicConfigEditor"

export function SettingsPage() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <Button asChild variant="ghost" size="sm">
            <Link to="/" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Main
            </Link>
          </Button>
        </div>
        
        <header className="mb-8">
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Configure your application preferences and update the swp_config.yaml file
          </p>
        </header>

        <DynamicConfigEditor />
      </div>
    </div>
  )
}