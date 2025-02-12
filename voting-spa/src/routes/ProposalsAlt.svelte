<script lang="ts">
  import { push } from "svelte-spa-router";
  import {
    getAllProposalMetrics,
    getAllProposals,
  } from "../lib/ts/js/graphql/api";
  import {
    processProposalMetrics,
    pythonDateToUnixTime,
  } from "../lib/ts/js/utils";
  import { viewingProposal } from "../lib/ts/js/store";
  import VoteMetricsDisplay from "../components/VoteMetricsDisplay.svelte";

  function formatNumber(num: number): string {
    return Number(num || 0)
      .toFixed(4)
      .replace(/\.?0+$/, "");
  }

  function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;

    // Find the last space before maxLength
    const lastSpace = text.lastIndexOf(" ", maxLength);

    // If no space found, truncate at maxLength
    if (lastSpace === -1) return text.slice(0, maxLength) + "...";

    // Truncate at the last space
    return text.slice(0, lastSpace) + "...";
  }

  function truncateAfterSentence(
    text: string,
    maxLength: number = 200,
  ): string {
    // First apply hard character limit
    if (text.length > maxLength) {
      return text.slice(0, maxLength) + "...";
    }

    // Find all sentence endings up to maxLength
    const regex = /[.!?]+/g;
    const matches = [...text.slice(0, maxLength + 30).matchAll(regex)];

    if (matches.length === 0) {
      // If no sentence endings found, truncate at maxLength
      return text.slice(0, maxLength) + "...";
    }

    // Find the last sentence ending that's closest to but not exceeding maxLength
    let lastMatch = matches[0];
    for (const match of matches) {
      if (match.index! > maxLength) break;
      lastMatch = match;
    }

    return text.slice(0, lastMatch.index! + 1) + "...";
  }

  function truncateAfterLines(text: string, maxLines: number = 5): string {
    // First replace escaped newlines with actual newlines
    const unescaped = text.replace(/\\n/g, "\n");

    // Split into lines
    const lines = unescaped.split("\n");

    // If we have more lines than the max, truncate
    if (lines.length > maxLines) {
      // Join the first maxLines lines and add ellipsis
      return lines.slice(0, maxLines).join("\n") + "\n...";
    }

    return unescaped;
  }

  // Function to format description with line breaks
  function formatDescription(description: string): string {
    // Strip any HTML tags that might be in the input
    return description
      .replace(/<[^>]*>/g, "") // Remove any HTML tags
      .replace(/&[^;]+;/g, "") // Remove HTML entities
      .trim(); // Remove any leading/trailing whitespace
  }

  function getStatus(expires_at: string, status: string): string {
    const expired_unix_time = pythonDateToUnixTime(expires_at);
    const current_unix_time = Date.now();
    const expired = expired_unix_time < current_unix_time;

    if (expired && status === "active") {
      return "concluded";
    } else if (!expired && status === "active") {
      return "active";
    } else {
      return "finalized";
    }
  }

  function truncateAddress(address: string): string {
    if (!address) return "";
    if (address.length <= 12) return address;
    return `${address.slice(0, 6)}...${address.slice(-6)}`;
  }

  let proposals: any[] = [];
  let metrics: any[] = [];
  let proposal_data: any[] = [];
  const proposalRequests = [getAllProposals(), getAllProposalMetrics()];

  Promise.all(proposalRequests).then((data: any) => {
    proposals = data[0];
    metrics = data[1];
    proposal_data = Object.values(processProposalMetrics(proposals, metrics))
      .sort((a, b) => new Date(b.proposal.created_at).getTime() - new Date(a.proposal.created_at).getTime());
  });

  function handleClickProposal(data: any) {
    viewingProposal.set(data);
    push(`#/view_proposal/${data.proposal.id}`);
  }
</script>

