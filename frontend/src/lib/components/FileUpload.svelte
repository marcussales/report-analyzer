<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	export let accept: string = '.xlsx,.xls,.pdf';
	export let label: string = 'Upload File';
	export let description: string = 'Drag and drop or click to select';
	export let loading: boolean = false;
	export let disabled: boolean = false;
	export let multiple: boolean = false;

	const dispatch = createEventDispatcher<{ upload: File; uploadMultiple: File[] }>();

	let dragOver = false;
	let fileInput: HTMLInputElement;

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		if (!disabled && !loading) {
			dragOver = true;
		}
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		dragOver = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		dragOver = false;

		if (disabled || loading) return;

		const files = e.dataTransfer?.files;
		if (files && files.length > 0) {
			if (multiple) {
				const validFiles = Array.from(files).filter(isValidFile);
				if (validFiles.length > 0) {
					dispatch('uploadMultiple', validFiles);
				}
			} else {
				const file = files[0];
				if (isValidFile(file)) {
					dispatch('upload', file);
				}
			}
		}
	}

	function handleFileSelect(e: Event) {
		const target = e.target as HTMLInputElement;
		const files = target.files;
		if (files && files.length > 0) {
			if (multiple) {
				const validFiles = Array.from(files).filter(isValidFile);
				if (validFiles.length > 0) {
					dispatch('uploadMultiple', validFiles);
				}
			} else {
				dispatch('upload', files[0]);
			}
		}
	}

	function isValidFile(file: File): boolean {
		const extensions = accept.split(',').map((ext) => ext.trim().toLowerCase());
		const fileName = file.name.toLowerCase();
		return extensions.some((ext) => fileName.endsWith(ext));
	}

	function openFileDialog() {
		if (!disabled && !loading) {
			fileInput.click();
		}
	}
</script>

<div
	class="upload-zone"
	class:drag-over={dragOver}
	class:disabled={disabled || loading}
	role="button"
	tabindex="0"
	on:dragover={handleDragOver}
	on:dragleave={handleDragLeave}
	on:drop={handleDrop}
	on:click={openFileDialog}
	on:keydown={(e) => e.key === 'Enter' && openFileDialog()}
>
	<input
		bind:this={fileInput}
		type="file"
		{accept}
		{multiple}
		class="hidden"
		on:change={handleFileSelect}
		{disabled}
	/>

	{#if loading}
		<div class="flex flex-col items-center gap-2">
			<svg
				class="animate-spin h-10 w-10 text-accent-500"
				xmlns="http://www.w3.org/2000/svg"
				fill="none"
				viewBox="0 0 24 24"
			>
				<circle
					class="opacity-25"
					cx="12"
					cy="12"
					r="10"
					stroke="currentColor"
					stroke-width="4"
				></circle>
				<path
					class="opacity-75"
					fill="currentColor"
					d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
				></path>
			</svg>
			<span class="text-sm text-warm-500">Processando...</span>
		</div>
	{:else}
		<svg
			class="mx-auto h-12 w-12 text-warm-600"
			stroke="currentColor"
			fill="none"
			viewBox="0 0 48 48"
		>
			<path
				d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
				stroke-width="2"
				stroke-linecap="round"
				stroke-linejoin="round"
			/>
		</svg>
		<div class="mt-4 flex text-sm leading-6 text-warm-400">
			<span class="font-semibold text-accent-400 hover:text-accent-300">{label}</span>
		</div>
		<p class="text-xs leading-5 text-warm-500">{description}</p>
		{#if multiple}
			<p class="text-xs leading-5 text-warm-600 mt-1">Voce pode selecionar multiplos arquivos</p>
		{/if}
	{/if}
</div>
