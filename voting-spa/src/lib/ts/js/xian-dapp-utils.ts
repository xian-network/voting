const XianWalletUtils: any = {
    rpcUrl: 'https://testnet.xian.org', // Default RPC URL
    isWalletReady: false,
    initialized: false,
    state: {
        walletReady: {
            isReady: false,
            resolvers: [],
        },
        walletInfo: {
            requests: [],
        },
        signMessage: {
            requests: [],
        },
        transaction: {
            requests: [],
        },
    },

    // Initialize listeners to resolve promises and set RPC URL
    init: function (rpcUrl: string) {
        if (this.initialized) {
            console.warn('XianWalletUtils is already initialized. Avoiding re-initialization.');
            return;
        }

        if (rpcUrl) {
            this.rpcUrl = rpcUrl;
        }

        // Event listeners for wallet events
        document.addEventListener('xianWalletInfo', (event: any) => {
            // Resolve pending wallet info requests
            if (this.state.walletInfo.requests.length > 0) {
                const resolver: any = this.state.walletInfo.requests.shift();
                if (resolver) {
                    resolver(event.detail);
                }
            }
        });

        document.addEventListener('xianWalletSignMsgResponse', (event: any) => {
            // Resolve pending sign message requests
            if (this.state.signMessage.requests.length > 0) {
                const resolver: any = this.state.signMessage.requests.shift();
                if (resolver) {
                    resolver(event.detail);
                }
            }
        });

        document.addEventListener('xianWalletTxStatus', (event: any) => {
            // Resolve pending transaction status requests
            if (this.state.transaction.requests.length > 0) {
                const resolver: any = this.state.transaction.requests.shift();
                if ('errors' in event.detail) {
                    resolver(event.detail);
                } else {
                    this.getTxResultsAsyncBackoff(event.detail.txid).then((tx: any) => {
                        let data = tx.result.tx_result.data;
                        let original_tx = tx.result.tx;
                        let decodedData = window.atob(data);
                        let decodedOriginalTx = window.atob(original_tx);
                        let parsedData = JSON.parse(decodedData);
                        parsedData.tx_hash = event.detail.txid;
                        parsedData.original_tx = JSON.parse(this.hexToString(decodedOriginalTx));
                        resolver(parsedData);
                    }).catch((error: any) => {
                        console.error('Final error after retries:', error);
                        resolver(null);
                    });
                }
            }
        });

        document.addEventListener('xianReady', () => {
            this.isWalletReady = true;
            // Resolve all pending wallet ready requests
            while (this.state.walletReady.resolvers.length > 0) {
                const resolver: any = this.state.walletReady.resolvers.shift();
                if (resolver) {
                    resolver();
                }
            }
            console.log('Xian Wallet is ready');
        });

        this.initialized = true; // Mark as initialized
    },

    waitForWalletReady: function () {
        return new Promise((resolve: any) => {
            if (this.isWalletReady) {
                resolve();
            } else {
                this.state.walletReady.resolvers.push(resolve);
                setTimeout(() => {
                    if (!this.isWalletReady) {
                        const index = this.state.walletReady.resolvers.indexOf(resolve);
                        if (index !== -1) {
                            this.state.walletReady.resolvers.splice(index, 1);
                            resolve(); // Resolve anyway to not block the flow
                        }
                    }
                }, 100); // 2 seconds timeout
            }
        });
    },

    requestWalletInfo: async function () {
        await this.waitForWalletReady();
        return new Promise((resolve, reject) => {
            this.state.walletInfo.requests.push(resolve);

            const timeoutId = setTimeout(() => {
                const index = this.state.walletInfo.requests.indexOf(resolve);
                if (index !== -1) {
                    this.state.walletInfo.requests.splice(index, 1);
                    reject(new Error('Xian Wallet Chrome extension not installed or not responding'));
                }
            }, 100); // 2 seconds timeout

            document.dispatchEvent(new CustomEvent('xianWalletGetInfo'));
        });
    },

    signMessage: async function (message: any) {
        await this.waitForWalletReady();
        return new Promise((resolve: any, reject: any) => {
            this.state.signMessage.requests.push(resolve);

            const timeoutId = setTimeout(() => {
                const index = this.state.signMessage.requests.indexOf(resolve);
                if (index !== -1) {
                    this.state.signMessage.requests.splice(index, 1);
                    reject(new Error('Xian Wallet Chrome extension not responding'));
                }
            }, 30000); // 30 seconds timeout, this requires manual confirmation

            document.dispatchEvent(new CustomEvent('xianWalletSignMsg', {
                detail: {
                    message: message
                }
            }));
        });
    },

    sendTransaction: async function (contract: any, method: any, kwargs: any) {
        await this.waitForWalletReady();
        return new Promise((resolve, reject) => {
            this.state.transaction.requests.push(resolve);

            const timeoutId = setTimeout(() => {
                const index = this.state.transaction.requests.indexOf(resolve);
                if (index !== -1) {
                    this.state.transaction.requests.splice(index, 1);
                    reject(new Error('Xian Wallet Chrome extension not responding'));
                }
            }, 30000); // 30 seconds timeout, this requires manual confirmation

            document.dispatchEvent(new CustomEvent('xianWalletSendTx', {
                detail: {
                    contract: contract,
                    method: method,
                    kwargs: kwargs
                }
            }));
        });
    },

    getTxResults: async function (txHash: string) {
        try {
            const response = await fetch(`${this.rpcUrl}/tx?hash=0x${txHash}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json();
            console.log({txHash})
            data.tx_hash = txHash;
            return data;
        } catch (error) {
            console.log('Transaction not found yet');
            throw error; // Rethrow the error to trigger retries
        }
    },

    getBalanceRequest: async function (address: string, contract: string) {
        const response = await fetch(`${this.rpcUrl}/abci_query?path=%22/get/${contract}.balances:${address}%22`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        let balance = data.result.response.value;
        if (balance === 'AA==') {
            return 0;
        }
        let decodedBalance = window.atob(balance);
        return decodedBalance;
    },

    getBalance: async function (contract: string) {
        const info = await this.requestWalletInfo();
        const address = info.address;
        const balance = await this.getBalanceRequest(address, contract);
        return balance;
    },

    getApprovedBalanceRequest: async function (token_contract: string, address: string, approved_to: string) {
        const response = await fetch(`${this.rpcUrl}/abci_query?path=%22/get/${token_contract}.balances:${address}:${approved_to}%22`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        let balance = data.result.response.value;
        if (balance === 'AA==') {
            return 0;
        }
        let decodedBalance = window.atob(balance);
        return decodedBalance;
    },

    getApprovedBalance: async function (token_contract: string, approved_to: string) {
        const info = await this.requestWalletInfo();
        const address = info.address;
        const balance = await this.getApprovedBalanceRequest(token_contract, address, approved_to);
        return balance;
    },

    getTxResultsAsyncBackoff: async function (txHash: string, retries = 5, delay = 1000) {
        try {
            return await this.getTxResults(txHash);
        } catch (error) {
            if (retries === 0) {
                throw error;
            }
            await new Promise(resolve => setTimeout(resolve, delay));
            return await this.getTxResultsAsyncBackoff(txHash, retries - 1, delay * 2);
        }
    },

    hexToString: function (hex: string) {
        let bytes = [];
        for (let i = 0; i < hex.length; i += 2) {
            bytes.push(parseInt(hex.substr(i, 2), 16));
        }
        return String.fromCharCode.apply(String, bytes);
    },
};
export default XianWalletUtils;
