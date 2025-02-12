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
  import { location } from "svelte-spa-router";

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

  // Add social media links
  const socialLinks = [
    { href: "https://t.me/xian_network", icon: "telegram", label: "Telegram" },
    { href: "https://discord.gg/AcjdvgHnaT", icon: "discord", label: "Discord" },
    { href: "https://xiannetwork.medium.com/", icon: "medium", label: "Medium" },
    { href: "https://github.com/xian-network", icon: "github", label: "GitHub" },
    { href: "https://forum.xian.org", icon: "discourse", label: "Discourse" },
  ];
</script>

<main class="flex flex-col items-center w-full min-h-screen">
  <ToastNotification />
  {#if showNav}
    <header class="w-full border-b border-gray-800">
      <div class="max-w-7xl mx-auto px-6">
        <div class="h-16 flex items-center justify-between">
          <a href="#/" class="font-mono text-xl">xiandao:~$</a>
          <nav class="flex items-center">
            <a
              class="px-5 h-16 flex items-center border-transparent hover:border-gray-700 border-b-2 -mb-[2px] transition-colors"
              href="#/proposals">proposals</a
            >
            <a
              class="px-5 h-16 flex items-center border-transparent hover:border-gray-700 border-b-2 -mb-[2px] transition-colors"
              href="#/about">about</a
            >
            <div class="pl-4">
              <a
                class="px-4 py-2 rounded-lg font-semibold text-sm transition-all bg-[rgba(255,255,255,0.1)] border border-[rgba(78,205,196,0.4)] backdrop-blur-sm hover:bg-[rgba(78,205,196,0.15)] hover:border-[rgba(78,205,196,0.6)] hover:transform hover:-translate-y-0.5"
                href="#/create-proposal">+ create</a
              >
            </div>
          </nav>
        </div>
      </div>
    </header>
  {/if}
  <div class="w-full max-w-7xl px-6 py-8 flex-grow">
    <Router {routes} />
  </div>
  {#if showNav}
    <Footer class="w-full border-t border-gray-800">
      <div class="w-full max-w-7xl mx-auto px-6 py-6">
        <div class="flex items-center justify-between">
          <FooterCopyright href="#/" by="XianDAO" />
          <div class="flex space-x-6">
            {#each socialLinks as { href, icon, label }}
              <a
                {href}
                class="text-gray-400 hover:text-white transition-colors"
                target="_blank"
                rel="noopener noreferrer"
              >
                <span class="sr-only">{label}</span>
                {#if icon === "telegram"}
                  <svg
                    class="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.223-.535.223l.19-2.712 4.94-4.465c.215-.19-.047-.296-.332-.106l-6.104 3.853-2.623-.916c-.57-.176-.582-.57.12-.843l10.24-3.95c.475-.176.89.107.605.944z"
                    />
                  </svg>
                {:else if icon === "discord"}
                  <svg
                    class="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515a.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0a12.64 12.64 0 0 0-.617-1.25a.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057a19.9 19.9 0 0 0 5.993 3.03a.078.078 0 0 0 .084-.028a14.09 14.09 0 0 0 1.226-1.994a.076.076 0 0 0-.041-.106a13.107 13.107 0 0 1-1.872-.892a.077.077 0 0 1-.008-.128a10.2 10.2 0 0 0 .372-.292a.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127a12.299 12.299 0 0 1-1.873.892a.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028a19.839 19.839 0 0 0 6.002-3.03a.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.956-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419c0-1.333.955-2.419 2.157-2.419c1.21 0 2.176 1.096 2.157 2.42c0 1.333-.946 2.418-2.157 2.418z"
                    />
                  </svg>
                {:else if icon === "medium"}
                  <svg
                    class="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z"
                    />
                  </svg>
                {:else if icon === "github"}
                  <svg
                    class="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      fill-rule="evenodd"
                      d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                      clip-rule="evenodd"
                    />
                  </svg>
                {:else if icon === "discourse"}
                  <svg
                    class="w-6 h-6"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="M12.103 0C18.666 0 24 5.485 24 11.997c0 6.51-5.33 11.99-11.9 11.99L0 24V11.79C0 5.28 5.532 0 12.103 0zm.116 4.563c-2.593-.003-4.996 1.352-6.337 3.57-1.33 2.208-1.387 4.957-.148 7.22L4.4 19.61l4.794-1.074c2.745 1.225 5.965.676 8.136-1.39 2.17-2.054 2.86-5.228 1.737-7.997-1.135-2.778-3.84-4.59-6.84-4.585h-.008z"
                    />
                  </svg>
                {/if}
              </a>
            {/each}
          </div>
        </div>
      </div>
    </Footer>
  {/if}
</main>

<style>
</style>
