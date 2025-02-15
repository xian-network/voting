<script lang="ts">
    import { onMount } from "svelte";
    import { getProposal, getProposalMetrics, hasVoted } from "../lib/ts/js/api/api";
    import { updateXnsLookups } from "../lib/ts/js/xns";
    import { viewingProposal, walletInfo, xnsLookupsStore } from "../lib/ts/js/store";
    import { processProposalMetrics, pythonDateToUnixTime } from "../lib/ts/js/utils";
    import VoteButtons from "../components/VoteButtons.svelte";
    import VoteMetricsDisplay from "../components/VoteMetricsDisplay.svelte";
    
    interface RouteParams {
        id: string;
    }
    
    export let params: RouteParams;

    let p_data: any;
    let proposal: any;
    let metrics: any;
    let userVote: any = null;
    
    // Subscribe to wallet info
    let userAddress: string;
    walletInfo.subscribe(info => {
        userAddress = info.address;
        // If address changes and we have a proposal ID, check vote status
        if (userAddress && params?.id) {
            checkVoteStatus();
        }
    });

    async function checkVoteStatus() {
        try {
            const voteData = await hasVoted(params.id, userAddress);
            if (voteData && voteData.length > 0) {
                userVote = voteData[0].value;
            }
        } catch (error) {
            console.error('Error checking vote status:', error);
        }
    }

    function formatNumber(num: number): string {
        return Number(num || 0).toFixed(4).replace(/\.?0+$/, '');
    }

    // Function to format description with line breaks
    function formatDescription(description: string): string {
        // First replace escaped newlines with actual newlines
        const unescaped = description.replace(/\\n/g, '\n');
        // Then replace newlines with <br> tags for HTML display
        return unescaped.split('\n').join('<br>');
    }

    function getStatus(expires_at: string, status: string): string {
        const expired_unix_time = pythonDateToUnixTime(expires_at);
        const current_unix_time = Date.now();
        const expired = expired_unix_time < current_unix_time;

        if (expired && status === "active") {
            return "concluded";
        } else if (!expired && status === "active") {
            return "active";
        } else {
            return "finalized";
        }
    }

    function getVoteText(vote: string): string {
        switch(vote) {
            case 'y': return 'in favor';
            case 'n': return 'against';
            case '-': return 'to abstain';
            default: return '';
        }
    }

    function truncateAddress(address: string): string {
        if (!address) return "";
        if (address.length <= 12) return address;
        return `${address.slice(0, 6)}...${address.slice(-6)}`;
    }

    async function refreshProposalData() {
        const proposalRequests = [
            getProposal(params.id),
            getProposalMetrics(params.id),
        ];
        const data = await Promise.all(proposalRequests);
        p_data = Object.values(
            processProposalMetrics(data[0], data[1]),
        )[0];
        proposal = p_data.proposal;
        metrics = p_data.metrics;
        updateXnsLookups([proposal.creator])
    }

    // Modal state
    let showExternalLinkModal = false;
    let pendingExternalUrl = '';

    function handleExternalLinkClick(url: string, e: MouseEvent) {
        e.preventDefault();
        pendingExternalUrl = url;
        showExternalLinkModal = true;
    }

    function handleConfirmNavigation() {
        if (pendingExternalUrl) {
            window.open(pendingExternalUrl, '_blank', 'noopener,noreferrer');
        }
        showExternalLinkModal = false;
    }

    onMount(async () => {
        p_data = $viewingProposal;
        proposal = p_data?.proposal;
        metrics = p_data?.metrics;

        if (!p_data) {
            await refreshProposalData();
        }

        // Check initial vote status if we have an address
        if (userAddress) {
            await checkVoteStatus();
        }
    });
</script>

