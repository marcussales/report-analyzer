<script lang="ts">
	import MetricCard from '$lib/components/MetricCard.svelte';
</script>

<svelte:head>
	<title>Dashboard - Report Analyzer</title>
</svelte:head>

<div class="space-y-8">
	<div>
		<h1 class="text-2xl font-bold text-warm-100">Dashboard</h1>
		<p class="mt-2 text-sm text-warm-400">
			Bem-vindo ao Report Analyzer. Selecione uma das opcoes abaixo para comecar.
		</p>
	</div>

	<div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
		<!-- Synthetic vs Billing Card -->
		<a href="/synthetic" class="block group">
			<div
				class="card hover:shadow-glow transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-accent-500/50"
			>
				<div class="card-header bg-accent-500/10">
					<h3 class="text-lg font-semibold text-accent-400">Sintetico vs Faturamento</h3>
				</div>
				<div class="card-body">
					<p class="text-warm-400 mb-4">
						Compare o relatorio sintetico de colaboradores com o relatorio de faturamento.
						Identifique divergencias de horas trabalhadas vs horas apropriadas.
					</p>
					<div class="flex flex-wrap gap-2">
						<span class="badge-info">
							Excel
						</span>
						<span class="badge-error">
							PDF
						</span>
						<span class="badge-success">
							Export CSV/Excel
						</span>
					</div>
				</div>
			</div>
		</a>

		<!-- Detail Comparison Card -->
		<a href="/detail" class="block group">
			<div
				class="card hover:shadow-glow transition-all duration-200 cursor-pointer border-2 border-transparent hover:border-success-400/50"
			>
				<div class="card-header bg-success-50">
					<h3 class="text-lg font-semibold text-success-400">Ponto vs Apropriacao</h3>
				</div>
				<div class="card-body">
					<p class="text-warm-400 mb-4">
						Compare a folha de ponto (PDF) com o relatorio de apropriacao (Excel).
						Identifique divergencias dia a dia e marcacoes manuais.
					</p>
					<div class="flex flex-wrap gap-2">
						<span class="badge-error">
							PDF
						</span>
						<span class="badge-info">
							Excel
						</span>
						<span class="badge-success">
							Export CSV/Excel
						</span>
					</div>
				</div>
			</div>
		</a>
	</div>

	<div class="mt-8">
		<h2 class="text-lg font-semibold text-warm-200 mb-4">Funcionalidades</h2>
		<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
			<MetricCard title="Upload de Arquivos" value="Drag & Drop" icon="chart" variant="info" />
			<MetricCard
				title="Normalizacao de Nomes"
				value="Automatica"
				icon="users"
				variant="success"
			/>
			<MetricCard title="Conversao de Tempo" value="HH:MM <-> Decimal" icon="clock" variant="warning" />
			<MetricCard title="Export de Dados" value="CSV / Excel" icon="check" variant="default" />
		</div>
	</div>
</div>
