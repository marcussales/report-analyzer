<script lang="ts">
	import { api } from '$lib/api/client';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import ExportButton from '$lib/components/ExportButton.svelte';
	import {
		timesheetReport,
		appropriationReport,
		detailComparison,
		detailLoading,
		detailError,
		canCompareDetail,
		filteredDetailEntries,
		detailStatusFilter,
		resetDetailAnalysis
	} from '$lib/stores/analysis';

	let uploadingTimesheet = $state(false);
	let uploadingAppropriation = $state(false);

	async function handleTimesheetUpload(event: CustomEvent<File>) {
		uploadingTimesheet = true;
		detailError.set(null);

		try {
			const response = await api.uploadTimesheet(event.detail);
			timesheetReport.set(response);
		} catch (error) {
			detailError.set(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			uploadingTimesheet = false;
		}
	}

	async function handleAppropriationUpload(event: CustomEvent<File>) {
		uploadingAppropriation = true;
		detailError.set(null);

		try {
			const response = await api.uploadAppropriation(event.detail);
			appropriationReport.set(response);
		} catch (error) {
			detailError.set(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			uploadingAppropriation = false;
		}
	}

	async function runComparison() {
		if (!$timesheetReport || !$appropriationReport) return;

		detailLoading.set(true);
		detailError.set(null);

		try {
			const response = await api.compareDetail($timesheetReport.id, $appropriationReport.id);
			detailComparison.set(response);
		} catch (error) {
			detailError.set(error instanceof Error ? error.message : 'Comparison failed');
		} finally {
			detailLoading.set(false);
		}
	}

	const columns = [
		{ key: 'date', label: 'Data', type: 'text' as const },
		{ key: 'day_of_week', label: 'Dia', type: 'text' as const },
		{ key: 'timesheet_status', label: 'Status Ponto', type: 'text' as const },
		{ key: 'timesheet_worked', label: 'Horas Trabalhadas', type: 'text' as const, align: 'right' as const },
		{ key: 'appropriation_total', label: 'Total Apropriacao', type: 'text' as const, align: 'right' as const },
		{ key: 'activities_count', label: 'Atividades', type: 'number' as const, align: 'center' as const },
		{ key: 'manual_entries', label: 'Manuais', type: 'number' as const, align: 'center' as const },
		{ key: 'comparison_status', label: 'Status', type: 'status' as const, align: 'center' as const }
	];
</script>

<svelte:head>
	<title>Ponto vs Apropriacao - Report Analyzer</title>
</svelte:head>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-warm-100">Ponto vs Apropriacao</h1>
			<p class="mt-2 text-sm text-warm-400">
				Compare a folha de ponto (PDF) com o relatorio de apropriacao (Excel)
			</p>
		</div>
		<button class="btn-secondary" onclick={() => resetDetailAnalysis()}>
			Limpar Dados
		</button>
	</div>

	{#if $detailError}
		<div class="alert-error">
			<div class="flex">
				<div class="ml-3">
					<h3 class="text-sm font-medium">Erro</h3>
					<div class="mt-2 text-sm">{$detailError}</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Upload Section -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<div class="card">
			<div class="card-header">
				<h3 class="text-lg font-medium text-warm-200">Folha de Ponto (PDF)</h3>
			</div>
			<div class="card-body">
				{#if $timesheetReport}
					<div class="alert-success">
						<div class="flex items-center">
							<svg class="h-5 w-5 text-success-400" viewBox="0 0 20 20" fill="currentColor">
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<div class="ml-3">
								<p class="text-sm font-medium">
									{$timesheetReport.filename}
								</p>
								<p class="text-sm opacity-80">
									{$timesheetReport.records_count} dias processados
								</p>
							</div>
						</div>
					</div>
				{:else}
					<FileUpload
						accept=".pdf"
						label="Upload Folha de Ponto"
						description="PDF com registros de ponto"
						loading={uploadingTimesheet}
						on:upload={handleTimesheetUpload}
					/>
				{/if}
			</div>
		</div>

		<div class="card">
			<div class="card-header">
				<h3 class="text-lg font-medium text-warm-200">Apropriacao (Excel)</h3>
			</div>
			<div class="card-body">
				{#if $appropriationReport}
					<div class="alert-success">
						<div class="flex items-center">
							<svg class="h-5 w-5 text-success-400" viewBox="0 0 20 20" fill="currentColor">
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							<div class="ml-3">
								<p class="text-sm font-medium">
									{$appropriationReport.filename}
								</p>
								<p class="text-sm opacity-80">
									{$appropriationReport.records_count} dias processados
								</p>
							</div>
						</div>
					</div>
				{:else}
					<FileUpload
						accept=".xlsx,.xls"
						label="Upload Apropriacao"
						description="Excel com relatorio de apropriacao"
						loading={uploadingAppropriation}
						on:upload={handleAppropriationUpload}
					/>
				{/if}
			</div>
		</div>
	</div>

	<!-- Compare Button -->
	{#if $canCompareDetail && !$detailComparison}
		<div class="flex justify-center">
			<button class="btn-primary text-lg px-8 py-3" onclick={runComparison} disabled={$detailLoading}>
				{#if $detailLoading}
					<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
						<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
						<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
					</svg>
					Analisando...
				{:else}
					Gerar Analise
				{/if}
			</button>
		</div>
	{/if}

	<!-- Results Section -->
	{#if $detailComparison}
		<div class="space-y-6">
			<!-- Summary -->
			<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
				<MetricCard
					title="Dias no Ponto"
					value={$detailComparison.summary.total_days_timesheet}
					icon="chart"
					variant="default"
				/>
				<MetricCard
					title="Dias na Apropriacao"
					value={$detailComparison.summary.total_days_appropriation}
					icon="chart"
					variant="default"
				/>
				<MetricCard
					title="Dias em Comum"
					value={$detailComparison.summary.common_days}
					icon="check"
					variant="success"
				/>
				<MetricCard
					title="Divergencias"
					value={$detailComparison.summary.divergences}
					icon="x"
					variant={$detailComparison.summary.divergences > 0 ? 'error' : 'success'}
				/>
				<MetricCard
					title="Marcacoes Manuais"
					value={$detailComparison.summary.total_manual_entries}
					icon="search"
					variant={$detailComparison.summary.total_manual_entries > 0 ? 'warning' : 'default'}
				/>
			</div>

			<!-- Status Banner -->
			{#if $detailComparison.summary.divergences === 0}
				<div class="alert-success">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm font-medium">
								Parabens! Nao foram encontradas divergencias entre os relatorios.
							</p>
						</div>
					</div>
				</div>
			{:else}
				<div class="alert-warning">
					<div class="flex">
						<div class="flex-shrink-0">
							<svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
							</svg>
						</div>
						<div class="ml-3">
							<p class="text-sm font-medium">
								Foram encontradas {$detailComparison.summary.divergences} divergencias que precisam de atencao.
							</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Filters and Export -->
			<div class="flex flex-wrap items-center justify-between gap-4">
				<div class="flex flex-wrap items-center gap-4">
					<select
						class="select"
						bind:value={$detailStatusFilter}
					>
						<option value="all">Todos os Status</option>
						<option value="ok">Sem Divergencia</option>
						<option value="divergence">Com Divergencia</option>
						<option value="manual">Com Marcacoes Manuais</option>
					</select>
				</div>

				<ExportButton
					csvUrl={api.getDetailExportCsvUrl($detailComparison.id)}
					excelUrl={api.getDetailExportExcelUrl($detailComparison.id)}
				/>
			</div>

			<!-- Results Table -->
			<DataTable {columns} data={$filteredDetailEntries} emptyMessage="Nenhum resultado encontrado" maxHeight="500px" />

			<p class="text-sm text-warm-500">
				Exibindo {$filteredDetailEntries.length} de {$detailComparison.entries.length} dias
			</p>
		</div>
	{/if}
</div>
