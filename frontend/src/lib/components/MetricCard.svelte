<script lang="ts">
	export let title: string;
	export let value: string | number;
	export let subtitle: string = '';
	export let icon: 'users' | 'check' | 'x' | 'search' | 'chart' | 'clock' = 'chart';
	export let variant: 'default' | 'success' | 'error' | 'warning' | 'info' = 'default';

	const variantClasses = {
		default: 'bg-dark-100 text-warm-400',
		success: 'bg-success-50 text-success-400',
		error: 'bg-error-50 text-error-400',
		warning: 'bg-warning-50 text-warning-400',
		info: 'bg-accent-500/20 text-accent-400'
	};
</script>

<div class="metric-card">
	<div class="flex items-center">
		<div class="flex-shrink-0">
			<div class="p-3 rounded-lg {variantClasses[variant]}">
				{#if icon === 'users'}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
						/>
					</svg>
				{:else if icon === 'check'}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M5 13l4 4L19 7"
						/>
					</svg>
				{:else if icon === 'x'}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				{:else if icon === 'search'}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
						/>
					</svg>
				{:else if icon === 'clock'}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
						/>
					</svg>
				{:else}
					<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
						/>
					</svg>
				{/if}
			</div>
		</div>
		<div class="ml-5 w-0 flex-1">
			<dl>
				<dt class="metric-label truncate">{title}</dt>
				<dd class="flex items-baseline">
					<div class="metric-value">{value}</div>
					{#if subtitle}
						<div class="ml-2 text-sm text-warm-500">{subtitle}</div>
					{/if}
				</dd>
			</dl>
		</div>
	</div>
</div>
