<script lang="ts">
  import Router from "svelte-spa-router";
  import {
    Alert,
    Footer,
    FooterCopyright,
    FooterLinkGroup,
    FooterLink,
  } from "flowbite-svelte";
  import Landing from "./routes/Landing.svelte";
  import ProposalsAlt from "./routes/ProposalsAlt.svelte";
  import CreateProposal from "./routes/CreateProposalAlt.svelte";
  import ViewProposal from "./routes/ViewProposal.svelte";
  import About from "./routes/About.svelte";
  import ToastNotification from "./components/ToastNotification.svelte";
  import SocialIcons from "./components/SocialIcons.svelte";
  import { location } from "svelte-spa-router";
  import { slide } from 'svelte/transition';

  document.documentElement.classList.add("dark");

  $: showNav = $location !== "/" && $location !== "/landing";

  const routes = {
    // Exact path
    "/": Landing,
    "/landing": Landing,
    // Using named parameters, with last being optional
    "/proposals": ProposalsAlt,

    // Wildcard parameter
    "/create-proposal": CreateProposal,
    "/view_proposal/:id": ViewProposal,
    "/about": About,
    // Catch-all
    // This is optional, but if present it must be the last
    // "*": NotFound, // TO DO: Add NotFound component
  };

  let menuOpen = false;

  // Toggle body class when menu opens/closes
  $: if (typeof document !== 'undefined') {
    if (menuOpen) {
      document.body.classList.add('menu-open');
    } else {
      document.body.classList.remove('menu-open');
    }
  }
</script>

<main class="flex flex-col items-center w-full min-h-screen">
  <ToastNotification />
  {#if showNav}
    <header class="w-full border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6">
        <div class="h-16 flex items-center justify-between">
          <a href="#/" class="font-mono text-xl">xiandao:~$</a>
          
          <!-- Burger menu button for mobile -->
          <button 
            class="md:hidden p-2"
            on:click={() => menuOpen = !menuOpen}
            aria-label="Toggle menu"
          >
            <svg 
              class="w-6 h-6" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              {#if !menuOpen}
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M4 6h16M4 12h16M4 18h16"
                />
              {:else}
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M6 18L18 6M6 6l12 12"
                />
              {/if}
            </svg>
          </button>

          <!-- Desktop navigation -->
          <nav class="hidden md:flex items-center">
            <a
              class="px-5 h-16 flex items-center border-transparent hover:border-gray-700 border-b-2 -mb-[2px] transition-colors"
              href="#/proposals">proposals</a
            >
            <a
              class="px-5 h-16 flex items-center border-transparent hover:border-gray-700 border-b-2 -mb-[2px] transition-colors"
              href="#/about">about</a
            >
            <div class="pl-4 flex items-center space-x-4">
              <a
                class="px-4 py-2 rounded-lg font-semibold text-sm transition-all bg-[rgba(255,255,255,0.1)] border border-[rgba(78,205,196,0.4)] backdrop-blur-sm hover:bg-[rgba(78,205,196,0.15)] hover:border-[rgba(78,205,196,0.6)] hover:transform hover:-translate-y-0.5"
                href="#/create-proposal">+ create</a
              >
              <div class="pl-2">
                <SocialIcons iconSize="sm" iconColor="text-gray-300" spacing="space-x-3" />
              </div>
            </div>
          </nav>
        </div>

        <!-- Mobile navigation -->
        {#if menuOpen}
          <nav 
            class="fixed inset-0 z-50 md:hidden bg-gray-900/95 backdrop-blur-sm"
            transition:slide={{ duration: 200 }}
          >
            <!-- Close button -->
            <button
              class="absolute top-4 right-6"
              on:click={() => menuOpen = false}
              aria-label="Close menu"
            >
              <svg 
                class="w-6 h-6" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>

            <div class="h-[calc(100vh-4rem)] mt-16 px-6 py-8 flex flex-col justify-between">
              <!-- Navigation links -->
              <div class="flex flex-col space-y-4">
                <a
                  class="px-4 py-3 text-lg rounded-lg hover:bg-gray-800/50 transition-colors"
                  href="#/proposals"
                  on:click={() => menuOpen = false}
                >proposals</a>
                <a
                  class="px-4 py-3 text-lg rounded-lg hover:bg-gray-800/50 transition-colors"
                  href="#/about"
                  on:click={() => menuOpen = false}
                >about</a>
                <a
                  class="px-4 py-3 text-lg rounded-lg font-semibold transition-all bg-[rgba(255,255,255,0.1)] border border-[rgba(78,205,196,0.4)] backdrop-blur-sm hover:bg-[rgba(78,205,196,0.15)] hover:border-[rgba(78,205,196,0.6)]"
                  href="#/create-proposal"
                  on:click={() => menuOpen = false}
                >+ create</a>
              </div>

              <!-- Social links -->
              <div class="border-t border-gray-800 pt-8 flex justify-center">
                <SocialIcons iconColor="text-gray-300" />
              </div>
            </div>
          </nav>
        {/if}
      </div>
    </header>
  {/if}
  <div class="w-full max-w-7xl px-0 py-0 sm:px-6 sm:py-8 flex-grow">
    <Router {routes} />
  </div>
  {#if showNav}
    <Footer class="w-full border-t border-gray-800">
      <div class="w-full max-w-7xl mx-auto px-6 py-6">
        <div class="flex items-center justify-between">
          <FooterCopyright href="#/" by="XianDAO" />
          <SocialIcons iconColor="text-gray-300" />
        </div>
      </div>
    </Footer>
  {/if}
</main>

<style lang="scss">
  @media (max-width: 480px) {
    :global(#app) {
      padding: 0;
    }
  }

  /* Prevent scrolling when mobile menu is open */
  :global(body.menu-open) {
    overflow: hidden;
    position: fixed;
    width: 100%;
  }

  nav {
    transition: all 0.2s ease-in-out;
  }

  /* Mobile menu animation styles */
  :global(.mobile-menu-enter),
  :global(.mobile-menu-leave-to) {
    opacity: 0;
    transform: translateY(-1rem);
  }

  :global(.mobile-menu-enter-active),
  :global(.mobile-menu-leave-active) {
    transition: opacity 0.2s ease, transform 0.2s ease;
  }
</style>
