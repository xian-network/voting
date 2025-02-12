<script lang="ts">
    import { handleWalletError, handleWalletInfo } from "../lib/ts/js/wallet";
    import XianWalletUtils from "../lib/ts/js/xian-dapp-utils";
    import { GradientButton } from "flowbite-svelte";
    import { walletInfo } from "../lib/ts/js/store";
    import { proposalStatus, convertTransactionHashToBase64 } from "../lib/ts/js/utils";
    import { toasts } from "../lib/ts/js/store";
    import { createEventDispatcher } from 'svelte';
    import { VOTING_CONTRACT_NAME } from "../lib/ts/js/config";

    const dispatch = createEventDispatcher();

    export let proposal_id: string;
    export let status: string = 'active';

    let isVoting = false;
    let isFinalizing = false;

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

    async function vote(proposal_id: string, choice: string) {
        isVoting = true;
        
        try {
            const contractName = VOTING_CONTRACT_NAME;
            const methodName = "vote";
            const response = await XianWalletUtils.sendTransaction(contractName, methodName, {
                proposal_id: proposal_id,
                choice: choice,
            });

            if (response.errors) {
                throw new Error(response.errors);
            }
            console.log({response})
            toasts.add({
                type: 'success',
                title: 'Success!',
                message: 'Your vote has been recorded.',
                transactionHash: response.tx_hash
            });
            
            // Dispatch event to parent to trigger data refresh
            dispatch('voted');
        } catch (error: any) {
            toasts.add({
                type: 'error',
                title: 'Error!',
                message: error.message || 'Transaction failed'
            });
        } finally {
            isVoting = false;
        }
    }

    async function finalizeProposal() {
        isFinalizing = true;
        
        try {
            const contractName = VOTING_CONTRACT_NAME;
            const methodName = "finalize_proposal";
            const response = await XianWalletUtils.sendTransaction(contractName, methodName, {
                proposal_id: proposal_id
            });
            console.log({response})
            if (response.errors) {
                throw new Error(response.errors);
            }

            toasts.add({
                type: 'success',
                title: 'Success!',
                message: 'Proposal has been finalized.',
                transactionHash: await convertTransactionHashToBase64(response.hash)
            });

            // Dispatch event to parent to trigger data refresh
            dispatch('finalized');
        } catch (error: any) {
            toasts.add({
                type: 'error',
                title: 'Error!',
                message: error.message || 'Finalization failed'
            });
        } finally {
            isFinalizing = false;
        }
    }
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
        {#if status === 'active'}
            <div class="vote-buttons flex gap-2">
                <GradientButton
                    size="xl"
                    shadow
                    color="blue"
                    disabled={isVoting}
                    on:click={() => vote(proposal_id, "y")}>
                    {#if isVoting}Voting...{:else}Yes{/if}
                </GradientButton>
                <GradientButton
                    size="xl"
                    shadow
                    color="teal"
                    disabled={isVoting}
                    on:click={() => vote(proposal_id, "-")}>
                    {#if isVoting}Voting...{:else}Abstain{/if}
                </GradientButton>
                <GradientButton
                    size="xl"
                    shadow
                    color="pink"
                    disabled={isVoting}
                    on:click={() => vote(proposal_id, "n")}>
                    {#if isVoting}Voting...{:else}No{/if}
                </GradientButton>
            </div>
        {:else if status === 'concluded'}
            <GradientButton
                size="xl"
                shadow
                color="purple"
                disabled={isFinalizing}
                on:click={finalizeProposal}>
                {#if isFinalizing}Finalizing...{:else}Finalize Proposal{/if}
            </GradientButton>
        {:else if status === 'finalized'}
            <div class="text-gray-400 italic">Proposal has been finalized</div>
        {/if}
    {/if}
</div>
