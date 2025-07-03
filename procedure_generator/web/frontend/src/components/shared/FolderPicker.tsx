import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FolderOpen, History } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FolderPickerProps {
  value: string;
  onChange: (path: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
}

export function FolderPicker({ 
  value, 
  onChange, 
  placeholder = "Enter folder path...", 
  disabled = false,
  className,
  id
}: FolderPickerProps) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  
  // Common folder path suggestions
  const commonPaths = [
    'C:\\Documents',
    'C:\\Users\\%USERNAME%\\Documents',
    'C:\\Projects',
    'D:\\Work',
    '/home/user/Documents',
    '/Users/%USER%/Documents',
    './templates',
    './procedures',
    '../shared/templates'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  const handleSuggestionClick = (path: string) => {
    onChange(path);
    setShowSuggestions(false);
  };

  const handleShowSuggestions = () => {
    setShowSuggestions(!showSuggestions);
  };

  const filteredPaths = commonPaths.filter(path => 
    path.toLowerCase().includes(value.toLowerCase()) ||
    value === ''
  );

  return (
    <div className={cn("relative", className)}>
      <div className="flex gap-2">
        <Input
          id={id}
          type="text"
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          disabled={disabled}
          className="flex-1"
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
        />
        <Button
          type="button"
          variant="outline"
          size="default"
          onClick={handleShowSuggestions}
          disabled={disabled}
          className="px-3"
          title="Show common paths"
        >
          <History className="h-4 w-4" />
        </Button>
      </div>
      
      {showSuggestions && filteredPaths.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-background border border-border rounded-md shadow-lg max-h-48 overflow-y-auto">
          <div className="p-2 text-xs text-muted-foreground border-b">
            Common folder paths:
          </div>
          {filteredPaths.map((path, index) => (
            <button
              key={index}
              type="button"
              className="w-full text-left px-3 py-2 text-sm hover:bg-muted focus:bg-muted focus:outline-none"
              onClick={() => handleSuggestionClick(path)}
              disabled={disabled}
            >
              <div className="flex items-center gap-2">
                <FolderOpen className="h-3 w-3 text-muted-foreground" />
                <span className="font-mono text-xs">{path}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}