<script lang="ts">
    import { handleWalletError, handleWalletInfo } from "../lib/ts/js/wallet";
    import XianWalletUtils from "../lib/ts/js/xian-dapp-utils";
    import { Button, GradientButton } from "flowbite-svelte";
    import { walletInfo } from "../lib/ts/js/store";
    import { proposalStatus } from "../lib/ts/js/utils";

    export let proposal_id: string;

    async function connectWallet() {
        XianWalletUtils.init("https://node.xian.org");
        const info =
            await XianWalletUtils.requestWalletInfo().catch(handleWalletError);
        handleWalletInfo(info);
        // isConnected = true;
    }

    function installWallet() {
        window.open(
            "https://chromewebstore.google.com/detail/xian-wallet/kcimjjhplbcgkcnanijkolfillgfanlc",
            "_blank",
        );
    }

    function unlockWallet() {
        // walletInfo.set({
        //     initialized: true,
        //     address: '',
        //     chain_id: '',
        //     installed: false,
        //     locked: false
        // });
    }

    async function vote(proposal_id: string, choice: string) {
        const contractName = "con_vote_test_4";
        const methodName = "vote";
        XianWalletUtils.sendTransaction(contractName, methodName, {
            proposal_id: proposal_id,
            choice: choice,
        });
    }
</script>

<div class="flex justify-end gap-2">
    {#if !$walletInfo.initialized}
        <GradientButton color="blue" on:click={connectWallet}
            >Connect Xian Wallet To Vote</GradientButton
        >
    {:else if !$walletInfo.installed}
        <GradientButton color="green" on:click={installWallet}
            >Install Wallet</GradientButton
        >
    {:else if $walletInfo.locked}
        <GradientButton color="purple" on:click={unlockWallet}
            >Unlock Wallet</GradientButton
        >
    {:else}
        <div class="vote-buttons">
            <GradientButton
                shadow
                color="blue"
                on:click={() => vote(proposal_id, "y")}>Yes</GradientButton
            >
            <GradientButton
                shadow
                color="teal"
                on:click={() => vote(proposal_id, "-")}>Abstain</GradientButton
            >
            <GradientButton
                shadow
                color="pink"
                on:click={() => vote(proposal_id, "n")}>No</GradientButton
            >
        </div>
    {/if}
</div>
