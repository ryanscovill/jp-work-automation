import React, { useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  accept: string;
  multiple?: boolean;
  onFileSelect: (files: File[]) => void;
  className?: string;
  children?: React.ReactNode;
  disabled?: boolean;
}

export function FileUpload({ 
  accept, 
  multiple = false, 
  onFileSelect, 
  className, 
  children, 
  disabled = false 
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) {
      setIsDragOver(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    validateAndSelectFiles(files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    validateAndSelectFiles(files);
    // Clear the input value to allow selecting the same file again
    e.target.value = '';
  };

  const validateAndSelectFiles = (files: File[]) => {
    if (!multiple && files.length > 1) {
      files = [files[0]];
    }

    const validFiles = files.filter(file => {
      const acceptedTypes = accept.split(',').map(type => type.trim());
      return acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return file.name.toLowerCase().endsWith(type.toLowerCase());
        }
        return file.type.match(type.replace('*', '.*'));
      });
    });

    onFileSelect(validFiles);
  };

  const handleClick = () => {
    if (!disabled) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div
      className={cn(
        "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
        {
          "border-primary bg-primary/5": isDragOver && !disabled,
          "border-muted-foreground/25 hover:border-muted-foreground/50": !isDragOver && !disabled,
          "border-muted-foreground/10 cursor-not-allowed opacity-50": disabled,
        },
        className
      )}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
      />
      {children || (
        <div className="space-y-2">
          <p className="text-sm font-medium">
            {isDragOver ? "Drop files here" : "Click to select files or drag and drop"}
          </p>
          <p className="text-xs text-muted-foreground">
            Accepts: {accept}
          </p>
        </div>
      )}
    </div>
  );
}