<main class="flex flex-col min-h-screen p-5 pt-8">
  <div class="text-center mb-12">
    <h1 class="text-5xl font-extralight">holder proposals</h1>
    <p class="text-lg mt-2">crowdsourced sentiment powered by $xian</p>
  </div>

  {#if proposal_data.length === 0}
    <div class="flex justify-center items-center flex-grow">Loading...</div>
  {:else}
    <div class="w-full max-w-7xl grid grid-cols-1 sm:grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mx-auto px-4">
      {#each Object.values(proposal_data) as p_data, i}
        <button
          type="button"
          class="card"
          style="animation-delay: {i * 60}ms"
          on:click={() => handleClickProposal(p_data)}
          on:keydown={(e) => e.key === "Enter" && handleClickProposal(p_data)}
        >
          <div class="card-content">
            <div class="content-wrapper">
              <div class="header-row">
                <h2 class="text-xl font-bold card-title mb-4">
                  {truncateText(p_data.proposal.title, 50)}
                </h2>
                <div
                  class="status-pill {(() => {
                    const status = getStatus(
                      p_data.proposal.expires_at,
                      p_data.proposal.status,
                    );
                    return `status-${status}`;
                  })()}"
                >
                  {(() => {
                    const status = getStatus(
                      p_data.proposal.expires_at,
                      p_data.proposal.status,
                    );
                    return status;
                  })()}
                </div>
              </div>
              <p class="mt-2 description">
                {#if p_data.proposal.description}
                  {@const formattedText = formatDescription(
                    truncateAfterLines(
                      truncateAfterSentence(p_data.proposal.description),
                    ),
                  )}
                  <p>
                    {#each formattedText.split("\n") as line, i}
                      {#if line.trim()}
                        {line}
                        {#if i < formattedText.split("\n").length - 1}
                          <br />
                        {/if}
                      {/if}
                    {/each}
                  </p>
                {/if}
              </p>
            </div>

            <div class="vote-metrics mb-6">
              <VoteMetricsDisplay metrics={p_data.metrics} />
            </div>

            <div class="dates text-sm text-gray-400">
              <div class="flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                  />
                </svg>
                <span
                  >Created by:
                  <a
                    href={`https://explorer.xian.org/addresses/${p_data.proposal.creator}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="hover:text-cyan-400 transition-colors"
                    on:click|stopPropagation
                  >
                    {truncateAddress(p_data.proposal.creator)}
                  </a>
                </span>
              </div>
              <div class="flex items-center gap-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span
                  >Created: {new Date(
                    p_data.proposal.created_at,
                  ).toLocaleString()}</span
                >
              </div>
              <div class="flex items-center gap-1 mt-1">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                    clip-rule="evenodd"
                  />
                </svg>
                <span
                  >Concludes: {new Date(
                    p_data.proposal.expires_at,
                  ).toLocaleString()}</span
                >
              </div>
            </div>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</main>

<style lang="scss">
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  :global(body) {
    background: linear-gradient(135deg, #121212, #1e1e2e);
    color: #e0e0e0;
    font-family: "Poppins", sans-serif;
    text-shadow: 1px 1px 10px rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
  }

  .card {
    background: rgba(30, 30, 50, 0.95);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease;
    border: 1px solid rgba(100, 100, 255, 0.2);
    position: relative;
    cursor: pointer;
    width: 100%;
    text-align: left;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
    will-change: transform, opacity;
    
    /* Initial animation state */
    opacity: 0;
    animation: fadeInUp 0.6s ease forwards;

    &:hover,
    &:focus {
      transform: translateY(-4px);
      border-color: rgba(255, 0, 255, 0.4);
      outline: none;
    }

    &:focus-visible {
      outline: 2px solid rgba(255, 0, 255, 0.8);
      outline-offset: 2px;
    }
  }

  .card-content {
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 200px;
    gap: 1.5rem;
  }

  .content-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
  }

  .card-title {
    word-wrap: break-word;
    flex: 1;
    min-width: 0;
  }

  .description {
    white-space: pre-wrap;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
    max-width: 100%;
    margin-bottom: 1rem;
    p {
      word-wrap: break-word;
      overflow-wrap: break-word;
      hyphens: auto;
    }
  }

  .status-pill {
    flex-shrink: 0;
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
    text-transform: uppercase;
    min-width: 100px;
    width: auto;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .status-active {
    background-color: #71cbff;
    color: #000;
  }

  .status-concluded {
    background-color: #e282ff;
    color: #000;
  }

  .status-finalized {
    background-color: #3dff91;
    color: #000;
  }

  .dates {
    padding-top: 0.5rem;
  }
</style>
