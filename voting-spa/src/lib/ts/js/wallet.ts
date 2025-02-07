import { walletAddressElementValue, walletInfo } from "./store";
// import { updateCurrentCounter } from "./node";

export const handleWalletInfo = (info: any) => {
    walletAddressElementValue.set(info.address.slice(0, 10) + '...');
    if (info.locked) {
        walletInfo.set({
            initialized: true,
            installed: true,
            address: info.address,
            chain_id: info.chain_id,
            locked: true
        });
        walletAddressElementValue.set('Wallet is Locked');
        console.log("Your wallet is locked. Please unlock it to interact with the dapp.");
    } else {
        walletInfo.set({
            initialized: true,
            installed: true,
            address: info.address,
            chain_id: info.chain_id,
            locked: false
        });
    }
}

export const handleWalletError = (error: any) => {
    console.log("You don't have the Xian Wallet extension installed. Please install it to interact with the dapp.");
    walletAddressElementValue.set('Wallet not installed');
    walletInfo.set({
        initialized: true,
        installed: false,
        address: '',
        chain_id: '',
        locked: false
    });
}

export const handleTransaction = (response: any) => {
    if (response.errors) {
        console.error('Transaction failed:', response.errors);
        console.log("Transaction failed: " + response.errors);
        return;
    }
    console.log('Transaction succeeded:', response);
    console.log("Transaction succeeded");
    // updateCurrentCounter();
}

export const handleTransactionError = (error: any) => {
    console.error('Transaction error:', error);
    console.log("Transaction error: " + error);
}