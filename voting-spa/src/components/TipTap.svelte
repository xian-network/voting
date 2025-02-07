<script lang="ts">
	import { onMount, onDestroy } from "svelte";
	import { Editor } from "@tiptap/core";
	import StarterKit from "@tiptap/starter-kit";

	export let editable: boolean = true;
	export let content: string = '';
	
	let element: any;
	let editor: any;
	
	onMount(() => {
		editor = new Editor({
			element: element,
			extensions: [StarterKit],
			content: content,
			editable: editable,
			onTransaction: () => {
				// force re-render so `editor.isActive` works as expected
				editor = editor;
				content = editor.getHTML();
			},
			editorProps: {
				attributes: {
					class: "prose prose-sm sm:prose-base lg:prose-lg xl:prose-2xl focus:outline-none",
				},
			},
		});
	});

	onDestroy(() => {
		if (editor) {
			editor.destroy();
		}
	});
</script>

{#if editable && editor}
	<button
		on:click={() =>
			editor.chain().focus().toggleHeading({ level: 1 }).run()}
		class:active={editor.isActive("heading", { level: 1 })}
	>
		H1
	</button>
	<button
		on:click={() =>
			editor.chain().focus().toggleHeading({ level: 2 }).run()}
		class:active={editor.isActive("heading", { level: 2 })}
	>
		H2
	</button>
	<button
		on:click={() => editor.chain().focus().setParagraph().run()}
		class:active={editor.isActive("paragraph")}
	>
		P
	</button>
{/if}

<div 
	class="tt-content w-full rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 whitespace-normal overflow-hidden {editable ? 'p-5 border' : ''}" 
	bind:this={element} 
/>

<style>
	button.active {
		background: black;
		color: white;
	}
	.tt-content {
		white-space: normal;
		overflow: hidden;
		text-overflow: ellipsis;
		word-break: break-word;
	}
</style>
