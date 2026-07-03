<script lang="ts">
	import { goto } from '$app/navigation';

	import { WEBUI_NAME, showSidebar } from '$lib/stores';
	import { askCampusKnowledge, type CampusKnowledgeAskResponse } from '$lib/apis/campus/knowledge';

	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import BookOpen from '$lib/components/icons/BookOpen.svelte';
	import ChevronRight from '$lib/components/icons/ChevronRight.svelte';
	import Clipboard from '$lib/components/icons/Clipboard.svelte';
	import Component from '$lib/components/icons/Component.svelte';
	import Document from '$lib/components/icons/Document.svelte';
	import DocumentPage from '$lib/components/icons/DocumentPage.svelte';
	import Grid from '$lib/components/icons/Grid.svelte';
	import Home from '$lib/components/icons/Home.svelte';
	import Note from '$lib/components/icons/Note.svelte';
	import QuestionMarkCircle from '$lib/components/icons/QuestionMarkCircle.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import Sparkles from '$lib/components/icons/Sparkles.svelte';
	import User from '$lib/components/icons/User.svelte';

	type LibraryTone = 'blue' | 'cyan' | 'green' | 'amber' | 'purple' | 'slate';

	type LibraryCategory = {
		id: string;
		title: string;
		count: number;
		description: string;
		icon: typeof DocumentPage;
		tone: LibraryTone;
	};

	type HotQuestion = {
		id: string;
		title: string;
		teacher: string;
		likes: number;
	};

	const libraryCategories: LibraryCategory[] = [
		{
			id: 'rules',
			title: '制度文件',
			count: 86,
			description: '校内制度、办法、规则',
			icon: BookOpen,
			tone: 'blue'
		},
		{
			id: 'policy',
			title: '政策文件',
			count: 124,
			description: '上级政策、教育法规',
			icon: Document,
			tone: 'cyan'
		},
		{
			id: 'work-plan',
			title: '工作方案',
			count: 73,
			description: '各类专项方案',
			icon: Clipboard,
			tone: 'green'
		},
		{
			id: 'case-template',
			title: '案例模板',
			count: 58,
			description: '历史案例参考',
			icon: ArchiveBox,
			tone: 'amber'
		},
		{
			id: 'research',
			title: '历史研判',
			count: 142,
			description: 'AI 生成的过往研判',
			icon: Sparkles,
			tone: 'purple'
		},
		{
			id: 'qa',
			title: '问答库 · 精选',
			count: 32,
			description: '问吧沉淀的高频答案',
			icon: QuestionMarkCircle,
			tone: 'slate'
		}
	];

	const hotQuestions: HotQuestion[] = [
		{
			id: 'late-homework-rule',
			title: '连续请假超过 3 天有什么规定？',
			teacher: '陈校长',
			likes: 12
		},
		{
			id: 'school-supervision',
			title: '校车管理有什么规定？',
			teacher: '刘老师',
			likes: 2
		},
		{
			id: 'canteen-check',
			title: '校园安全检查的频次规定？',
			teacher: '王主任',
			likes: 8
		},
		{
			id: 'double-reduction',
			title: '“双减”对作业的具体要求？',
			teacher: '李老师',
			likes: 23
		}
	];

	const bottomNav = [
		{ id: 'school', label: '校情', icon: Home, href: '/' },
		{ id: 'apps', label: '应用', icon: Grid, href: '/apps' },
		{ id: 'insight', label: '研判', icon: Sparkles, href: '/apps' },
		{ id: 'knowledge', label: '智库', icon: Note, href: '/apps' },
		{ id: 'mine', label: '我的', icon: User, href: '/apps' }
	];

	let question = '';
	let asking = false;
	let answer: CampusKnowledgeAskResponse | null = null;
	let askError = '';

	const toneClass = (tone: LibraryTone) => {
		const classes = {
			blue: 'bg-blue-50 text-blue-600 ring-blue-100',
			cyan: 'bg-cyan-50 text-cyan-600 ring-cyan-100',
			green: 'bg-emerald-50 text-emerald-600 ring-emerald-100',
			amber: 'bg-amber-50 text-amber-600 ring-amber-100',
			purple: 'bg-violet-50 text-violet-600 ring-violet-100',
			slate: 'bg-slate-50 text-slate-600 ring-slate-200'
		};

		return classes[tone];
	};

	const navigateTo = (href: string) => {
		goto(href);
	};

	const askHandler = async () => {
		const trimmedQuestion = question.trim();
		if (!trimmedQuestion || asking) {
			return;
		}

		asking = true;
		answer = null;
		askError = '';

		try {
			answer = await askCampusKnowledge(localStorage.token, trimmedQuestion);
		} catch (error) {
			askError = `${error}`;
		} finally {
			asking = false;
		}
	};
