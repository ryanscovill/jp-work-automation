import { Routes, Route, Link } from "react-router-dom"
import { Settings } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Toaster } from "@/components/ui/sonner"
import { ExcelToPdfTab } from "@/components/tabs/ExcelToPdfTab"
import { GenerateSwpTab } from "@/components/tabs/GenerateSwpTab"
import { FillNopTab } from "@/components/tabs/FillNopTab"
import { UpdateMasterTab } from "@/components/tabs/UpdateMasterTab"
import { SettingsPage } from "@/components/pages/SettingsPage"

function MainPage() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-center">Work Procedure PDF Generator</h1>
          <p className="text-muted-foreground text-center mt-2">
            Automate creating work procedure PDFs and form filling
          </p>
        </header>

        <Tabs defaultValue="excel-pdf" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="excel-pdf">Excel to PDF</TabsTrigger>
            <TabsTrigger value="generate-swp">Generate SWP</TabsTrigger>
            <TabsTrigger value="fill-nop">Fill NOP</TabsTrigger>
            <TabsTrigger value="update-master">Update Master</TabsTrigger>
          </TabsList>

          <TabsContent value="excel-pdf" className="mt-6">
            <ExcelToPdfTab />
          </TabsContent>

          <TabsContent value="generate-swp" className="mt-6">
            <GenerateSwpTab />
          </TabsContent>

          <TabsContent value="fill-nop" className="mt-6">
            <FillNopTab />
          </TabsContent>

          <TabsContent value="update-master" className="mt-6">
            <UpdateMasterTab />
          </TabsContent>
        </Tabs>
      </div>
      
      {/* Settings Icon - Fixed position bottom left */}
      <div className="fixed bottom-6 left-6">
        <Button 
          asChild 
          variant="outline" 
          size="icon"
          className="rounded-full shadow-lg hover:shadow-xl transition-shadow"
        >
          <Link to="/settings">
            <Settings className="h-5 w-5" />
          </Link>
        </Button>
      </div>
      
      <Toaster />
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<MainPage />} />
      <Route path="/settings" element={<SettingsPage />} />
    </Routes>
  )
}

export default App
