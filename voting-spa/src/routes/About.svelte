<script>
    import { fade } from 'svelte/transition';
</script>

<div class="container mx-auto px-4 py-8 max-w-4xl" in:fade>
    <h1 class="text-4xl font-bold mb-8 text-primary">About Xian Community Voting</h1>

    <div class="prose prose-lg max-w-none">
        <p class="text-xl mb-8 text-white dark:text-white/70">
            The Xian Community Voting System is a transparent and democratic platform designed to give every token holder 
            a voice in shaping the future of the ecosystem.
        </p>

        <h2 class="text-2xl font-semibold mt-8 mb-4 text-primary">Purpose</h2>
        <p class="mb-4 text-white dark:text-white/70">
            Our platform enables the community to express their sentiment on any topic, from proposing new features 
            to suggesting teams and projects for potential DAO funding. Through meaningful discussions backed by 
            token-weighted voting, we ensure that every voice is heard and every vote carries the weight of real 
            investment in the ecosystem.
        </p>

        <h2 class="text-2xl font-semibold mt-8 mb-4 text-primary">How It Works</h2>
        
        <h3 class="text-xl font-semibold mt-6 mb-3">Creating Proposals</h3>
        <p class="mb-6 text-white dark:text-white/70">
            Any token holder can create a proposal on our platform. To maintain quality and prevent spam, there's a small fee 
            of 100 Xian (this fee may be adjusted as needed). When creating a proposal, you'll provide a title, a detailed 
            description of your idea, and set an end date for the voting period. This structure ensures that each proposal 
            is well-thought-out and gives the community sufficient time to consider and vote.
        </p>

        <h3 class="text-xl font-semibold mt-6 mb-3">Voting Process</h3>
        <p class="mb-6 text-white dark:text-white/70">
            Participation in voting is open to all token holders. When casting your vote, you can choose to vote "Yes," "No," 
            or "Abstain." The weight of your vote is determined by your token balance, ensuring that those with greater 
            investment in the ecosystem have proportional influence. For maximum flexibility, you can change your vote at any 
            time before the proposal expires. All votes are recorded on-chain, maintaining complete transparency throughout 
            the process.
        </p>

        <h3 class="text-xl font-semibold mt-6 mb-3">Proposal Lifecycle</h3>
        <p class="mb-6 text-white dark:text-white/70">
            Each proposal goes through two main phases. During the active phase, token holders can freely cast and modify 
            their votes. Once the voting period ends, the proposal enters the finalized state. At this point, the system 
            calculates the final tally, taking into account both the number of votes cast and their token-weighted power. 
            This dual measurement provides a comprehensive view of both community participation and stake-weighted sentiment.
        </p>

        <h2 class="text-2xl font-semibold mt-8 mb-4 text-primary">Important Notes</h2>
        <p class="mb-6 text-white dark:text-white/70">
            It's important to understand that this is primarily a sentiment gathering system - it doesn't directly execute 
            changes or move funds. The voting power is calculated based on token holdings at the time of finalization, 
            ensuring that the final results reflect the current state of stakeholder investment. In keeping with our 
            commitment to transparency, all aspects of the voting process are publicly visible and verifiable on-chain.
        </p>
        
        <p class="mb-6 text-white dark:text-white/70">
            Proposals that receive overwhelming community support will be put forward to the validator DAO for consideration, 
            creating a pathway for community-driven initiatives to potentially become reality.
        </p>
    </div>
</div>

<style>
    :global(.dark) .text-primary {
        @apply text-primary-300;
    }
    
    .text-primary {
        @apply text-primary-600;
    }
</style> 