<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<div class="min-h-screen bg-dark-300">
	<!-- Navigation -->
	<nav class="bg-dark-200 border-b border-dark-50 sticky top-0 z-50">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="flex h-16 items-center justify-between">
				<div class="flex items-center gap-8">
					<!-- Logo -->
					<a href="/" class="flex items-center gap-3">
						<div class="w-8 h-8 rounded-lg bg-accent-500 flex items-center justify-center">
							<svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
						</div>
						<span class="text-lg font-semibold text-warm-100">Report Analyzer</span>
					</a>

					<!-- Nav Links -->
					<div class="hidden md:flex items-center gap-1">
						<a href="/" class="nav-link">
							Dashboard
						</a>
						<a href="/synthetic" class="nav-link">
							Sintetico vs Faturamento
						</a>
						<a href="/detail" class="nav-link">
							Ponto vs Apropriacao
						</a>
					</div>
				</div>

				<!-- Right side -->
				<div class="flex items-center gap-4">
					<span class="text-xs text-warm-500 hidden sm:block">v1.0.0</span>
				</div>
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="py-8">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			{@render children()}
		</div>
	</main>

	<!-- Footer -->
	<footer class="border-t border-dark-50 py-6 mt-auto">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<p class="text-center text-sm text-warm-600">
				Report Analyzer - Rust + Svelte
			</p>
		</div>
	</footer>
</div>
