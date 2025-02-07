# Contributor Voting System

A decentralized voting system that allows token holders to create and vote on proposals. The system consists of a smart contract written in Python and a modern web interface built with Svelte.

## Overview

The Contributor Voting System enables token holders to:
- Create proposals with titles and detailed descriptions
- Vote on active proposals (Yes/No/Abstain)
- View proposal details and real-time voting metrics
- Track voting power based on token holdings
- Automatically tally votes and finalize proposals after expiration

### Key Features

- **Token-based Voting**: Only token holders can create proposals and vote
- **Power-weighted Voting**: Votes are weighted by the number of tokens held
- **Real-time Metrics**: Live updates of vote counts and voting power distribution
- **Automatic Finalization**: Proposals are automatically finalized after expiration
- **Modern UI**: Responsive and intuitive interface built with Svelte and Flowbite

## Project Structure

```
contributor-voting/
├── contracts/           # Smart contract code
│   ├── voting.py       # Main voting contract
│   └── tests/          # Contract tests
└── voting-spa/         # Frontend Single Page Application
    ├── src/            # Source code
    ├── public/         # Static assets
    └── package.json    # Frontend dependencies
```

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Git

## Installation

### Smart Contract Setup

1. Set up a Python virtual environment:

```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (WSL)
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd voting-spa
```

2. Install dependencies:

```bash
npm install
```

## Development

### Running the Smart Contract Tests

```bash
cd contracts
python -m pytest tests/
```

### Running the Frontend Development Server

```bash
cd voting-spa
npm run dev
```

The development server will start at `http://localhost:5173`

### Building for Production

```bash
cd voting-spa
npm run build
```

The production build will be available in the `dist` directory.

## Environment Setup

### Mac OS

1. Install Homebrew if not already installed:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Node.js:
```bash
brew install node
```

3. Install Python:
```bash
brew install python@3.8
```

### Linux

1. Update package manager:
```bash
sudo apt update
sudo apt upgrade
```

2. Install Node.js:
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

3. Install Python:
```bash
sudo apt-get install python3.8 python3.8-venv
```

### Windows (WSL)

1. Install WSL if not already installed:
```powershell
wsl --install
```

2. Install Node.js:
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

3. Install Python:
```bash
sudo apt-get update
sudo apt-get install python3.8 python3.8-venv
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 
