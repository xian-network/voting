import { formatDateTime } from "../utils";
import { getAllProposalsQuery, getAllProposalMetricsQuery, getProposalQuery, getProposalMetricsQuery, hasVotedQuery } from "./queries";
import { TransactionBuilder, type I_NetworkSettings, type I_TxInfo } from "xian-js"

const graphql_endpoint = 'https://node.xian.org/graphql'

export async function fetchValues(query: string) {
    const data = JSON.stringify({
        query: query,
    });

    try {
        const response = await fetch(graphql_endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length.toString(),
            },
            body: data,
        });
        const responseData = await response.json();
        const nodes = responseData.data.allStates.nodes;
        return nodes;
    } catch (error) {
        console.error('Error with request:', error);
    }
}

export function formatProposal(nodes: any) {
    return nodes.map((node: any) => {
        const key = node.key.split(":")[1];
        return {
            id: key,
            expires_readable: formatDateTime(node.value.expires_at),
            created_readable: formatDateTime(node.value.created_at),
            ...node.value
        }
    })
}

export async function getAllProposals() {
    const query = getAllProposalsQuery();
    const response = await fetchValues(query);
    return formatProposal(response);
}

export async function getProposal(id: string) {
    const query = getProposalQuery(id);
    const response = await fetchValues(query);
    return formatProposal(response);
}

export async function getAllProposalMetrics() {
    const query = getAllProposalMetricsQuery();
    const response = await fetchValues(query);
    console.log(response);
    return response;
}

export async function getProposalMetrics(id: string) {
    const query = getProposalMetricsQuery(id);
    const response = await fetchValues(query);
    console.log(response);
    return response;
}

export async function hasVoted(id: string, address: string) {
    const query = hasVotedQuery(id, address);
    const response = await fetchValues(query);
    console.log(response);
    return response;
}

export async function requestXnsLookup(addresses: string[]) {
    let networkInfo: I_NetworkSettings = {
        chain_id: "xian-network-3",
        masternode_hosts: ["https://node.xian.org"]
    };

    const txInfo: I_TxInfo = {
        contractName: "con_xns_multilookup",
        methodName: "multicall",
        kwargs: {
            addresses
        },
        chain_id: "xian-network-3",
        senderVk: "abc123"
    }

    let tx = new TransactionBuilder(networkInfo, txInfo)
    const res = await tx.simulate_txn()
    console.log(res)
    return res
}