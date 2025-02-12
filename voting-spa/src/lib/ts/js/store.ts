import { writable } from "svelte/store";

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastNotification {
    id: string;
    type: ToastType;
    message: string;
    title?: string;
    transactionHash?: string;
}

function createToastStore() {
    const { subscribe, update } = writable<ToastNotification[]>([]);

    return {
        subscribe,
        add: (notification: Omit<ToastNotification, 'id'>) => {
            const id = Math.random().toString(36).substring(2);
            update(notifications => [...notifications, { ...notification, id }]);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                update(notifications => notifications.filter(n => n.id !== id));
            }, 5000);
        },
        remove: (id: string) => {
            update(notifications => notifications.filter(n => n.id !== id));
        }
    };
}

export const toasts = createToastStore();
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
