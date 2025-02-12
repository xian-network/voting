<script lang="ts">
  import { unixToPythonDatetimeString } from "../lib/ts/js/utils";
  import CreateProposalButtons from "../components/CreateProposalButtons.svelte";

  let title = "";
  let description = "";
  let durationValue = 1;
  let durationUnit: "hours" | "days" | "weeks" = "days";
  let discussionUrl = "";
  let formErrors: { title?: string; description?: string; discussionUrl?: string } = {};
  let touched = { title: false, description: false, discussionUrl: false };

  // Load saved data from localStorage
  if (typeof window !== "undefined") {
    title = localStorage.getItem("proposalTitle") || "";
    description = localStorage.getItem("proposalContent") || "";
    discussionUrl = localStorage.getItem("proposalDiscussionUrl") || "";
  }

  // Save to localStorage when values change
  $: {
    if (typeof window !== "undefined") {
      localStorage.setItem("proposalTitle", title);
      localStorage.setItem("proposalContent", description);
      localStorage.setItem("proposalDiscussionUrl", discussionUrl);
    }
  }

  // Validate on input change and update isValid
  $: {
    if (touched.title) validateField('title', title);
    if (touched.description) validateField('description', description);
    if (touched.discussionUrl) validateField('discussionUrl', discussionUrl);
  }

  // Computed property for form validity
  $: isValid = title.length >= 10 && description.length >= 100 && (!discussionUrl || isValidUrl(discussionUrl));

  function isValidUrl(url: string): boolean {
    if (!url) return true; // Empty URL is valid
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  // Process description to preserve line breaks
  $: processedDescription = description.replace(/\n/g, "\\n");

  function validateField(field: 'title' | 'description' | 'discussionUrl', value: string) {
    if (field === 'title' && value.length < 10) {
      formErrors.title = "Title must be at least 10 characters long";
    } else if (field === 'title') {
      delete formErrors.title;
    }

    if (field === 'description' && value.length < 100) {
      formErrors.description = "Description must be at least 100 characters long";
    } else if (field === 'description') {
      delete formErrors.description;
    }

    if (field === 'discussionUrl' && value && !isValidUrl(value)) {
      formErrors.discussionUrl = "Please enter a valid URL";
    } else if (field === 'discussionUrl') {
      delete formErrors.discussionUrl;
    }

    formErrors = formErrors; // Trigger reactivity
  }

  function handleInput(field: 'title' | 'description' | 'discussionUrl') {
    touched[field] = true;
  }

  function validateForm(): boolean {
    touched.title = true;
    touched.description = true;
    touched.discussionUrl = true;
    
    validateField('title', title);
    validateField('description', description);
    validateField('discussionUrl', discussionUrl);

    return title.length >= 10 && description.length >= 100 && (!discussionUrl || isValidUrl(discussionUrl));
  }

  function calculateExpiryDate() {
    const now = new Date();
    const multiplier: Record<string, number> = {
      hours: 60 * 60 * 1000,
      days: 24 * 60 * 60 * 1000,
      weeks: 7 * 24 * 60 * 60 * 1000,
    };
    const futureDate = new Date(
      now.getTime() + durationValue * multiplier[durationUnit],
    );
    return futureDate;
  }

  let kwargs = {
    title: "",
    description: "",
    expires_at: "",
    metadata: {}
  };

  $: kwargs.description = processedDescription;
  $: kwargs.title = title;
  $: kwargs.expires_at = unixToPythonDatetimeString(
    calculateExpiryDate().getTime(),
  );
  $: kwargs.metadata = discussionUrl ? { discussion_url: discussionUrl } : {};

  function handleSubmitProposalClick() {
    if (!validateForm()) {
      return;
    }
    // Continue with proposal submission
  }
</script>

<main class="flex flex-col items-center min-h-screen p-5">
  <div class="w-full max-w-4xl px-8 mx-auto">
    <h1 class="text-4xl font-bold mb-8">Create New Proposal</h1>

    <div class="space-y-8">
      <div class="form-group">
        <label for="title" class="block text-xl font-medium mb-3">Title</label>
        <input
          type="text"
          id="title"
          bind:value={title}
          on:input={() => handleInput('title')}
          placeholder="Enter proposal title (minimum 10 characters)"
          class="w-full p-4 text-lg rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500
            {formErrors.title && touched.title ? 'border-red-500' : ''}"
        />
        {#if formErrors.title && touched.title}
          <p class="text-red-500 mt-2 text-base">{formErrors.title}</p>
        {/if}
      </div>

      <div class="form-group">
        <label for="description" class="block text-xl font-medium mb-3">Description</label>
        <textarea
          id="description"
          bind:value={description}
          on:input={() => handleInput('description')}
          placeholder="Enter proposal description (minimum 100 characters)"
          rows="12"
          class="w-full p-4 text-lg rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500
            {formErrors.description && touched.description ? 'border-red-500' : ''}"
        ></textarea>
        {#if formErrors.description && touched.description}
          <p class="text-red-500 mt-2 text-base">{formErrors.description}</p>
        {/if}
        <p class="text-gray-400 mt-2 text-sm">Characters: {description.length}/100</p>
      </div>

      <div class="form-group">
        <label for="discussionUrl" class="block text-xl font-medium mb-3">Discussion URL <span class="text-gray-400 text-base">(optional)</span></label>
        <input
          type="url"
          id="discussionUrl"
          bind:value={discussionUrl}
          on:input={() => handleInput('discussionUrl')}
          placeholder="Enter URL for discussion thread"
          class="w-full p-4 text-lg rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500
            {formErrors.discussionUrl && touched.discussionUrl ? 'border-red-500' : ''}"
        />
        {#if formErrors.discussionUrl && touched.discussionUrl}
          <p class="text-red-500 mt-2 text-base">{formErrors.discussionUrl}</p>
        {/if}
      </div>

      <div class="form-group">
        <label class="block text-xl font-medium mb-3">Voting Duration</label>
        <div class="flex gap-6 items-center">
          <input
            type="number"
            bind:value={durationValue}
            min="1"
            class="w-32 p-4 text-lg rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
          />
          <select
            bind:value={durationUnit}
            class="p-4 text-lg rounded-lg bg-gray-800 border border-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 min-w-[150px]"
          >
            <option value="hours">Hours</option>
            <option value="days">Days</option>
            <option value="weeks">Weeks</option>
          </select>
        </div>
        <p class="text-gray-400 mt-3 text-lg">
          Voting concludes: {calculateExpiryDate().toLocaleString()}
        </p>
      </div>

      <CreateProposalButtons 
        {kwargs} 
        {handleSubmitProposalClick}
        {isValid}
      />
    </div>
  </div>
</main>

<style lang="scss">
  :global(body) {
    background: linear-gradient(135deg, #121212, #1e1e2e);
    color: #e0e0e0;
  }

  .form-group {
    @apply bg-gray-900 p-8 rounded-xl border border-gray-800;
  }

  input[type="text"],
  input[type="number"],
  textarea,
  select {
    @apply text-white;

    &::placeholder {
      @apply text-gray-500;
    }
  }
</style>
