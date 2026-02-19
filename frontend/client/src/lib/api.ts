const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp?: string;
}

export interface UploadResponse {
  message: string;
  num_transactions: number;
  num_accounts: number;
  date_range: {
    start: string;
    end: string;
  };
}

export interface DetectionResponse {
  detection_results: any;
  scoring_report: any;
  fraud_ring_output: any;
  timestamp: string;
}

export interface GraphMetricsResponse {
  metrics: any;
  timestamp: string;
}

export interface NetworkVisualizationResponse {
  plotly_data: any;
  timestamp: string;
}

export interface FraudRing {
  ring_id: string;
  member_accounts: string[];
  pattern_type: string;
  risk_score: number;
}

export interface FraudRingsResponse {
  fraud_rings: FraudRing[];
  timestamp: string;
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    try {
      // Prepare headers: if body is FormData, do NOT set Content-Type so browser can add multipart boundary
      const isFormData = options?.body instanceof FormData;
      const headers: Record<string, string> = {
        ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
        ...((options && options.headers) || {}),
      } as any;

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      // Try to parse response body (if any) to surface backend error messages
      const contentType = response.headers.get('content-type') || '';
      const parseJson = contentType.includes('application/json');
      const responseBody = parseJson ? await response.json().catch(() => null) : await response.text().catch(() => null);

      if (!response.ok) {
        const serverMessage = parseJson && responseBody ? (responseBody.error || responseBody.message || JSON.stringify(responseBody)) : responseBody || `HTTP ${response.status}`;
        throw new Error(String(serverMessage));
      }

      return responseBody as ApiResponse<T>;
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async uploadTransactions(file: File): Promise<ApiResponse<UploadResponse>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<UploadResponse>('/api/upload-transactions', {
      method: 'POST',
      body: formData,
      headers: {}, // Let browser set content-type for FormData
    });
  }

  async runDetection(): Promise<ApiResponse<DetectionResponse>> {
    return this.request<DetectionResponse>('/api/run-detection', {
      method: 'POST',
    });
  }

  async getGraphMetrics(): Promise<ApiResponse<GraphMetricsResponse>> {
    return this.request<GraphMetricsResponse>('/api/graph-metrics');
  }

  async getNetworkVisualization(): Promise<ApiResponse<NetworkVisualizationResponse>> {
    return this.request<NetworkVisualizationResponse>('/api/visualizations/network');
  }

  async getFraudRings(): Promise<ApiResponse<FraudRingsResponse>> {
    return this.request<FraudRingsResponse>('/api/fraud-rings');
  }

  async healthCheck(): Promise<ApiResponse<{ status: string; timestamp: string }>> {
    return this.request('/api/health');
  }
}

export const apiService = new ApiService();