<div class="flex flex-col items-center min-h-screen p-5">
    {#if p_data}
        <div class="container-width w-full bg-[rgba(30,30,50,0.95)] backdrop-blur-lg p-8 rounded-2xl shadow-cyan-300/30 shadow-lg border border-cyan-500/50">
            <div class="header-row mb-6">
                <h1 class="text-3xl font-bold flex-1">{proposal.title}</h1>
                <div
                    class="status-pill {(() => {
                        const status = getStatus(proposal.expires_at, proposal.status);
                        return `status-${status}`;
                    })()}"
                >
                    {(() => {
                        const status = getStatus(proposal.expires_at, proposal.status);
                        return status;
                    })()}
                </div>
            </div>

            <div class="dates text-sm text-gray-400 mb-8">
                <div class="flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                    </svg>
                    <span>Created by: <a href={`https://explorer.xian.org/addresses/${proposal.creator}`} target="_blank" rel="noopener noreferrer" class="hover:text-cyan-400 transition-colors">{$xnsLookupsStore[proposal.creator] ? $xnsLookupsStore[proposal.creator] : truncateAddress(proposal.creator)}</a></span>
                </div>
                <div class="flex items-center gap-1 mt-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                    </svg>
                    <span>Created: {new Date(proposal.created_at).toLocaleString()}</span>
                </div>
                <div class="flex items-center gap-1 mt-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                    </svg>
                    <span>Concludes: {new Date(proposal.expires_at).toLocaleString()}</span>
                </div>
                {#if proposal.metadata?.discussion_url}
                    <div class="flex items-center gap-1 mt-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                        </svg>
                        <span>Discussion: <a 
                            href={proposal.metadata.discussion_url} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            class="text-cyan-400 hover:text-cyan-300 transition-colors break-all"
                            on:click={(e) => handleExternalLinkClick(proposal.metadata.discussion_url, e)}
                        >{proposal.metadata.discussion_url}</a></span>
                    </div>
                {/if}
            </div>

            <div class="mb-8">
                <div class="flex justify-between items-end mb-2">
                    <span class="text-lg font-bold text-gray-400">Support</span>
                </div>
                <VoteMetricsDisplay {metrics} />
            </div>

            <div class="prose prose-invert max-w-none mb-8 description-content">
                {#if proposal.description}
                    {#each proposal.description.replace(/\\n/g, '\n').split('\n') as line, i}
                        {#if line.trim()}
                            {line}
                            {#if i < proposal.description.replace(/\\n/g, '\n').split('\n').length - 1}
                                <br>
                            {/if}
                        {/if}
                    {/each}
                {/if}
            </div>

            {#if userVote}
                <div class="mb-6 p-4 bg-gray-800 rounded-lg text-center">
                    <p class="text-lg">
                        You have voted <span class="font-bold text-cyan-400">{getVoteText(userVote)}</span> on this proposal
                    </p>
                    {#if getStatus(proposal.expires_at, proposal.status) === 'active'}
                        <p class="text-sm text-gray-400 mt-2">
                            You can still change your vote if you'd like
                        </p>
                    {/if}
                </div>
            {/if}

            <div class="flex justify-center">
                <VoteButtons 
                    proposal_id={proposal.id} 
                    status={getStatus(proposal.expires_at, proposal.status)}
                    on:voted={async () => {
                        await refreshProposalData();
                        await checkVoteStatus();
                    }}
                    on:finalized={refreshProposalData}
                />
            </div>
        </div>
    {:else}
        <div class="text-center text-gray-400">Loading...</div>
    {/if}
</div>

{#if showExternalLinkModal}
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4" on:click={() => showExternalLinkModal = false}>
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/70 backdrop-blur-sm"></div>
        
        <!-- Popup -->
        <div 
            class="relative z-10 bg-[rgba(30,30,50,0.95)] p-6 rounded-lg border border-cyan-500/50 shadow-cyan-300/30 shadow-lg max-w-md w-full"
            on:click|stopPropagation
        >
            <div class="text-center">
                <svg class="mx-auto mb-4 text-cyan-400 w-12 h-12" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 class="mb-5 text-lg font-normal text-gray-200">
                    You are about to leave the DAO site and visit an external website. Are you sure you want to continue?
                </h3>
                <div class="flex justify-center gap-4">
                    <button
                        class="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors"
                        on:click={handleConfirmNavigation}
                    >
                        Yes, continue
                    </button>
                    <button
                        class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition-colors"
                        on:click={() => showExternalLinkModal = false}
                    >
                        No, go back
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}

<style lang="scss">
    :global(body) {
        background: linear-gradient(135deg, #121212, #1e1e2e);
        color: #e0e0e0;
        font-family: "Poppins", sans-serif;
    }

    .container-width {
        width: 100%;
        max-width: 800px;
        margin: 0 auto;
    }

    .header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 1rem;
    }

    .status-pill {
        flex-shrink: 0;
        padding: 6px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        text-transform: uppercase;
        min-width: 100px;
        width: auto;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .status-active {
        background-color: #71CBFF;
        color: #000;
    }

    .status-concluded {
        background-color: #e282ff;
        color: #000;
    }

    .status-finalized {
        background-color: #3dff91;
        color: #000;
    }

    .description-content {
        background: rgba(0, 0, 0, 0.2);
        padding: 1.5rem;
        border-radius: 0.5rem;
        white-space: pre-wrap;
        line-height: 1.6;
        word-wrap: break-word;
        overflow-wrap: break-word;
        hyphens: auto;
        max-width: 100%;
        overflow: hidden;
    }
</style>
