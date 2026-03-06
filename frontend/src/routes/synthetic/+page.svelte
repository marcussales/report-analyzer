<script lang="ts">
	import { api } from '$lib/api/client';
	import FileUpload from '$lib/components/FileUpload.svelte';
	import MetricCard from '$lib/components/MetricCard.svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import ExportButton from '$lib/components/ExportButton.svelte';
	import {
		syntheticReport,
		billingReport,
		syntheticComparison,
		syntheticLoading,
		syntheticError,
		canCompareSynthetic,
		filteredResults,
		statusFilter,
		categoryFilter,
		typeFilter,
		resetSyntheticAnalysis
	} from '$lib/stores/analysis';

	let uploadingSynthetic = $state(false);
	let uploadingBilling = $state(false);

	// Month/Year selection - default to current month
	const now = new Date();
	let selectedMonth = $state(now.getMonth() + 1);
	let selectedYear = $state(now.getFullYear());

	const months = [
		{ value: 1, label: 'Janeiro' },
		{ value: 2, label: 'Fevereiro' },
		{ value: 3, label: 'Marco' },
		{ value: 4, label: 'Abril' },
		{ value: 5, label: 'Maio' },
		{ value: 6, label: 'Junho' },
		{ value: 7, label: 'Julho' },
		{ value: 8, label: 'Agosto' },
		{ value: 9, label: 'Setembro' },
		{ value: 10, label: 'Outubro' },
		{ value: 11, label: 'Novembro' },
		{ value: 12, label: 'Dezembro' }
	];

	async function handleSyntheticUpload(event: CustomEvent<File>) {
		uploadingSynthetic = true;
		syntheticError.set(null);

		try {
			const response = await api.uploadSynthetic(event.detail);
			syntheticReport.set(response);
		} catch (error) {
			syntheticError.set(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			uploadingSynthetic = false;
		}
	}

	async function handleBillingUpload(event: CustomEvent<File>) {
		uploadingBilling = true;
		syntheticError.set(null);

		try {
			const response = await api.uploadBilling(event.detail);
			billingReport.set(response);
		} catch (error) {
			syntheticError.set(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			uploadingBilling = false;
		}
	}

	async function handleBillingUploadMultiple(event: CustomEvent<File[]>) {
		uploadingBilling = true;
		syntheticError.set(null);

		try {
			const response = await api.uploadBillingMultiple(event.detail);
			billingReport.set(response);
		} catch (error) {
			syntheticError.set(error instanceof Error ? error.message : 'Upload failed');
		} finally {
			uploadingBilling = false;
		}
	}

	async function runComparison() {
		if (!$syntheticReport || !$billingReport) return;

		syntheticLoading.set(true);
		syntheticError.set(null);

		try {
			const response = await api.compareSynthetic(
				$syntheticReport.id,
				$billingReport.id,
				selectedMonth,
				selectedYear
			);
			syntheticComparison.set(response);
		} catch (error) {
			syntheticError.set(error instanceof Error ? error.message : 'Comparison failed');
		} finally {
			syntheticLoading.set(false);
		}
	}

	function formatHours(hours: number): string {
		const h = Math.floor(hours);
		const m = Math.round((hours - h) * 60);
		return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
	}

	const columns = [
		{ key: 'original_name', label: 'Colaborador', type: 'text' as const },
		{ key: 'collaborator_type', label: 'Tipo', type: 'badge' as const, align: 'center' as const },
		{ key: 'worked_hours', label: 'Horas Previstas', type: 'hours' as const, align: 'right' as const },
		{ key: 'billed_hours', label: 'Horas Apropriadas', type: 'hours' as const, align: 'right' as const },
		{ key: 'difference', label: 'Diferenca', type: 'hours' as const, align: 'right' as const },
		{ key: 'status', label: 'Status', type: 'status' as const, align: 'center' as const },
		{ key: 'category', label: 'Categoria', type: 'status' as const, align: 'center' as const }
	];
</script>

<svelte:head>
	<title>Sintetico vs Faturamento - Report Analyzer</title>
</svelte:head>

<div class="space-y-8">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold text-warm-100">Sintetico vs Faturamento</h1>
			<p class="mt-2 text-sm text-warm-400">
				Compare o relatorio sintetico com o relatorio de faturamento
			</p>
		</div>
		<button class="btn-secondary" onclick={() => resetSyntheticAnalysis()}>
			Limpar Dados
		</button>
	</div>

	{#if $syntheticError}
		<div class="alert-error">
			<div class="flex">
				<div class="ml-3">
					<h3 class="text-sm font-medium">Erro</h3>
					<div class="mt-2 text-sm">{$syntheticError}</div>
				</div>
			</div>
		</div>
	{/if}

	<!-- Upload Section -->
	<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
		<div class="card">
			<div class="card-header">
				<h3 class="text-lg font-medium text-warm-200">Relatorio Sintetico</h3>
			</div>
			<div class="card-body">
				{#if $syntheticReport}
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
									{$syntheticReport.filename}
								</p>
								<p class="text-sm opacity-80">
									{$syntheticReport.records_count} colaboradores processados
								</p>
							</div>
						</div>
					</div>
				{:else}
					<FileUpload
						accept=".xlsx,.xls,.pdf"
						label="Upload Relatorio Sintetico"
						description="Excel ou PDF com colaboradores e horas trabalhadas"
						loading={uploadingSynthetic}
						on:upload={handleSyntheticUpload}
					/>
				{/if}
			</div>
		</div>

		<div class="card">
			<div class="card-header">
				<h3 class="text-lg font-medium text-warm-200">Relatorio de Faturamento</h3>
			</div>
			<div class="card-body">
				{#if $billingReport}
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
									{$billingReport.filename}
								</p>
								<p class="text-sm opacity-80">
									{$billingReport.records_count} profissionais processados
								</p>
							</div>
						</div>
					</div>
				{:else}
					<FileUpload
						accept=".xlsx,.xls"
						label="Upload Relatorio Faturamento"
						description="Excel com profissionais e horas apropriadas"
						loading={uploadingBilling}
						multiple={true}
						on:upload={handleBillingUpload}
						on:uploadMultiple={handleBillingUploadMultiple}
					/>
				{/if}
			</div>
		</div>
	</div>

	<!-- Month/Year Selector and Compare Button -->
	{#if $canCompareSynthetic && !$syntheticComparison}
		<div class="card">
			<div class="card-header">
				<h3 class="text-lg font-medium text-warm-200">Configuracao da Analise</h3>
			</div>
			<div class="card-body">
				<div class="flex flex-wrap items-end gap-4 justify-center">
					<div>
						<label class="block text-sm font-medium text-warm-400 mb-1">Mes</label>
						<select class="select" bind:value={selectedMonth}>
							{#each months as month}
								<option value={month.value}>{month.label}</option>
							{/each}
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-warm-400 mb-1">Ano</label>
						<select class="select" bind:value={selectedYear}>
							<option value={2025}>2025</option>
							<option value={2026}>2026</option>
							<option value={2027}>2027</option>
						</select>
					</div>
					<button class="btn-primary text-lg px-8 py-3" onclick={runComparison} disabled={$syntheticLoading}>
						{#if $syntheticLoading}
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
				<p class="mt-3 text-sm text-warm-500 text-center">
					O mes/ano e usado para calcular as horas previstas dos PJs (dias uteis x 8h)
				</p>
			</div>
		</div>
	{/if}

	<!-- Results Section -->
	{#if $syntheticComparison}
		<div class="space-y-6">
			<!-- Statistics -->
			<div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
				<MetricCard
					title="Total"
					value={$syntheticComparison.statistics.total_collaborators}
					icon="users"
					variant="default"
				/>
				<MetricCard
					title="CLT"
					value={$syntheticComparison.statistics.total_clt}
					icon="users"
					variant="default"
				/>
				<MetricCard
					title="PJ"
					value={$syntheticComparison.statistics.total_pj}
					icon="users"
					variant="default"
				/>
				<MetricCard
					title="Aprovados"
					value={$syntheticComparison.statistics.approved}
					icon="check"
					variant="success"
				/>
				<MetricCard
					title="Divergentes"
					value={$syntheticComparison.statistics.divergent}
					icon="x"
					variant="error"
				/>
				<MetricCard
					title="% Aprovacao"
					value="{$syntheticComparison.statistics.approval_percentage.toFixed(1)}%"
					icon="chart"
					variant={$syntheticComparison.statistics.approval_percentage >= 90 ? 'success' : $syntheticComparison.statistics.approval_percentage >= 70 ? 'warning' : 'error'}
				/>
			</div>

			<!-- Info Card -->
			<div class="bg-warm-800/50 rounded-lg p-4 border border-warm-700">
				<div class="flex flex-wrap gap-6 text-sm">
					<div>
						<span class="text-warm-400">Periodo:</span>
						<span class="text-warm-200 ml-1">{months.find(m => m.value === $syntheticComparison.month)?.label} {$syntheticComparison.year}</span>
					</div>
					<div>
						<span class="text-warm-400">Dias Uteis:</span>
						<span class="text-warm-200 ml-1">{$syntheticComparison.business_days}</span>
					</div>
					<div>
						<span class="text-warm-400">Horas Previstas PJ:</span>
						<span class="text-warm-200 ml-1">{$syntheticComparison.expected_pj_hours}h</span>
					</div>
				</div>
			</div>

			<!-- Filters and Export -->
			<div class="flex flex-wrap items-center justify-between gap-4">
				<div class="flex flex-wrap items-center gap-4">
					<select
						class="select"
						bind:value={$typeFilter}
					>
						<option value="all">Todos os Tipos</option>
						<option value="CLT">CLT</option>
						<option value="PJ">PJ</option>
					</select>

					<select
						class="select"
						bind:value={$statusFilter}
					>
						<option value="all">Todos os Status</option>
						<option value="Aprovado">Aprovados</option>
						<option value="Divergente">Divergentes</option>
						<option value="Não Encontrado">Nao Encontrados</option>
					</select>

					<select
						class="select"
						bind:value={$categoryFilter}
					>
						<option value="all">Todas Categorias</option>
						<option value="Aprovado">Aprovado</option>
						<option value="Mais Trabalhadas">Mais Trabalhadas</option>
						<option value="Menos Trabalhadas">Menos Trabalhadas</option>
					</select>
				</div>

				<ExportButton
					csvUrl={api.getExportCsvUrl($syntheticComparison.id)}
					excelUrl={api.getExportExcelUrl($syntheticComparison.id)}
				/>
			</div>

			<!-- Results Table -->
			<DataTable {columns} data={$filteredResults} emptyMessage="Nenhum resultado encontrado" maxHeight="500px" />

			<p class="text-sm text-warm-500">
				Exibindo {$filteredResults.length} de {$syntheticComparison.results.length} colaboradores
			</p>
		</div>
	{/if}
</div>
