<script lang="ts">
	import StatusBadge from './StatusBadge.svelte';

	type Column = {
		key: string;
		label: string;
		type?: 'text' | 'number' | 'status' | 'hours' | 'badge';
		align?: 'left' | 'center' | 'right';
	};

	export let columns: Column[] = [];
	export let data: Record<string, any>[] = [];
	export let emptyMessage: string = 'No data available';
	export let maxHeight: string = '400px';

	function formatValue(value: any, type?: string): string {
		if (value === null || value === undefined) return '-';

		if (type === 'hours' && typeof value === 'number') {
			const hours = Math.floor(value);
			const minutes = Math.round((value - hours) * 60);
			return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
		}

		if (type === 'number' && typeof value === 'number') {
			return value.toFixed(2);
		}

		return String(value);
	}

	function getStatusVariant(
		status: string
	): 'success' | 'error' | 'warning' | 'info' | 'neutral' {
		const statusLower = status.toLowerCase();
		if (statusLower.includes('approved') || statusLower.includes('ok') || statusLower.includes('sem divergencia') || statusLower.includes('aprovado')) {
			return 'success';
		}
		if (statusLower.includes('divergent') || statusLower.includes('divergencia') || statusLower.includes('erro') || statusLower.includes('divergente')) {
			return 'error';
		}
		if (statusLower.includes('not_found') || statusLower.includes('nao encontrado') || statusLower.includes('manual') || statusLower.includes('não encontrado')) {
			return 'warning';
		}
		return 'neutral';
	}

	function getBadgeVariant(value: string): 'success' | 'error' | 'warning' | 'info' | 'neutral' {
		if (value === 'CLT') return 'info';
		if (value === 'PJ') return 'warning';
		return 'neutral';
	}
</script>

<div class="table-container">
	<div class="overflow-auto" style="max-height: {maxHeight}">
		<table class="table">
			<thead>
				<tr>
					{#each columns as column}
						<th
							scope="col"
							class:text-left={column.align !== 'center' && column.align !== 'right'}
							class:text-center={column.align === 'center'}
							class:text-right={column.align === 'right'}
						>
							{column.label}
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#if data.length === 0}
					<tr>
						<td colspan={columns.length} class="px-4 py-8 text-center text-sm text-warm-500">
							{emptyMessage}
						</td>
					</tr>
				{:else}
					{#each data as row, index}
						<tr>
							{#each columns as column}
								<td
									class:text-left={column.align !== 'center' && column.align !== 'right'}
									class:text-center={column.align === 'center'}
									class:text-right={column.align === 'right'}
								>
									{#if column.type === 'status'}
										<StatusBadge
											status={formatValue(row[column.key], column.type)}
											variant={getStatusVariant(row[column.key])}
										/>
									{:else if column.type === 'badge'}
										<StatusBadge
											status={row[column.key]}
											variant={getBadgeVariant(row[column.key])}
										/>
									{:else}
										<span class="text-warm-200">
											{formatValue(row[column.key], column.type)}
										</span>
									{/if}
								</td>
							{/each}
						</tr>
					{/each}
				{/if}
			</tbody>
		</table>
	</div>
</div>
