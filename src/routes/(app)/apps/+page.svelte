<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	import { WEBUI_NAME, showSidebar } from '$lib/stores';
	import { getCampusApps, type CampusAgentApp } from '$lib/apis/campus/apps';

	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import ChevronRight from '$lib/components/icons/ChevronRight.svelte';
	import Component from '$lib/components/icons/Component.svelte';
	import Document from '$lib/components/icons/Document.svelte';
	import Grid from '$lib/components/icons/Grid.svelte';
	import Home from '$lib/components/icons/Home.svelte';
	import Note from '$lib/components/icons/Note.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import Sparkles from '$lib/components/icons/Sparkles.svelte';
	import User from '$lib/components/icons/User.svelte';

	type AppCategory = {
		id: string;
		label: string;
		apps: CampusAgentApp[];
	};

	type AppIcon = typeof Grid;

	const bottomNav = [
		{ id: 'school', label: '校情', icon: Home, href: '/' },
		{ id: 'apps', label: '应用', icon: Grid, href: '/apps' },
		{ id: 'insight', label: '研判', icon: Sparkles, href: '/apps' },
		{ id: 'knowledge', label: '智库', icon: Note, href: '/apps' },
		{ id: 'mine', label: '我的', icon: User, href: '/apps' }
	];

	const iconMap: Record<string, AppIcon> = {
		book: BookOpen,
		component: Component,
		document: Document,
		grid: Grid,
		home: Home,
		note: Note,
		search: Search,
		sparkles: Sparkles
	};

	let apps: CampusAgentApp[] = [];
	let loading = true;
	let loadError = '';
	let activeCategory = 'all';
	let frameApp: CampusAgentApp | null = null;

	$: categories = groupAppsByCategory(apps);
	$: filteredApps =
		activeCategory === 'all' ? apps : apps.filter((app) => app.category === activeCategory);

	const getAppIcon = (icon: string) => iconMap[icon] ?? Grid;

	const groupAppsByCategory = (items: CampusAgentApp[]): AppCategory[] => {
		const grouped = new Map<string, AppCategory>();

		for (const app of items) {
			if (!grouped.has(app.category)) {
				grouped.set(app.category, {
					id: app.category,
					label: app.category_label,
					apps: []
				});
			}

			grouped.get(app.category)?.apps.push(app);
		}

		return Array.from(grouped.values());
	};

	const openApp = (app: CampusAgentApp) => {
		if (app.display_mode === 'native') {
			goto(app.entry_url);
			return;
		}

		if (app.display_mode === 'iframe') {
			frameApp = app;
			return;
		}

		window.open(app.entry_url, '_blank', 'noopener,noreferrer');
	};

	const navigateTo = (href: string) => {
		goto(href);
	};

	onMount(async () => {
		try {
			apps = await getCampusApps(localStorage.token);
		} catch (error) {
			loadError = `${error}`;
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>应用中心 • {$WEBUI_NAME}</title>
</svelte:head>

<div
	class="flex h-screen max-h-[100dvh] w-full flex-col overflow-hidden bg-[#f3f6fb] transition-width duration-200 ease-in-out {$showSidebar
		? 'md:max-w-[calc(100%-var(--sidebar-width))]'
		: ''}"
>
	<div class="flex min-h-0 flex-1 justify-center overflow-hidden">
		<main
			class="relative flex h-full max-h-[100dvh] w-full max-w-[430px] flex-col overflow-hidden bg-[#f4f7fc] text-slate-950 shadow-sm"
		>
			<div
				class="pointer-events-none absolute inset-0 bg-[linear-gradient(145deg,transparent_0%,transparent_36%,rgba(64,93,230,0.05)_36.2%,rgba(64,93,230,0.05)_36.8%,transparent_37%)]"
			></div>

			<section class="relative shrink-0 border-b border-slate-200/80 bg-white px-5 pb-4 pt-3">
				<div class="flex items-center justify-between gap-3">
					<button
						type="button"
						class="flex min-w-0 items-center gap-1 text-[11px] font-medium text-slate-600"
						aria-label="切换学校视角"
					>
						<span
							class="flex h-4 w-4 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-[9px] text-blue-700"
							>学</span
						>
						<span class="truncate">屹力中学 · 德育主任视角</span>
						<ChevronRight className="size-3 rotate-90 text-slate-400" strokeWidth="2" />
					</button>

					<div class="rounded-full bg-blue-50 px-3 py-1 text-[11px] font-medium text-blue-700">
						{apps.length} 个应用
					</div>
				</div>

				<div class="mt-3 flex items-end gap-3">
					<h1 class="text-[24px] font-semibold leading-8 tracking-normal">应用中心</h1>
					<p class="pb-1 text-xs text-slate-500">智能体 · 工具 · 智库 · 画布</p>
				</div>
			</section>

			<section class="relative shrink-0 bg-[#f4f7fc] px-4 pb-3 pt-3">
				<div
					class="flex items-center gap-2 rounded-xl border border-blue-100 bg-white px-3 py-2 shadow-[0_8px_24px_rgba(42,67,180,0.08)]"
				>
					<Search className="size-4 shrink-0 text-blue-600" strokeWidth="2" />
					<input
						class="h-8 min-w-0 flex-1 bg-transparent text-sm font-medium text-slate-700 outline-hidden placeholder:text-slate-400"
						placeholder="搜索应用、智能体或工具"
						aria-label="搜索应用"
					/>
				</div>

				<div class="mt-3 flex gap-2 overflow-x-auto pb-1 [-webkit-overflow-scrolling:touch]">
					<button
						type="button"
						class="shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium transition {activeCategory ===
						'all'
							? 'border-blue-100 bg-blue-50 text-blue-700'
							: 'border-slate-200 bg-white text-slate-500'}"
						on:click={() => (activeCategory = 'all')}
					>
						全部
					</button>
					{#each categories as category}
						<button
							type="button"
							class="shrink-0 rounded-full border px-3 py-1.5 text-xs font-medium transition {activeCategory ===
							category.id
								? 'border-blue-100 bg-blue-50 text-blue-700'
								: 'border-slate-200 bg-white text-slate-500'}"
							on:click={() => (activeCategory = category.id)}
						>
							{category.label}
						</button>
					{/each}
				</div>
			</section>

			<section
				class="relative min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 pb-4 [-webkit-overflow-scrolling:touch]"
			>
				{#if loading}
					<div
						class="rounded-xl border border-slate-200/80 bg-white px-4 py-5 text-sm text-slate-500"
					>
						正在加载应用
					</div>
				{:else if loadError}
					<div
						class="rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-700"
					>
						{loadError}
					</div>
				{:else}
					<div class="grid gap-3 pb-2">
						{#each filteredApps as app}
							<button
								type="button"
								class="min-w-0 rounded-xl border border-slate-200/80 bg-white p-3.5 text-left shadow-[0_1px_2px_rgba(31,35,41,0.04),0_8px_22px_rgba(31,35,41,0.05)] transition active:scale-[0.985]"
								aria-label={`打开${app.name}`}
								on:click={() => openApp(app)}
							>
								<div class="flex items-center gap-3">
									<div
										class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700 ring-1 ring-blue-100"
									>
										<svelte:component
											this={getAppIcon(app.icon)}
											className="size-5"
											strokeWidth="2"
										/>
									</div>

									<div class="min-w-0 flex-1">
										<div class="flex min-w-0 items-center gap-2">
											<div class="truncate text-[15px] font-semibold text-slate-950">
												{app.name}
											</div>
											{#if app.badge}
												<span
													class="shrink-0 rounded-md bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-700"
													>{app.badge}</span
												>
											{/if}
										</div>
										<div class="mt-0.5 truncate text-[11px] leading-4 text-slate-400">
											{app.category_label}
										</div>
										<div class="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
											{app.description}
										</div>
									</div>

									<ChevronRight className="size-4 shrink-0 text-slate-300" strokeWidth="2" />
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</section>

			<nav
				class="relative z-10 shrink-0 border-t border-slate-200/90 bg-white/95 px-2 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur"
				aria-label="应用导航"
			>
				<div class="grid grid-cols-5">
					{#each bottomNav as item}
						<button
							type="button"
							class="flex min-w-0 flex-col items-center gap-1 rounded-lg px-1 py-1 text-[11px] font-medium transition {item.id ===
							'apps'
								? 'text-blue-700'
								: 'text-slate-400 hover:bg-slate-50 hover:text-slate-600'}"
							on:click={() => navigateTo(item.href)}
							aria-current={item.id === 'apps' ? 'page' : undefined}
						>
							<svelte:component
								this={item.icon}
								className="size-5"
								strokeWidth={item.id === 'apps' ? '2' : '1.7'}
							/>
							<span class="truncate">{item.label}</span>
						</button>
					{/each}
				</div>
			</nav>

			{#if frameApp}
				<div class="absolute inset-0 z-20 flex flex-col bg-white">
					<div
						class="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 px-4"
					>
						<div class="min-w-0">
							<div class="truncate text-sm font-semibold text-slate-900">{frameApp.name}</div>
							<div class="truncate text-[11px] text-slate-400">{frameApp.entry_url}</div>
						</div>
						<button
							type="button"
							class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-600"
							on:click={() => (frameApp = null)}
						>
							关闭
						</button>
					</div>
					<iframe class="min-h-0 flex-1 border-0" src={frameApp.entry_url} title={frameApp.name}
					></iframe>
				</div>
			{/if}
		</main>
	</div>
</div>
