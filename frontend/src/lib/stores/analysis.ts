import { writable, derived } from 'svelte/store';
import type {
	UploadResponse,
	ComparisonResponse,
	DetailComparisonResponse
} from '$lib/api/client';

// Synthetic analysis state
export const syntheticReport = writable<UploadResponse | null>(null);
export const billingReport = writable<UploadResponse | null>(null);
export const syntheticComparison = writable<ComparisonResponse | null>(null);
export const syntheticLoading = writable(false);
export const syntheticError = writable<string | null>(null);

// Detail analysis state
export const timesheetReport = writable<UploadResponse | null>(null);
export const appropriationReport = writable<UploadResponse | null>(null);
export const detailComparison = writable<DetailComparisonResponse | null>(null);
export const detailLoading = writable(false);
export const detailError = writable<string | null>(null);

// Derived states
export const canCompareSynthetic = derived(
	[syntheticReport, billingReport],
	([$synthetic, $billing]) => $synthetic !== null && $billing !== null
);

export const canCompareDetail = derived(
	[timesheetReport, appropriationReport],
	([$timesheet, $appropriation]) => $timesheet !== null && $appropriation !== null
);

// Reset functions
export function resetSyntheticAnalysis() {
	syntheticReport.set(null);
	billingReport.set(null);
	syntheticComparison.set(null);
	syntheticError.set(null);
}

export function resetDetailAnalysis() {
	timesheetReport.set(null);
	appropriationReport.set(null);
	detailComparison.set(null);
	detailError.set(null);
}

// Filter state for comparison results
export const statusFilter = writable<string>('all');
export const categoryFilter = writable<string>('all');
export const typeFilter = writable<string>('all');

export const filteredResults = derived(
	[syntheticComparison, statusFilter, categoryFilter, typeFilter],
	([$comparison, $status, $category, $type]) => {
		if (!$comparison) return [];

		return $comparison.results.filter((result) => {
			const statusMatch = $status === 'all' || result.status === $status;
			const categoryMatch = $category === 'all' || result.category === $category;
			const typeMatch = $type === 'all' || result.collaborator_type === $type;
			return statusMatch && categoryMatch && typeMatch;
		});
	}
);

// Detail filter state
export const detailStatusFilter = writable<string>('all');

export const filteredDetailEntries = derived(
	[detailComparison, detailStatusFilter],
	([$comparison, $filter]) => {
		if (!$comparison) return [];

		if ($filter === 'all') return $comparison.entries;

		return $comparison.entries.filter((entry) => {
			if ($filter === 'divergence') {
				return (
					entry.comparison_status.includes('DIVERGENCIA') ||
					entry.comparison_status.includes('SEM')
				);
			}
			if ($filter === 'manual') {
				return entry.manual_entries > 0;
			}
			if ($filter === 'ok') {
				return (
					entry.comparison_status.includes('SEM DIVERGENCIA') ||
					entry.comparison_status.includes('OK')
				);
			}
			return true;
		});
	}
);
