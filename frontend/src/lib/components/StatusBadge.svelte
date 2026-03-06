<script lang="ts">
	export let status: string;
	export let variant: 'success' | 'error' | 'warning' | 'info' | 'neutral' = 'neutral';

	const variantClasses = {
		success: 'badge-success',
		error: 'badge-error',
		warning: 'badge-warning',
		info: 'badge-info',
		neutral: 'badge-neutral'
	};
</script>

<span class={variantClasses[variant]}>
	{status}
</span>
