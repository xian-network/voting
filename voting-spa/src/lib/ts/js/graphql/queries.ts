export const getAllProposalsQuery = (offset = 0, take = 10) => {
  return `
    query GetProposals {
        allStates(
          filter: {
            key: { startsWith: "con_vote_test_4.proposals"}
          }
          orderBy: UPDATED_DESC
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
            key: { startsWith: "con_vote_test_4.proposals:${id}"}
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
            key: { startsWith: "con_vote_test_4.proposal_metrics"}
          }
          orderBy: UPDATED_DESC
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
      allStates(filter: {key: {startsWith: "con_vote_test_4.proposal_metrics:${id}"}}) {
        nodes {
          key
          value
        }
      }
    }
  `;
};