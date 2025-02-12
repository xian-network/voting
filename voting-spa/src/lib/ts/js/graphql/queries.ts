import { VOTING_CONTRACT_NAME } from "../config";

export const getAllProposalsQuery = (offset = 0, take = 10) => {
  return `
    query GetProposals {
        allStates(
          filter: {
            key: { startsWith: "${VOTING_CONTRACT_NAME}.proposals"}
          }
          orderBy: NATURAL
        ) {
          nodes {
            key
            value
          }
        }
      }
    `;
};


export const getProposalQuery = (id: string) => {
  return `
    query GetProposals {
        allStates(
          filter: {
            key: { startsWith: "${VOTING_CONTRACT_NAME}.proposals:${id}"}
          }
        ) {
          nodes {
            key
            value
          }
        }
      }
    `;
};

export const getAllProposalMetricsQuery = (offset = 0, take = 10) => {
  return `
    query GetProposals {
        allStates(
          filter: {
            key: { startsWith: "${VOTING_CONTRACT_NAME}.proposal_metrics"}
          }
          orderBy: NATURAL
        ) {
          nodes {
            key
            value
          }
        }
      }
    `;
};

export const getProposalMetricsQuery = (id: string) => {
  return `
    query GetProposalMetrics {
      allStates(filter: {key: {startsWith: "${VOTING_CONTRACT_NAME}.proposal_metrics:${id}"}}) {
        nodes {
          key
          value
        }
      }
    }
  `;
};

export const hasVotedQuery = (id: string, address: string) => {
  return `
    query HasVoted {
      allStates(filter: {key: {startsWith: "${VOTING_CONTRACT_NAME}.proposal_votes:${id}:${address}"}}) {
        nodes {
          key
          value
        }
      }
    }
  `;
};

export const GET_ALL_PROPOSALS = `
query GetAllProposals {
  allStates(filter: {
    key: { startsWith: "${VOTING_CONTRACT_NAME}.proposals"}
  }) {
    edges {
      node {
        key
        value
      }
    }
  }
}
`;

export const GET_PROPOSAL = (id: string) => `
query GetProposal {
  allStates(filter: {
    key: { startsWith: "${VOTING_CONTRACT_NAME}.proposals:${id}"}
  }) {
    edges {
      node {
        key
        value
      }
    }
  }
}
`;

export const GET_ALL_PROPOSAL_METRICS = `
query GetAllProposalMetrics {
  allStates(filter: {
    key: { startsWith: "${VOTING_CONTRACT_NAME}.proposal_metrics"}
  }) {
    edges {
      node {
        key
        value
      }
    }
  }
}
`;

export const GET_PROPOSAL_METRICS = (id: string) => `
query GetProposalMetrics {
  allStates(filter: {key: {startsWith: "${VOTING_CONTRACT_NAME}.proposal_metrics:${id}"}}) {
    edges {
      node {
        key
        value
      }
    }
  }
}
`;

export const GET_PROPOSAL_VOTE = (id: string, address: string) => `
query GetProposalVote {
  allStates(filter: {key: {startsWith: "${VOTING_CONTRACT_NAME}.proposal_votes:${id}:${address}"}}) {
    edges {
      node {
        key
        value
      }
    }
  }
}
`;
