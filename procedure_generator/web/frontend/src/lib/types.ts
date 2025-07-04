export interface TaskResponse {
  task_id: string;
  message: string;
}

export interface TaskStatus {
  status: 'processing' | 'completed' | 'error';
  progress: number;
  output_file?: string;
  error?: string;
}

export interface ExcelToPdfRequest {
  excel_file: File;
  pdf_template: File;
}

export interface GenerateSwpRequest {
  source_pdf: File;
  template_folder: string;
  work_procedure_folder: string;
}

export interface FillNopRequest {
  swp_file: File;
}

export interface UpdateMasterRequest {
  source_pdf: File;
  template_folder: string;
  work_procedure_folder: string;
}

export interface ApiError {
  detail: string;
}

// Legacy types removed - now using dynamic Configuration type

// Flexible configuration type for dynamic UI generation
export type ConfigValue = string | number | boolean | ConfigValue[] | { [key: string]: ConfigValue }

export interface Configuration {
  [key: string]: ConfigValue;
}

export interface ConfigResponse {
  config: Configuration;
  comments: Record<string, string>;
}

export interface ConfigUpdateRequest {
  config: Configuration;
}