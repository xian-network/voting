## Design & Running the SPA

The Contributor Voting application is built as a modern Single Page Application (SPA) using the following technology stack:

- [Svelte](https://svelte.dev/) - A modern, lightweight frontend framework
- [TypeScript](https://www.typescriptlang.org/) - For type-safe JavaScript development
- [Vite](https://vitejs.dev/) - Next generation frontend tooling
- [TailwindCSS](https://tailwindcss.com/) - For utility-first styling
- [Flowbite-Svelte](https://flowbite-svelte.com/) - UI component library

## How Voting Works

The voting system is implemented as a Xian smart contract that enables token-weighted governance. Here's how it works:

### Proposal Creation

1. Any token holder can create a proposal by providing:
   - Title (10-50 characters)
   - Description (minimum 100 characters)
   - Expiration date and time
   - Optional metadata

2. Creating a proposal requires paying a proposal fee (configurable by the contract owner)

### Voting Process

1. Token holders can vote on active proposals with three options:
   - "y" (Yes/For)
   - "n" (No/Against)
   - "-" (Abstain)

2. Key voting features:
   - Each address can vote once per proposal
   - Votes can be changed while the proposal is active
   - Vote weight is determined by the voter's token balance
   - Only votes from current token holders are counted

### Vote Tallying

The system tracks two types of metrics for each proposal:
1. Raw vote counts (total number of voters for each choice)
2. Power-weighted totals (sum of token balances for each choice)

Tallies can be updated in two ways:
- Automatically after each vote (if enabled by contract settings)
- Manually by token holders during the voting period

### Proposal Finalization

1. Once a proposal expires:
   - No more votes can be cast
   - The proposal must be finalized to record final vote tallies
   - Final tallies are calculated using current token balances at the time of finalization

2. The finalization process:
   - Calculates and stores final vote counts and power-weighted totals
   - Marks the proposal as "finalized"
   - Emits an event with the final results

### Transparency

All voting actions emit blockchain events for:
- Proposal creation
- Vote casting (including vote changes)
- Proposal finalization with results

These events enable full transparency and auditability of the voting process.

### Prerequisites

Before running the SPA, ensure you have:

- Node.js (v18 or higher)
- npm (comes with Node.js)

### Development Setup

1. Navigate to the SPA directory:
   ```bash
   cd voting-spa
   ```

2. Install dependencies:
   ```bash
   npm ci
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   This will start the development server at `http://localhost:5173` (or another port if 5173 is in use)

### Building for Production

To create a production build:

```bash
npm run build
```

The built files will be in the `dist` directory, ready for deployment.

### Preview Production Build

To preview the production build locally:

```bash
npm run preview
```

### Type Checking

To run type checking:

```bash
npm run check
```

### Project Structure

The SPA follows a standard Svelte project structure:

```
voting-spa/
├── src/
│   ├── routes/          # Page components
│   ├── components/      # Reusable UI components
│   ├── lib/            # Utilities and shared code
│   └── App.svelte      # Root component
├── public/             # Static assets
└── index.html          # Entry point
```

### Deployment

The application is automatically deployed to GitHub Pages when changes are pushed to the main branch. The deployment process is handled by GitHub Actions as defined in `.github/workflows/deploy.yml`.

### Development Notes

- The application uses Svelte's built-in reactivity system for state management
- TailwindCSS is used for styling with utility classes
- TypeScript is used throughout the project for better type safety and developer experience
- The SPA interacts with Xian smart contracts through the provided utilities in `src/lib/ts/js/xian-dapp-utils.ts` 