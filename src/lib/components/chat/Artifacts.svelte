<script lang="ts">
	import { onMount, getContext, createEventDispatcher } from 'svelte';
	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	import {
		artifactCode,
		chatId,
		config,
		settings,
		showArtifacts,
		showControls,
		artifactContents
	} from '$lib/stores';
	import { copyToClipboard } from '$lib/utils';
	import { injectCsp } from '$lib/utils/csp';

	import XMark from '../icons/XMark.svelte';
	import ArrowsPointingOut from '../icons/ArrowsPointingOut.svelte';
	import Tooltip from '../common/Tooltip.svelte';
	import SvgPanZoom from '../common/SVGPanZoom.svelte';
	import Download from '../icons/Download.svelte';
	import Markdown from './Messages/Markdown.svelte';

	export let overlay = false;

	let contents: Array<{ type: string; content: string }> = [];
	let selectedContentIdx = 0;

	let copied = false;
	let iframeElement: HTMLIFrameElement;

	const parseImageArtifactContent = (content: string) => {
		const trimmed = content.trim();

		if (!trimmed) {
			return { url: '', error: 'Image artifact is missing a URL.' };
		}

		if (!trimmed.startsWith('{')) {
			return { url: trimmed, name: '', alt: '' };
		}

		try {
			const data = JSON.parse(trimmed);
			if (!data || typeof data.url !== 'string' || !data.url.trim()) {
				return { url: '', error: 'Image artifact payload must include a URL.' };
			}

			return {
				url: data.url,
				name: typeof data.name === 'string' ? data.name : '',
				alt: typeof data.alt === 'string' ? data.alt : '',
				prompt: typeof data.prompt === 'string' ? data.prompt : ''
			};
		} catch {
			return { url: '', error: 'Image artifact payload is not valid JSON.' };
		}
	};

	function navigateContent(direction: 'prev' | 'next') {
		selectedContentIdx =
			direction === 'prev'
				? Math.max(selectedContentIdx - 1, 0)
				: Math.min(selectedContentIdx + 1, contents.length - 1);
	}

	const iframeLoadHandler = () => {
		iframeElement.contentWindow.addEventListener(
			'click',
			function (e) {
				const target = e.target.closest('a');
				if (target && target.href) {
					e.preventDefault();
					const url = new URL(target.href, iframeElement.baseURI);
					if (url.origin === window.location.origin) {
						iframeElement.contentWindow.history.pushState(
							null,
							'',
							url.pathname + url.search + url.hash
						);
					} else {
						console.info('External navigation blocked:', url.href);
					}
				}
			},
			true
		);

		// Cancel drag when hovering over iframe
		iframeElement.contentWindow.addEventListener('mouseenter', function (e) {
			e.preventDefault();
			iframeElement.contentWindow.addEventListener('dragstart', (event) => {
				event.preventDefault();
			});
		});
	};

	const showFullScreen = () => {
		if (iframeElement.requestFullscreen) {
			iframeElement.requestFullscreen();
		} else if (iframeElement.webkitRequestFullscreen) {
			iframeElement.webkitRequestFullscreen();
		} else if (iframeElement.msRequestFullscreen) {
			iframeElement.msRequestFullscreen();
		}
	};

	const getDownloadMeta = (type: string) => {
		if (type === 'image') {
			return { extension: 'png', mimeType: 'image/png' };
		}

		if (type === 'document' || type === 'report') {
			return { extension: 'md', mimeType: 'text/markdown' };
		}

		if (type === 'svg') {
			return { extension: 'svg', mimeType: 'image/svg+xml' };
		}

		return { extension: 'html', mimeType: 'text/html' };
	};

	const downloadArtifact = () => {
		const content = contents[selectedContentIdx];

		if (content.type === 'image') {
			const image = parseImageArtifactContent(content.content);
			if (!image.url) {
				return;
			}

			const a = document.createElement('a');
			a.href = image.url;
			a.download = image.name || `artifact-${$chatId}-${selectedContentIdx}.png`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			return;
		}

		const { extension, mimeType } = getDownloadMeta(content.type);
		const blob = new Blob([content.content], { type: mimeType });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `artifact-${$chatId}-${selectedContentIdx}.${extension}`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	};

	onMount(() => {
		const unsubscribeArtifactCode = artifactCode.subscribe((value) => {
			if (contents) {
				const codeIdx = contents.findIndex((content) => content.content.includes(value));
				selectedContentIdx = codeIdx !== -1 ? codeIdx : 0;
			}
		});

		const unsubscribeArtifactContents = artifactContents.subscribe((value) => {
			const newContents = value ?? [];
			console.log('Artifact contents updated:', newContents);

			if (newContents.length === 0) {
				showControls.set(false);
				showArtifacts.set(false);
				selectedContentIdx = 0;
			} else if (newContents.length > contents.length) {
				selectedContentIdx = newContents.length - 1;
			}

			contents = newContents;
		});

		return () => {
			unsubscribeArtifactCode();
			unsubscribeArtifactContents();
		};
	});
</script>

<div
	class=" w-full h-full relative flex flex-col bg-white dark:bg-gray-850"
	id="artifacts-container"
