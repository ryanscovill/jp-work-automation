import type { TaskResponse, TaskStatus, ExcelToPdfRequest, GenerateSwpRequest, FillNopRequest, UpdateMasterRequest, ConfigResponse, Configuration } from './types';

const API_BASE = '/api';

class ApiClient {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; api_version: string }> {
    return this.makeRequest('/health');
  }

  async excelToPdf(request: ExcelToPdfRequest): Promise<TaskResponse> {
    const formData = new FormData();
    formData.append('excel_file', request.excel_file);
    formData.append('pdf_template', request.pdf_template);

    return this.makeRequest('/excel-to-pdf', {
      method: 'POST',
      body: formData,
    });
  }

  async generateSwp(request: GenerateSwpRequest): Promise<TaskResponse> {
    const formData = new FormData();
    formData.append('source_pdf', request.source_pdf);
    formData.append('template_folder', request.template_folder);
    formData.append('work_procedure_folder', request.work_procedure_folder);

    return this.makeRequest('/generate-swp', {
      method: 'POST',
      body: formData,
    });
  }

  async fillNop(request: FillNopRequest): Promise<TaskResponse> {
    const formData = new FormData();
    formData.append('swp_file', request.swp_file);

    return this.makeRequest('/fill-nop', {
      method: 'POST',
      body: formData,
    });
  }

  async updateMaster(request: UpdateMasterRequest): Promise<TaskResponse> {
    const formData = new FormData();
    formData.append('source_pdf', request.source_pdf);
    formData.append('template_folder', request.template_folder);
    formData.append('work_procedure_folder', request.work_procedure_folder);

    return this.makeRequest('/update-master', {
      method: 'POST',
      body: formData,
    });
  }

  async getTaskStatus(taskId: string): Promise<TaskStatus> {
    return this.makeRequest(`/task-status/${taskId}`);
  }

  getDownloadUrl(taskId: string): string {
    return `${API_BASE}/download/${taskId}`;
  }

  async downloadFile(taskId: string): Promise<void> {
    const response = await fetch(this.getDownloadUrl(taskId));
    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `output_${taskId}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }

  async getConfig(): Promise<ConfigResponse> {
    return this.makeRequest('/config');
  }

  async updateConfig(config: Configuration): Promise<{ message: string }> {
    return this.makeRequest('/config', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ config }),
    });
  }
}

export const apiClient = new ApiClient();

// Export convenience functions for config management
export const getConfig = () => apiClient.getConfig();
export const updateConfig = (config: Configuration) => apiClient.updateConfig(config);