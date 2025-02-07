<script lang="ts">
    export let metrics: {
        pow_abstain: number,
        pow_against: number,
        pow_for: number,
        pow_total: number
    };

    export let tall: boolean = false;
    console.log(metrics);
    // Calculate percentages for each section
    $: forPercent = (metrics.pow_for / metrics.pow_total) * 100;
    $: abstainPercent = (metrics.pow_abstain / metrics.pow_total) * 100;
    $: againstPercent = (metrics.pow_against / metrics.pow_total) * 100;
</script>

<div class="progress-bar {tall ? 'tall' : ''} {metrics.pow_total === 0 ? 'none' : ''}">
    {#if metrics.pow_total > 0}
    <div class="for" style="width: {forPercent}%">
        <span class="percent-text">Y : {forPercent.toFixed(1)}%</span>
    </div>
    <div class="abstain" style="width: {abstainPercent}%">
        <span class="percent-text">- : {abstainPercent.toFixed(1)}%</span>
    </div>
    <div class="against" style="width: {againstPercent}%">
            <span class="percent-text">N : {againstPercent.toFixed(1)}%</span>
        </div>
    {:else}
        <div class="progress-bar flex justify-center items-center flex-col">
            <div class="text-xs text-gray-400">No votes yet</div>
        </div>
    {/if}
</div>

<style>
    .none {
        border: 1px solid rgba(255, 255, 255, 0.512);
    }

    .progress-bar {
        width: 100%;
        height: 24px;
        display: flex;
        /* border-radius: 4px; */
        overflow: hidden;
        cursor: help;
        /* padding: 3px; */
    }

    .tall {
        height: 30px;
    }

    .for, .abstain, .against {
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        color: white;
        /* min-width: 50px; */
    }

    .for {
        background-color: #4299E1; /* blue */
        height: 100%;
    }

    .abstain {
        background-color: #A0AEC0; /* grey */
        height: 100%;
    }

    .against {
        background-color: #F687B3; /* pink */
        height: 100%;
    }

    .percent-text {
        display: none;
    }

    .for:hover .percent-text,
    .abstain:hover .percent-text,
    .against:hover .percent-text {
        display: block;
    }
</style>
