const API_BASE = '/api';

export interface UploadResponse {
	id: string;
	report_type: string;
	filename: string;
	records_count: number;
	message: string;
}

export interface ComparisonResult {
	collaborator: string;
	original_name: string;
	collaborator_type: 'CLT' | 'PJ';
	worked_hours: number;
	billed_hours: number;
	difference: number;
	absolute_difference: number;
	status: string;
	category: string;
	is_billed: boolean;
}

export interface ComparisonStatistics {
	total_collaborators: number;
	total_clt: number;
	total_pj: number;
	approved: number;
	divergent: number;
	not_found: number;
	approval_percentage: number;
	total_worked_hours: number;
	total_billed_hours: number;
	total_difference: number;
}

export interface ComparisonResponse {
	id: string;
	month: number;
	year: number;
	expected_pj_hours: number;
	business_days: number;
	results: ComparisonResult[];
	statistics: ComparisonStatistics;
	created_at: string;
}

export interface DetailComparisonEntry {
	date: string;
	day_of_week: string;
	timesheet_status: string;
	timesheet_worked: string;
	timesheet_balance: string;
	appropriation_total: string;
	activities_count: number;
	manual_entries: number;
	comparison_status: string;
	difference: string;
}

export interface DetailComparisonSummary {
	total_days_timesheet: number;
	total_days_appropriation: number;
	common_days: number;
	divergences: number;
	total_manual_entries: number;
}

export interface DetailComparisonResponse {
	id: string;
	entries: DetailComparisonEntry[];
	summary: DetailComparisonSummary;
	created_at: string;
}

class ApiClient {
	// Upload endpoints
	async uploadSynthetic(file: File): Promise<UploadResponse> {
		const formData = new FormData();
		formData.append('file', file);

		const response = await fetch(`${API_BASE}/upload/synthetic`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Upload failed');
		}

		return response.json();
	}

	async uploadBilling(file: File): Promise<UploadResponse> {
		const formData = new FormData();
		formData.append('file', file);

		const response = await fetch(`${API_BASE}/upload/billing`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Upload failed');
		}

		return response.json();
	}

	async uploadBillingMultiple(files: File[]): Promise<UploadResponse> {
		const formData = new FormData();
		files.forEach((file, index) => {
			formData.append(`file${index}`, file);
		});

		const response = await fetch(`${API_BASE}/upload/billing`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Upload failed');
		}

		return response.json();
	}

	async uploadTimesheet(file: File): Promise<UploadResponse> {
		const formData = new FormData();
		formData.append('file', file);

		const response = await fetch(`${API_BASE}/upload/timesheet`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Upload failed');
		}

		return response.json();
	}

	async uploadAppropriation(file: File): Promise<UploadResponse> {
		const formData = new FormData();
		formData.append('file', file);

		const response = await fetch(`${API_BASE}/upload/appropriation`, {
			method: 'POST',
			body: formData
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Upload failed');
		}

		return response.json();
	}

	// Analysis endpoints
	async compareSynthetic(
		syntheticId: string,
		billingId: string,
		month?: number,
		year?: number
	): Promise<ComparisonResponse> {
		const now = new Date();
		const response = await fetch(`${API_BASE}/analysis/compare-synthetic`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				synthetic_id: syntheticId,
				billing_id: billingId,
				month: month ?? now.getMonth() + 1, // JavaScript months are 0-indexed
				year: year ?? now.getFullYear()
			})
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Comparison failed');
		}

		return response.json();
	}

	async compareDetail(
		timesheetId: string,
		appropriationId: string
	): Promise<DetailComparisonResponse> {
		const response = await fetch(`${API_BASE}/analysis/compare-detail`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				timesheet_id: timesheetId,
				appropriation_id: appropriationId
			})
		});

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Comparison failed');
		}

		return response.json();
	}

	async getStatistics(id: string): Promise<ComparisonStatistics> {
		const response = await fetch(`${API_BASE}/analysis/statistics/${id}`);

		if (!response.ok) {
			const error = await response.json();
			throw new Error(error.error || 'Failed to get statistics');
		}

		return response.json();
	}

	// Export endpoints
	getExportCsvUrl(id: string): string {
		return `${API_BASE}/export/csv/${id}`;
	}

	getExportExcelUrl(id: string): string {
		return `${API_BASE}/export/excel/${id}`;
	}

	getDetailExportCsvUrl(id: string): string {
		return `${API_BASE}/export/detail-csv/${id}`;
	}

	getDetailExportExcelUrl(id: string): string {
		return `${API_BASE}/export/detail-excel/${id}`;
	}
}

export const api = new ApiClient();
