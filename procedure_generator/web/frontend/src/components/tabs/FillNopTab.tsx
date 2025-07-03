import { useState } from 'react';
import { Label } from '@/components/ui/label';
import { FileUpload } from '@/components/shared/FileUpload';
import { TabTemplate } from '@/components/shared/TabTemplate';
import { apiClient } from '@/lib/api';

export function FillNopTab() {
  const [swpFile, setSwpFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSwpFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setSwpFile(files[0]);
      setError(null);
      setSuccess(false);
    }
  };

  const handleSubmit = async () => {
    if (!swpFile) {
      setError('Please select a SWP PDF file');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      setSuccess(false);
      
      const response = await apiClient.fillNop({
        swp_file: swpFile,
      });
      
      setCurrentTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleComplete = () => {
    setIsProcessing(false);
    setSuccess(true);
  };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetForm = () => {
    setSwpFile(null);
    setCurrentTaskId(null);
    setError(null);
    setSuccess(false);
    setIsProcessing(false);
  };

  const infoSection = (
    <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
      <h4 className="text-sm font-medium text-blue-800 mb-2">Important Notes:</h4>
      <ul className="text-sm text-blue-700 space-y-1">
        <li>• This process will open a browser window automatically</li>
        <li>• Make sure you have a stable internet connection</li>
        <li>• The browser will navigate to the WorkSafeBC website</li>
        <li>• Do not close the browser window during processing</li>
      </ul>
    </div>
  );

  return (
    <TabTemplate
      title="Fill NOP Form"
      description="Automate filling of NOP (Notice of Project) forms on the WorkSafeBC website using browser automation"
      onSubmit={handleSubmit}
      onReset={resetForm}
      onError={handleError}
      submitButtonText="Fill NOP Form"
      processingText="Filling Form..."
      isSubmitDisabled={!swpFile}
      shouldShowReset={!!(swpFile || error || success)}
      isProcessing={isProcessing}
      currentTaskId={currentTaskId}
      error={error}
      success={success}
      successMessage="NOP form filling completed successfully!"
      infoSection={infoSection}
    >
      <div className="space-y-2">
        <Label htmlFor="swp-file">SWP PDF File</Label>
        <FileUpload
          accept=".pdf"
          onFileSelect={handleSwpFileSelect}
          disabled={isProcessing}
        >
          {swpFile ? (
            <div className="space-y-2">
              <p className="text-sm font-medium text-green-600">
                ✓ {swpFile.name}
              </p>
              <p className="text-xs text-muted-foreground">
                Click to change or drag new file
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-sm font-medium">Select SWP PDF</p>
              <p className="text-xs text-muted-foreground">
                The Safe Work Procedure PDF file
              </p>
            </div>
          )}
        </FileUpload>
      </div>
    </TabTemplate>
  );
}