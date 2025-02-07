<script lang="ts">
  import { Button, Card, GradientButton } from "flowbite-svelte";
  import { ArrowRightOutline } from 'flowbite-svelte-icons';
  import TipTap from "./TipTap.svelte";
  import StatusPill from "./StatusPill.svelte";
  import VoteMetricsBar from "./VoteMetricsBar.svelte";
  import { truncateHtml } from "../lib/ts/js/utils";
  import { onMount } from "svelte";

  export let p_data: any;
  console.log({ p_data });

  let { proposal, metrics } = p_data;

  export let onClick: (proposal: any) => void;
</script>

<Card class="mb-5">
  <div class="flex flex-col items-start">
    <div class="text-xs flex flex-row-reverse w-full">
      {proposal.created_readable}
    </div>
    <span
      class="mb-2 text-4xl font-bold tracking-tight text-gray-900 dark:text-white"
    >
      {proposal.title}
    </span>
    <div class="flex w-full mb-2">
      <StatusPill status={proposal.status} expires_at={proposal.expires_at} />
    </div>
    <p
      class="mb-2 text-xs font-normal text-gray-700 dark:text-gray-400 leading-tight"
    >
      Concludes on {proposal.expires_readable}
    </p>
    <div class="w-full mb-2">
      <div class="w-full flex flex-row justify-between mb-2">
        <div class="text-xs flex flex-col-reverse align-bottom font-bold text-gray-700 dark:text-gray-400">
          <span>Support</span>
        </div>
        <div>
          <div class="text-xs text-gray-700 dark:text-gray-400 text-right">
            Votes: {metrics.total_votes}
          </div>
          <div class="text-xs text-gray-700 dark:text-gray-400 text-right">
            Weight: {Number(metrics.pow_total).toFixed(2).replace(/\.?0+$/, '')}
          </div>
        </div>
      </div>
      <VoteMetricsBar {metrics} />
    </div>
    <p
      class="font-normal text-sm text-gray-700 dark:text-gray-400 leading-tight text-wrap mb-3"
    >
      <TipTap
        content={truncateHtml(proposal.description, 300)}
        editable={false}
      />
    </p>
    <div class="flex flex-row justify-end w-full">
      <GradientButton color="blue" on:click={() => onClick(proposal)} size="xs">Read More <ArrowRightOutline class="w-5 h-5 ms-2" /></GradientButton>
    </div>
  </div>
</Card>
