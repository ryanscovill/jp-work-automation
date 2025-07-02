import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FileUpload } from '@/components/shared/FileUpload';
import { ProgressTracker } from '@/components/shared/ProgressTracker';
import { apiClient } from '@/lib/api';

export function GenerateSwpTab() {
  const [sourcePdf, setSourcePdf] = useState<File | null>(null);
  const [templateFolder, setTemplateFolder] = useState('');
  const [workProcedureFolder, setWorkProcedureFolder] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSourcePdfSelect = (files: File[]) => {
    if (files.length > 0) {
      setSourcePdf(files[0]);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!sourcePdf || !templateFolder || !workProcedureFolder) {
      setError('Please provide all required fields');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      
      const response = await apiClient.generateSwp({
        source_pdf: sourcePdf,
        template_folder: templateFolder,
        work_procedure_folder: workProcedureFolder,
      });
      
      setCurrentTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleComplete = async () => {
    setIsProcessing(false);
    if (currentTaskId) {
      try {
        await apiClient.downloadFile(currentTaskId);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Download failed');
      }
    }
  };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetForm = () => {
    setSourcePdf(null);
    setTemplateFolder('');
    setWorkProcedureFolder('');
    setCurrentTaskId(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Safe Work Procedure</CardTitle>
        <CardDescription>
          Create a Safe Work Procedure (SWP) PDF from a source PDF and template folders
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="source-pdf">Source PDF</Label>
          <FileUpload
            accept=".pdf"
            onFileSelect={handleSourcePdfSelect}
            disabled={isProcessing}
          >
            {sourcePdf ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-green-600">
                  ✓ {sourcePdf.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  Click to change or drag new file
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm font-medium">Select Source PDF</p>
                <p className="text-xs text-muted-foreground">
                  The source PDF file
                </p>
              </div>
            )}
          </FileUpload>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="template-folder">Template Folder</Label>
            <Input
              id="template-folder"
              type="text"
              placeholder="/path/to/templates"
              value={templateFolder}
              onChange={(e) => setTemplateFolder(e.target.value)}
              disabled={isProcessing}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="work-procedure-folder">Work Procedure Folder</Label>
            <Input
              id="work-procedure-folder"
              type="text"
              placeholder="/path/to/work/procedures"
              value={workProcedureFolder}
              onChange={(e) => setWorkProcedureFolder(e.target.value)}
              disabled={isProcessing}
            />
          </div>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {currentTaskId && (
          <ProgressTracker
            taskId={currentTaskId}
            onComplete={handleComplete}
            onError={handleError}
          />
        )}

        <div className="flex gap-2">
          <Button
            onClick={handleSubmit}
            disabled={!sourcePdf || !templateFolder || !workProcedureFolder || isProcessing}
            className="flex-1"
          >
            {isProcessing ? 'Generating...' : 'Generate SWP'}
          </Button>
          
          {(sourcePdf || templateFolder || workProcedureFolder || error) && (
            <Button variant="outline" onClick={resetForm} disabled={isProcessing}>
              Reset
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}