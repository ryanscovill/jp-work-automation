import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FileUpload } from '@/components/shared/FileUpload';
import { TabTemplate } from '@/components/shared/TabTemplate';
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

  const resetForm = () => {
    setSourcePdf(null);
    setTemplateFolder('');
    setWorkProcedureFolder('');
    setCurrentTaskId(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <TabTemplate
      title="Generate Safe Work Procedure"
      description="Create a Safe Work Procedure (SWP) PDF from a source PDF and template folders"
      onSubmit={handleSubmit}
      onReset={resetForm}
      submitButtonText="Generate SWP"
      processingText="Generating..."
      isSubmitDisabled={!sourcePdf || !templateFolder || !workProcedureFolder}
      shouldShowReset={!!(sourcePdf || templateFolder || workProcedureFolder || error)}
      isProcessing={isProcessing}
      currentTaskId={currentTaskId}
      error={error}
    >
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
    </TabTemplate>
  );
}