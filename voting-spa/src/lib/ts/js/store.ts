import { writable } from "svelte/store";

export const walletAddressElementValue = writable("Connect Wallet");
export const walletInfo = writable<I_WalletInfo>({
    initialized: false,
    address: '',
    chain_id: '',
    installed: false,
    locked: false
});
export const viewingProposal = writable<any>();


interface I_WalletInfo {
    initialized: boolean;
    address: string;
    chain_id: string;
    installed: boolean;
    locked?: boolean;
}
