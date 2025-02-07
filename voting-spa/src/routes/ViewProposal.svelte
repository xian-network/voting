<script lang="ts">
    import { onMount } from "svelte";
    import TipTap from "../components/TipTap.svelte";
    import { getProposal, getProposalMetrics } from "../lib/ts/js/graphql/api";
    import { viewingProposal } from "../lib/ts/js/store";
    import { Card } from "flowbite-svelte";
    import { processProposalMetrics } from "../lib/ts/js/utils";
    import VoteMetricsBar from "../components/VoteMetricsBar.svelte";
    import VoteButtons from "../components/VoteButtons.svelte";
    export let params;

    let p_data: any;
    let proposal: any;
    let metrics: any;

    onMount(() => {
        p_data = $viewingProposal;
        proposal = p_data?.proposal;
        metrics = p_data?.metrics;

        console.log({ proposal: p_data });
        if (!p_data) {
            // retrieve the proposal data from the graphql api
            const proposalRequests = [
                getProposal(params.id),
                getProposalMetrics(params.id),
            ];
            Promise.all(proposalRequests).then((data) => {
                p_data = Object.values(
                    processProposalMetrics(data[0], data[1]),
                )[0];
                proposal = p_data.proposal;
                metrics = p_data.metrics;
            });
        }
    });
</script>

<div class="flex flex-col gap-4 w-full mt-10 justify-center items-center">
    {#if p_data}
        <div class="w-3/5">
            <h2 class="mb-7">{proposal.title}</h2>
            <div class="w-full flex flex-row justify-between mb-2">
                <div class="text-m flex flex-col-reverse align-bottom font-bold text-gray-700 dark:text-gray-400">
                  <span>Support</span>
                </div>
                <div>
                  <div class="text-m text-gray-700 dark:text-gray-400 text-right">
                    Total Votes: {metrics.total_votes}
                  </div>
                  <div class="text-m text-gray-700 dark:text-gray-400 text-right">
                    Total Weight: {metrics.pow_total}
                  </div>
                </div>
              </div>
            <div class="w-full mb-7">
                <VoteMetricsBar {metrics} tall={true} />
            </div>
            <TipTap content={proposal.description} editable={false} />
        </div>
        <div class="w-3/5">
            <VoteButtons proposal_id={proposal.id} />
        </div>
    {:else}
        <div>Loading....</div>
    {/if}
</div>
