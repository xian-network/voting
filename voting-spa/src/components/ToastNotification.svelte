<script lang="ts">
    import { Alert } from 'flowbite-svelte';
    import { toasts, type ToastNotification } from '../lib/ts/js/store';
    import { fly } from 'svelte/transition';
    import { quintOut } from 'svelte/easing';

    function getAlertColor(type: ToastNotification['type']) {
        switch (type) {
            case 'success':
                return 'green';
            case 'error':
                return 'red';
            case 'warning':
                return 'yellow';
            case 'info':
                return 'blue';
            default:
                return 'blue';
        }
    }
</script>

<div class="fixed top-4 right-4 z-50 flex flex-col gap-2 min-w-[320px] max-w-[420px]">
    {#each $toasts as toast (toast.id)}
        <div
            transition:fly={{ x: 50, duration: 300, easing: quintOut }}
            class="w-full"
        >
            <Alert
                color={getAlertColor(toast.type)}
                dismissable
                on:dismiss={() => toasts.remove(toast.id)}
            >
                <div class="flex flex-col gap-1">
                    {#if toast.title}
                        <span class="font-medium">{toast.title}</span>
                    {/if}
                    <span>{toast.message}</span>
                    {#if toast.transactionHash}
                        <a 
                            href="https://explorer.xian.org/tx/{toast.transactionHash}" 
                            target="_blank" 
                            class="text-cyan-400 hover:text-cyan-300 underline mt-1"
                        >
                            View transaction
                        </a>
                    {/if}
                </div>
            </Alert>
        </div>
    {/each}
</div>

<style>
    /* Ensure toasts are always on top */
    :global(.fixed) {
        z-index: 9999;
    }
</style> 