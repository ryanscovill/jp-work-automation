import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { FileUpload } from '@/components/shared/FileUpload';
import { TabTemplate } from '@/components/shared/TabTemplate';
import { apiClient } from '@/lib/api';

export function UpdateMasterTab() {
  const [sourcePdf, setSourcePdf] = useState<File | null>(null);
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
    if (!sourcePdf) {
      setError('Please select a master PDF file');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      
      const response = await apiClient.updateMaster({
        source_pdf: sourcePdf,
        template_folder: '',
        work_procedure_folder: '',
      });
      
      setCurrentTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetForm = () => {
    setSourcePdf(null);
    setCurrentTaskId(null);
    setError(null);
    setIsProcessing(false);
  };

  const infoSection = (
    <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
      <h4 className="text-sm font-medium text-yellow-800 mb-2">How it works:</h4>
      <ul className="text-sm text-yellow-700 space-y-1">
        <li>• Scans the template folder for available PDF templates</li>
        <li>• Scans the work procedure folder for procedure documents</li>
        <li>• Updates dropdown fields in the master PDF with found items</li>
        <li>• Creates an updated master PDF with current options</li>
      </ul>
    </div>
  );

  return (
    <TabTemplate
      title="Update Master"
      description="Update master PDF with current templates and work procedures from specified folders"
      onSubmit={handleSubmit}
      onReset={resetForm}
      onError={handleError}
      submitButtonText="Update Master PDF"
      processingText="Updating..."
      isSubmitDisabled={!sourcePdf}
      shouldShowReset={!!(sourcePdf || error)}
      isProcessing={isProcessing}
      currentTaskId={currentTaskId}
      error={error}
      infoSection={infoSection}
    >
      <div className="space-y-2">
        <Label htmlFor="source-pdf">Master PDF File</Label>
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
              <p className="text-sm font-medium">Select Master PDF</p>
              <p className="text-xs text-muted-foreground">
                The master PDF to update
              </p>
            </div>
          )}
        </FileUpload>
      </div>
    </TabTemplate>
  );
}