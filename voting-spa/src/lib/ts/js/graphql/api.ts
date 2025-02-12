import { formatDateTime } from "../utils";
import { getAllProposalsQuery, getAllProposalMetricsQuery, getProposalQuery, getProposalMetricsQuery, hasVotedQuery } from "./queries";

const endpoint = 'https://node.xian.org/graphql'

export async function fetchValues(query: string) {
    const data = JSON.stringify({
        query: query,
    });

    try {
        const response = await fetch(endpoint, {
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