>
	<div class="w-full h-full flex flex-col flex-1 relative">
		{#if contents.length > 0}
			<div
				class="pointer-events-auto z-20 flex justify-between items-center p-2.5 font-primar text-gray-900 dark:text-white"
			>
				<div class="flex-1 flex items-center justify-between pr-1">
					<div class="flex items-center space-x-2">
						<div class="flex items-center gap-0.5 self-center min-w-fit" dir="ltr">
							<button
								class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition disabled:cursor-not-allowed"
								on:click={() => navigateContent('prev')}
								disabled={contents.length <= 1}
								aria-label={$i18n.t('Previous version')}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2.5"
									class="size-3.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M15.75 19.5 8.25 12l7.5-7.5"
									/>
								</svg>
							</button>

							<div class="text-xs self-center dark:text-gray-100 min-w-fit">
								{$i18n.t('Version {{selectedVersion}} of {{totalVersions}}', {
									selectedVersion: selectedContentIdx + 1,
									totalVersions: contents.length
								})}
							</div>

							<button
								class="self-center p-1 hover:bg-black/5 dark:hover:bg-white/5 dark:hover:text-white hover:text-black rounded-md transition disabled:cursor-not-allowed"
								on:click={() => navigateContent('next')}
								disabled={contents.length <= 1}
								aria-label={$i18n.t('Next version')}
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2.5"
									class="size-3.5"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="m8.25 4.5 7.5 7.5-7.5 7.5"
									/>
								</svg>
							</button>
						</div>
					</div>

					<div class="flex items-center gap-1.5">
						<button
							class="copy-code-button bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md px-1.5 py-0.5"
							on:click={() => {
								copyToClipboard(contents[selectedContentIdx].content);
								copied = true;

								setTimeout(() => {
									copied = false;
								}, 2000);
							}}>{copied ? $i18n.t('Copied') : $i18n.t('Copy')}</button
						>

						<Tooltip content={$i18n.t('Download')}>
							<button
								class=" bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md p-0.5"
								on:click={downloadArtifact}
							>
								<Download className="size-3.5" />
							</button>
						</Tooltip>

						{#if contents[selectedContentIdx].type === 'iframe'}
							<Tooltip content={$i18n.t('Open in full screen')}>
								<button
									class=" bg-none border-none text-xs bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 transition rounded-md p-0.5"
									on:click={showFullScreen}
								>
									<ArrowsPointingOut className="size-3.5" />
								</button>
							</Tooltip>
						{/if}
					</div>
				</div>

				<button
					class="self-center pointer-events-auto p-1 rounded-full bg-white dark:bg-gray-850"
					on:click={() => {
						dispatch('close');
						showControls.set(false);
						showArtifacts.set(false);
					}}
				>
					<XMark className="size-3.5 text-gray-900 dark:text-white" />
				</button>
			</div>
		{/if}

		{#if overlay}
			<div class=" absolute top-0 left-0 right-0 bottom-0 z-10"></div>
		{/if}

		<div class="flex-1 w-full h-full">
			<div class=" h-full flex flex-col">
				{#if contents.length > 0}
					<div class="max-w-full w-full h-full">
						{#if contents[selectedContentIdx].type === 'iframe'}
							<iframe
								bind:this={iframeElement}
								title="Content"
								srcdoc={injectCsp(
									contents[selectedContentIdx].content,
									$config?.ui?.iframe_csp ?? ''
								)}
								class="w-full border-0 h-full rounded-none"
								sandbox="allow-scripts allow-downloads{($settings?.iframeSandboxAllowForms ?? false)
									? ' allow-forms'
									: ''}{($settings?.iframeSandboxAllowSameOrigin ?? false)
									? ' allow-same-origin'
									: ''}"
								on:load={iframeLoadHandler}
							></iframe>
						{:else if contents[selectedContentIdx].type === 'svg'}
							<SvgPanZoom
								className=" w-full h-full max-h-full overflow-hidden"
								svg={contents[selectedContentIdx].content}
							/>
						{:else if contents[selectedContentIdx].type === 'image'}
							{@const imageArtifact = parseImageArtifactContent(
								contents[selectedContentIdx].content
							)}
							<div
								class="h-full overflow-auto bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100"
							>
								<div class="flex min-h-full items-center justify-center p-6">
									{#if imageArtifact.error}
										<div class="text-sm text-gray-600 dark:text-gray-300">
											{imageArtifact.error}
										</div>
									{:else}
										<div class="flex h-full w-full flex-col items-center justify-center gap-3">
											<img
												class="max-h-[calc(100vh-7rem)] max-w-full rounded-md object-contain shadow-sm"
												src={imageArtifact.url}
												alt={imageArtifact.alt || imageArtifact.name || 'Generated image'}
											/>
											{#if imageArtifact.prompt}
												<div class="max-w-3xl text-center text-xs text-gray-500 dark:text-gray-400">
													{imageArtifact.prompt}
												</div>
											{/if}
										</div>
									{/if}
								</div>
							</div>
						{:else if ['document', 'report'].includes(contents[selectedContentIdx].type)}
							<div
								class="h-full overflow-auto bg-gray-50 text-gray-900 dark:bg-gray-950 dark:text-gray-100"
							>
								<div
									class="mx-auto min-h-full w-full max-w-4xl bg-white px-8 py-10 shadow-sm dark:bg-gray-900 sm:px-12 lg:px-16"
								>
									<div class="prose max-w-none dark:prose-invert prose-headings:font-semibold">
										<Markdown
											id={`artifact-${$chatId}-${selectedContentIdx}`}
											content={contents[selectedContentIdx].content}
											done={true}
											editCodeBlock={false}
											allowEmbeds={false}
										/>
									</div>
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<div class="m-auto font-medium text-xs text-gray-900 dark:text-white">
						{$i18n.t('No artifact content found.')}
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
