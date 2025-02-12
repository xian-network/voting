<script lang="ts">
    import { handleWalletError, handleWalletInfo } from "../lib/ts/js/wallet";
    import XianWalletUtils from "../lib/ts/js/xian-dapp-utils";
    import { GradientButton, Spinner } from "flowbite-svelte";
    import { walletInfo, toasts } from "../lib/ts/js/store";
    import { convertTransactionHashToBase64 } from "../lib/ts/js/utils";
    import { replace } from "svelte-spa-router";
    import { VOTING_CONTRACT_NAME } from "../lib/ts/js/config";

    interface ProposalArgs {
        title: string;
        description: string;
        expires_at: string;
    }

    export let kwargs: ProposalArgs;
    export let handleSubmitProposalClick: () => void;
    export let isValid = false;

    let isSubmitting = false;

    async function connectWallet() {
        XianWalletUtils.init("https://node.xian.org");
        const info =
            await XianWalletUtils.requestWalletInfo().catch(handleWalletError);
        handleWalletInfo(info);
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
        if (!isValid) return;

        isSubmitting = true;

        try {
            const contractName = VOTING_CONTRACT_NAME;
            const methodName = "create_proposal";
            const response = await XianWalletUtils.sendTransaction(
                contractName,
                methodName,
                kwargs,
            );

            if (response.errors) {
                throw new Error(response.errors);
            }

            localStorage.setItem("proposalTitle", "");
            localStorage.setItem("proposalContent", "");
            console.log({ response });
            toasts.add({
                type: "success",
                title: "Success!",
                message: "Your proposal has been submitted successfully.",
                transactionHash: response.tx_hash,
            });
            console.log({ response });
            replace(`/view_proposal/${response.result}`);
        } catch (error: unknown) {
            const errorMessage =
                error instanceof Error
                    ? error.message
                    : "Unknown error occurred";
            toasts.add({
                type: "error",
                title: "Error",
                message: `Failed to submit proposal: ${errorMessage}`,
            });
        } finally {
            isSubmitting = false;
        }
    }

    $: buttonClasses = !isValid ? "opacity-50 cursor-not-allowed" : "";
</script>

<div class="flex justify-end gap-2">
    {#if !$walletInfo.initialized}
        <GradientButton size="xl" color="blue" on:click={connectWallet}
            >Connect Xian Wallet</GradientButton
        >
    {:else if !$walletInfo.installed}
        <GradientButton size="xl" color="green" on:click={installWallet}
            >Install Wallet</GradientButton
        >
    {:else if $walletInfo.locked}
        <GradientButton size="xl" color="purple" on:click={unlockWallet}
            >Unlock Wallet</GradientButton
        >
    {:else}
        <GradientButton
            size="xl"
            color="pink"
            on:click={submitProposal}
            disabled={!isValid || isSubmitting}
            class={buttonClasses}
        >
            {#if isSubmitting}
                <div class="flex items-center gap-3">
                    <Spinner size="4" color="white" />
                    <span>Submitting...</span>
                </div>
            {:else}
                Submit Proposal
            {/if}
        </GradientButton>
    {/if}
</div>

<style>
    /* Add any custom styles here */
</style>
