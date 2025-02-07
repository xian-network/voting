<script lang="ts">
  import Router from "svelte-spa-router";
  import { Alert } from "flowbite-svelte";
  import Landing from "./routes/Landing.svelte";
  import Proposals from "./routes/Proposals.svelte";
  import CreateProposal from "./routes/CreateProposal.svelte";
  import ViewProposal from "./routes/ViewProposal.svelte";
  import { DarkMode } from 'flowbite-svelte';

  document.documentElement.classList.add("dark");

  const routes = {
    // Exact path
    "/": Proposals,
    "/landing": Landing,
    // Using named parameters, with last being optional
    "/proposals": Proposals,

    // Wildcard parameter
    "/create-proposal": CreateProposal,
    "/view_proposal/:id": ViewProposal,
    // Catch-all
    // This is optional, but if present it must be the last
    // "*": NotFound, // TO DO: Add NotFound component
  };
</script>

<main class="flex flex-col items-center w-full">
  <div class="header flex flex-row justify-between items-center w-full">
    <div class="logo">
      x i a n d a o
    </div>
    <nav class="flex justify-center gap-4 text-center text-lg">
      <a class="hover:text-gray-400 text-gray-400" href="#/">Proposals</a>
      <a class="hover:text-gray-400 text-gray-400" href="#/create-proposal">Create Proposal</a>
      <a class="hover:text-gray-400 text-gray-400" href="#/about">About</a>
    </nav>
    <div class="flex flex-row gap-2">
      <DarkMode />
    </div>
  </div>
  <Router {routes}></Router>
</main>
<!-- 
create_proposal(title: str, description: str, expires_at: datetime.datetime
    ):

    {"__time__": [2025, 2, 5, 12, 0]} -->

<style>
  main {
    padding: 1rem;
  }
</style>
