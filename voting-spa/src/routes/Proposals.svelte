<script lang="ts">
  import { push } from "svelte-spa-router";
  import {
    getAllProposalMetrics,
    getAllProposals,
  } from "../lib/ts/js/graphql/api";
  import { processProposalMetrics } from "../lib/ts/js/utils";
  import { viewingProposal } from "../lib/ts/js/store";
  import ProposalCard from "../components/ProposalCard.svelte";

  let proposals: any[] = [];
  let metrics: any[] = [];
  let proposal_data: any[] = [];
  const proposalRequests = [getAllProposals(), getAllProposalMetrics()];

  Promise.all(proposalRequests).then((data: any) => {
    proposals = data[0];
    metrics = data[1];
    proposal_data = processProposalMetrics(proposals, metrics);
  });

  function handleClickProposal(data: any) {
    console.log({ data });
    viewingProposal.set(data);
    push(`#/view_proposal/${data.proposal.id}`);
  }
</script>

<main class="min-h-screen overflow-hidden flex flex-col">
  <!-- Animated Cloud Background -->
  <div class="absolute inset-0">
    <div class="absolute top-10 left-0 w-16 h-16 bg-white rounded-full opacity-70 cloud1" />
    <div class="absolute top-20 left-0 w-20 h-20 bg-white rounded-full opacity-70 cloud2" />
    <div class="absolute top-32 left-0 w-12 h-12 bg-white rounded-full opacity-70 cloud3" />
  </div>

  <!-- Main Content -->
  <div class="relative z-10 flex-1 flex flex-col items-center py-10">
    <header class="text-center mb-10 w-full">
      <h1 class="text-5xl font-extrabold text-white mb-4 animate-pulse">Contributor Voting System</h1>
      <p class="text-xl text-white mb-6">Decentralized voting for token holders. Create proposals and vote in real-time.</p>
    </header>

    {#if proposal_data.length === 0}
      <div class="text-white text-xl text-center">Loading...</div>
    {:else}
      <div class="w-full max-w-2xl px-4">
        {#each Object.values(proposal_data) as p_data}
          <div class="transform transition-transform hover:scale-105">
            <ProposalCard {p_data} onClick={() => handleClickProposal(p_data)} />
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>

<style lang="scss">
  :global(html), :global(body) {
    margin: 0;
    padding: 0;
    min-height: 100vh;
    background: linear-gradient(to bottom right, #9333ea, #ec4899);
    background-attachment: fixed;
  }

  @keyframes cloudAnimation {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(110vw); }
  }

  .cloud1 {
    animation: cloudAnimation 30s linear infinite;
  }

  .cloud2 {
    animation: cloudAnimation 35s linear infinite;
    animation-delay: 5s;
  }

  .cloud3 {
    animation: cloudAnimation 40s linear infinite;
    animation-delay: 10s;
  }

  :global(.animate-pulse) {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: .7;
    }
  }
</style>
