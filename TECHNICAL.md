# Technical Documentation

## Smart Contract

The voting system is implemented as a Lamden smart contract in `contracts/voting.py`. The contract manages proposal creation, voting, and vote tallying.

### State Variables

- `owner`: Contract owner address
- `proposals`: Hash storing proposal details
- `proposal_votes`: Hash storing voter choices by proposal ID and voter
- `proposal_voters`: Hash storing voter addresses by proposal ID and index
- `proposal_vote_counts`: Hash storing number of voters per proposal
- `auto_update_tallies`: Boolean flag for automatic tally updates
- `proposal_metrics`: Hash storing vote counts and power metrics

### Key Functions

#### Proposal Management

```python
@export
def create_proposal(title: str, description: str, expires_at: str)
```
Creates a new proposal with the following requirements:
- Title must be at least 10 characters
- Description must be at least 100 characters
- Expiry date must be in the future
- Creator must hold tokens

#### Voting

```python
@export
def vote(proposal_id: str, choice: str)
```
Records a vote on a proposal:
- Choices: "y" (yes), "n" (no), "-" (abstain)
- Voter must hold tokens
- One vote per address per proposal
- Vote weight based on token balance

#### Vote Tallying

```python
@export
def finalize_proposal(proposal_id: str)
```
Finalizes a proposal after expiry:
- Calculates final vote counts
- Updates proposal metrics
- Changes proposal status to "finalized"

### Security Features

- Token holder verification
- Owner-only administrative functions
- Expiry date enforcement
- Vote duplication prevention

## Frontend Application

The frontend is a Svelte-based SPA using TailwindCSS and Flowbite for styling.

### Key Dependencies

- Svelte 5.15.0
- Vite 6.0.5
- TailwindCSS 3.4.9
- Flowbite-Svelte 0.47.4
- TipTap Editor 2.11.5

### Component Structure

```
src/
├── components/
│   ├── VoteMetricsBar.svelte    # Displays voting statistics
│   ├── VoteButtons.svelte       # Voting interface
│   ├── ProposalCard.svelte      # Proposal display card
│   ├── CreateProposalButtons.svelte
│   ├── StatusPill.svelte        # Status indicator
│   └── TipTap.svelte           # Rich text editor
├── routes/
│   ├── Proposals.svelte         # Proposal listing
│   ├── ViewProposal.svelte      # Single proposal view
│   ├── CreateProposal.svelte    # Proposal creation
│   └── Landing.svelte           # Home page
└── lib/
    └── ts/js/
        ├── graphql/             # API integration
        ├── utils.ts             # Utility functions
        └── store.ts             # State management
```

### State Management

The application uses Svelte stores for state management:
- Proposal data
- User voting status
- Token balances
- Authentication state

### API Integration

GraphQL is used for backend communication:
- Proposal queries
- Vote submission
- Real-time updates
- Token balance checks

## Testing

### Smart Contract Tests

Located in `contracts/tests/test_voting.py`:
- Proposal creation validation
- Voting mechanics
- Token balance checks
- Finalization logic
- Edge cases

Run tests with:
```bash
python -m pytest tests/
```

### Frontend Testing

Component testing using Svelte's testing utilities:
- Component rendering
- User interactions
- State updates
- API integration

## Deployment

### Smart Contract Deployment

1. Compile contract:
```bash
lamden-compiler contracts/voting.py
```

2. Deploy to network:
```bash
lamden-deploy voting.py
```

### Frontend Deployment

1. Build production assets:
```bash
npm run build
```

2. Deploy `dist/` directory to web server

## Performance Considerations

### Smart Contract

- Efficient state variable structure
- Optimized vote tallying
- Gas-efficient storage patterns
- Minimal on-chain computation

### Frontend

- Code splitting
- Lazy loading
- Optimized bundle size
- Caching strategies
- Real-time updates optimization

## Security Considerations

### Smart Contract

- Access control
- Input validation
- State manipulation protection
- Token balance verification
- Timestamp manipulation prevention

### Frontend

- Input sanitization
- XSS prevention
- CORS configuration
- API rate limiting
- Secure authentication

## Future Improvements

1. Smart Contract
   - Multi-signature proposal creation
   - Delegation system
   - Vote locking mechanism
   - Proposal categories

2. Frontend
   - Mobile optimization
   - Offline support
   - Advanced analytics
   - Social features
   - Notification system 
