<script lang="ts">
  import CreateProposalButtons from "../components/CreateProposalButtons.svelte";
  import Tiptap from "../components/TipTap.svelte";
  import { P } from "flowbite-svelte";
  import { unixToPythonDatetimeString } from "../lib/ts/js/utils";

  let title = "";
  let content = "";
  let durationValue = 1;
  let durationUnit = "days";
  let kwargs = {
    title: "",
    description: "",
    expires_at: 0,
  };

  // Load saved data from localStorage on component initialization
  if (typeof window !== "undefined") {
    title = localStorage.getItem("proposalTitle") || "";
    content = localStorage.getItem("proposalContent") || "";
  }

  // Save to localStorage when title or content changes
  $: {
    console.log("Saving to localStorage:", { title, content });
    if (typeof window !== "undefined") {
      localStorage.setItem("proposalTitle", title);
      localStorage.setItem("proposalContent", content);
    }
  }

  function calculateExpiryDate() {
    const now = new Date();
    const multiplier = {
      hours: 60 * 60 * 1000,
      days: 24 * 60 * 60 * 1000,
      weeks: 7 * 24 * 60 * 60 * 1000
    };
    const futureDate = new Date(now.getTime() + (durationValue * multiplier[durationUnit]));
    return futureDate;
  }

  $: kwargs.description = content;
  $: kwargs.title = title;
  $: kwargs.expires_at = unixToPythonDatetimeString(calculateExpiryDate().getTime());
  $: console.log({ kwargs });
</script>

<div class="p8 w-3/4">
  <input
    type="text"
    bind:value={title}
    placeholder="Enter proposal title"
    class="md:w-3/4 p-2 mb-4 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  />



  <Tiptap bind:content />
  <div>
    <P class="font-semibold">Voting concludes:</P>
  </div>
  <div class="md:w-1/2 flex gap-4 items-center">
    <input
      type="number"
      bind:value={durationValue}
      min="1"
      class="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-24"
    />
    <select
      bind:value={durationUnit}
      class="p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <option value="hours">Hours</option>
      <option value="days">Days</option>
      <option value="weeks">Weeks</option>
    </select>
  </div>
  <P>{calculateExpiryDate().toLocaleString()}</P>
  <CreateProposalButtons kwargs={kwargs} />
</div>

<style>
  input {
    width: 100%;
  }
</style>
