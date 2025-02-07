<script>
    import { handleWalletError, handleWalletInfo } from "../lib/ts/js/wallet";
    import XianWalletUtils from "../lib/ts/js/xian-dapp-utils";
    import { Button, GradientButton } from "flowbite-svelte";
    import { walletInfo } from "../lib/ts/js/store";

    export let kwargs;
    export let handleSubmitProposalClick

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

    async function submitProposal() {
        const contractName = "con_vote_test_4";
        const methodName = "create_proposal";
        XianWalletUtils.sendTransaction(
            contractName,
            methodName,
            kwargs,
        );
        localStorage.setItem("proposalTitle", '');
        localStorage.setItem("proposalContent", '');
        console.log("Proposal submitted");
    }
</script>

<div class="flex justify-end gap-2">
    {#if !$walletInfo.initialized}
        <GradientButton color="blue" on:click={connectWallet}>Connect Xian Wallet</GradientButton>
    {:else if !$walletInfo.installed}
        <GradientButton color="green" on:click={installWallet}>Install Wallet</GradientButton>
    {:else if $walletInfo.locked}
        <GradientButton color="purple" on:click={unlockWallet}>Unlock Wallet</GradientButton>
    {:else}
        <GradientButton color="pink" on:click={submitProposal}>Submit Proposal</GradientButton>
    {/if}
</div>
