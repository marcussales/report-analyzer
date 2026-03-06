<script lang="ts">
	export let csvUrl: string = '';
	export let excelUrl: string = '';
	export let disabled: boolean = false;

	let showDropdown = false;

	function download(url: string) {
		if (disabled || !url) return;
		window.location.href = url;
		showDropdown = false;
	}
</script>

<div class="relative inline-block text-left">
	<button
		type="button"
		class="btn-primary"
		{disabled}
		on:click={() => (showDropdown = !showDropdown)}
	>
		<svg class="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
			/>
		</svg>
		Exportar
		<svg class="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if showDropdown}
		<div
			class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-lg bg-dark-200 border border-dark-50 shadow-dark-lg focus:outline-none"
		>
			<div class="py-1">
				{#if csvUrl}
					<button
						class="w-full px-4 py-2.5 text-left text-sm text-warm-300 hover:bg-dark-100 transition-colors duration-150"
						on:click={() => download(csvUrl)}
					>
						<svg
							class="inline-block mr-2 h-4 w-4 text-warm-500"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						Exportar CSV
					</button>
				{/if}
				{#if excelUrl}
					<button
						class="w-full px-4 py-2.5 text-left text-sm text-warm-300 hover:bg-dark-100 transition-colors duration-150"
						on:click={() => download(excelUrl)}
					>
						<svg
							class="inline-block mr-2 h-4 w-4 text-success-400"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
							/>
						</svg>
						Exportar Excel
					</button>
				{/if}
			</div>
		</div>
	{/if}
</div>

{#if showDropdown}
	<!-- svelte-ignore a11y_click_events_have_key_events -->
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="fixed inset-0 z-0" on:click={() => (showDropdown = false)}></div>
{/if}