</script>

<svelte:head>
	<title>智库 • {$WEBUI_NAME}</title>
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

					<div
						class="rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-medium text-emerald-700"
					>
						本周 +8
					</div>
				</div>

				<div class="mt-3 flex items-end gap-3">
					<h1 class="text-[24px] font-semibold leading-8 tracking-normal">智库</h1>
					<p class="pb-1 text-xs text-slate-500">依据中心 · 415 份 · 被研判引用 1,142 次</p>
				</div>
			</section>

			<section class="relative shrink-0 bg-[#f4f7fc] px-4 pb-3 pt-3">
				<div
					class="flex items-center gap-2 rounded-xl border border-blue-100 bg-white p-1.5 shadow-[0_8px_24px_rgba(42,67,180,0.08)]"
				>
					<div class="flex min-w-0 flex-1 items-center gap-2 px-2">
						<Sparkles className="size-4 shrink-0 text-blue-600" strokeWidth="2" />
						<input
							bind:value={question}
							class="h-9 min-w-0 flex-1 bg-transparent text-sm font-medium text-slate-700 outline-hidden placeholder:text-slate-400"
							placeholder="“听评课考核办法是什么？”"
							aria-label="输入智库问题"
							on:keydown={(event) => {
								if (event.key === 'Enter') {
									askHandler();
								}
							}}
						/>
					</div>

					<button
						type="button"
						class="flex h-9 shrink-0 items-center gap-1 rounded-lg bg-blue-700 px-3 text-sm font-semibold text-white shadow-[0_8px_18px_rgba(37,78,210,0.24)] transition active:scale-[0.98]"
						disabled={asking}
						on:click={askHandler}
					>
						<Search className="size-3.5" strokeWidth="2.3" />
						{asking ? '问中' : '问'}
					</button>
				</div>

				<p class="mt-2 truncate px-1 text-[11px] leading-4 text-slate-400">
					只引制度条款 · 带原文出处 · 不替你做判断（需判断请发起研判）
				</p>

				{#if askError}
					<div
						class="mt-3 rounded-xl border border-amber-100 bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-700"
					>
						{askError}
					</div>
				{:else if answer}
					<div
						class="mt-3 rounded-xl border border-blue-100 bg-white px-3 py-3 shadow-[0_8px_24px_rgba(42,67,180,0.08)]"
					>
						<div class="text-xs font-semibold text-blue-700">RAGFlow 回答</div>
						<div class="mt-1 line-clamp-4 whitespace-pre-wrap text-xs leading-5 text-slate-700">
							{answer.answer}
						</div>
						{#if answer.references.length > 0}
							<div class="mt-2 truncate text-[11px] text-slate-400">
								引用 {answer.references.length} 条 · {answer.references[0]?.document_name ??
									'来源文档'}
							</div>
						{/if}
					</div>
				{/if}
			</section>

			<section
				class="relative min-h-0 flex-1 overflow-y-auto overscroll-contain px-4 pb-4 [-webkit-overflow-scrolling:touch]"
			>
				<div class="flex items-center justify-between pb-2 pt-1">
					<div class="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
						<Component className="size-3.5" strokeWidth="2" />
						分类浏览
					</div>
					<div class="text-[11px] text-slate-500">共 6 大类</div>
				</div>

				<div class="grid grid-cols-2 gap-2.5">
					{#each libraryCategories as category}
						<button
							type="button"
							class="min-w-0 rounded-xl border border-slate-200/80 bg-white p-3 text-left shadow-[0_1px_2px_rgba(31,35,41,0.04),0_8px_22px_rgba(31,35,41,0.05)] transition active:scale-[0.985]"
							aria-label={`打开${category.title}`}
						>
							<div class="flex items-center gap-3">
								<div
									class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ring-1 {toneClass(
										category.tone
									)}"
								>
									<svelte:component this={category.icon} className="size-4.5" strokeWidth="2" />
								</div>

								<div class="min-w-0">
									<div class="truncate text-sm font-semibold text-slate-950">
										{category.title}
										<span class="ml-1 text-[11px] font-medium text-slate-400">{category.count}</span
										>
									</div>
									<div class="mt-0.5 truncate text-[11px] leading-4 text-slate-400">
										{category.description}
									</div>
								</div>
							</div>
						</button>
					{/each}
				</div>

				<div class="mt-4 flex items-center justify-between">
					<div class="flex min-w-0 items-center gap-1.5 text-sm font-semibold text-slate-900">
						<QuestionMarkCircle className="size-3.5 shrink-0 text-blue-700" strokeWidth="2" />
						<span class="truncate">问吧 · 大家都在问</span>
						<span class="text-xs font-normal text-slate-400">· 与「精选」同一问答库</span>
					</div>
					<button type="button" class="shrink-0 text-[11px] font-semibold text-blue-700">
						全部 56 →
					</button>
				</div>

				<div
					class="mt-2 overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-[0_1px_2px_rgba(31,35,41,0.04),0_8px_22px_rgba(31,35,41,0.05)]"
				>
					{#each hotQuestions as question, index}
						<button
							type="button"
							class="flex w-full items-center gap-3 px-3.5 py-3 text-left transition active:bg-slate-50 {index ===
							0
								? ''
								: 'border-t border-slate-100'}"
							aria-label={`查看问题：${question.title}`}
						>
							<div class="flex h-5 w-5 shrink-0 items-center justify-center text-violet-500">
								<Note className="size-3.5" strokeWidth="2" />
							</div>

							<div class="min-w-0 flex-1">
								<div class="truncate text-[13px] font-semibold leading-5 text-slate-900">
									{question.title}
								</div>
								<div class="mt-0.5 truncate text-[11px] leading-4 text-slate-400">
									{question.teacher} · {question.likes} 人点过
								</div>
							</div>

							<ChevronRight className="size-4 shrink-0 text-slate-300" strokeWidth="2" />
						</button>
					{/each}
				</div>
			</section>

			<nav
				class="relative z-10 shrink-0 border-t border-slate-200/90 bg-white/95 px-2 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur"
				aria-label="智库导航"
			>
				<div class="grid grid-cols-5">
					{#each bottomNav as item}
						<button
							type="button"
							class="flex min-w-0 flex-col items-center gap-1 rounded-lg px-1 py-1 text-[11px] font-medium transition {item.id ===
							'knowledge'
								? 'text-blue-700'
								: 'text-slate-400 hover:bg-slate-50 hover:text-slate-600'}"
							on:click={() => navigateTo(item.href)}
							aria-current={item.id === 'knowledge' ? 'page' : undefined}
						>
							<svelte:component
								this={item.icon}
								className="size-5"
								strokeWidth={item.id === 'knowledge' ? '2' : '1.7'}
							/>
							<span class="truncate">{item.label}</span>
						</button>
					{/each}
				</div>
			</nav>
		</main>
	</div>
</div>
