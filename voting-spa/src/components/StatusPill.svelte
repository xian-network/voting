<script lang="ts">
    import { pythonDateToUnixTime } from "../lib/ts/js/utils";

    export let expires_at: string;
    export let status: string;

    const expired_unix_time = pythonDateToUnixTime(expires_at);
    const current_unix_time = Date.now();

    $: expired = expired_unix_time < current_unix_time;
    $: computed_status = getStatus(expired, status);

    function getStatus(expired: boolean, status: string) {
        if (expired && status === "active") {
            return "concluded";
        } else if (!expired && status === "active") {
            return "active";
        } else if (status !== "finalized") {
            return "finalized";
        }
    }
</script>

<div
    class="status-pill text-xs font-normalleading-tight"
    class:concluded={computed_status === "concluded"}
    class:active={computed_status === "active"}
    class:finalized={computed_status === "finalized"}
>
    {#if computed_status === "concluded"}
        <div>concluded</div>
    {:else if computed_status === "active"}
        <div>active</div>
    {:else if computed_status === "finalized"}
        <div>finalized</div>
    {/if}
</div>

<style lang="scss">
    .status-pill {
        width: 5rem;
        text-align: center;
        // border: 1px solid;
        border-radius: 0.1rem;
        padding: 0.09rem 0.5rem;
        color: #FFF;
    }

    .concluded {
        background-color: #e282ff;
    }

    .active {
        background-color: #71CBFF;
    }

    .finalized {
        background-color: #3dff91;
    }
</style>
