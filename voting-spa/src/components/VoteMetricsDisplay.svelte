<script lang="ts">
    export let metrics: {
        pow_abstain: number;
        pow_against: number;
        pow_for: number;
        pow_total: number;
        total_votes: number;
    };

    function formatNumber(num: number): string {
        return Number(num || 0).toFixed(4).replace(/\.?0+$/, '');
    }
</script>

<div class="vote-metrics">
    <div class="progress-bar">
        {#if metrics}
            {@const total = metrics.pow_total || 0}
            {@const forPercent = total > 0 ? (metrics.pow_for / total) * 100 : 0}
            {@const againstPercent = total > 0 ? (metrics.pow_against / total) * 100 : 0}
            {@const abstainPercent = total > 0 ? (metrics.pow_abstain / total) * 100 : 0}

            <div class="progress-section for" style="width: {forPercent}%" />
            <div class="progress-section against" style="width: {againstPercent}%" />
            <div class="progress-section abstain" style="width: {abstainPercent}%" />
        {/if}
    </div>
    <div class="vote-legend">
        <div class="vote-type">
            <span class="legend-dot for" />
            <span>Yes: {formatNumber(metrics?.pow_for)}</span>
        </div>
        <div class="vote-type">
            <span class="legend-dot against" />
            <span>No: {formatNumber(metrics?.pow_against)}</span>
        </div>
        <div class="vote-type">
            <span class="legend-dot abstain" />
            <span>Abstain: {formatNumber(metrics?.pow_abstain)}</span>
        </div>
    </div>

    <div class="text-sm text-gray-400 text-right mt-2">
        <span>Total Votes: {metrics?.total_votes || 0}</span>
        <span class="ml-4">Total Weight: {formatNumber(metrics?.pow_total)}</span>
    </div>
</div>

<style lang="scss">
    .vote-metrics {
        margin-top: auto;
    }

    .progress-bar {
        width: 100%;
        height: 12px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        overflow: hidden;
        display: flex;
    }

    .progress-section {
        height: 100%;
        transition: width 0.3s ease;

        &.for {
            background-color: #4299E1; /* blue */
        }

        &.against {
            background-color: #F687B3; /* pink */
        }

        &.abstain {
            background-color: #A0AEC0; /* grey */
        }
    }

    .vote-legend {
        display: flex;
        justify-content: space-between;
        margin-top: 0.75rem;
        font-size: 0.9rem;
    }

    .vote-type {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;

        &.for {
            background-color: #4299E1;
        }

        &.against {
            background-color: #F687B3;
        }

        &.abstain {
            background-color: #A0AEC0;
        }
    }
</style> 