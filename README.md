# OAO - Onchain Asset Optimizer

OAO is an AI-powered agent that analyzes an Ethereum wallet and
identifies lending opportunities across DeFi protocols.

Given a wallet address, OAO inspects the wallet's supported assets,
dynamically discovers relevant lending protocols and their markets,
filters opportunities using deterministic eligibility rules, and selects
competitive lending markets based on yield and liquidity.

The analysis is streamed to the frontend in real time.

## Live App

The app is live at [oao-agent.vercel.app](https://oao-agent.vercel.app/)

WARNING: Due to Render's cold start policy on the free deployment plan, the first wallet request might take up to 50 seconds if the app has been inactive for a while.

## How It Works

OAO processes a wallet through five stages:

**Wallet → Protocols → Markets → Optimize → Recommend**

### 1. Wallet Analysis

OAO retrieves the wallet's supported Ethereum assets and normalizes the
holdings for downstream analysis.

### 2. Protocol Discovery

An LLM identifies lending protocols that may provide relevant
opportunities. The LLM is used for discovery rather than as an
authoritative source of financial data.

### 3. Market Discovery

OAO uses The Graph MCP to discover and validate protocol Subgraphs, query
lending markets, match those markets against the wallet's assets, and
apply eligibility rules.

### 4. Optimization

A deterministic Python optimizer compares eligible markets by supply
rate and liquidity. Markets close to the best available rate are treated
as competitive, with TVL used to prefer deeper liquidity.

### 5. Recommendation

The LLM receives the optimizer's selected opportunities and explains the
result in human-readable form. It does not choose or modify the selected
markets.

## Architecture

The application consists of the following components:

-   **LangGraph** - orchestrates the analysis workflow.
-   **LLM (Claude Sonnet 5)** - discovers candidate protocols and explains the final
    recommendation.
-   **The Graph Token API** - retrieves wallet balances and supported
    assets.
-   **The Graph Subgraph MCP** - discovers and validates relevant
    Subgraphs.
-   **Subgraphs** - provide lending market data including rates, TVL,
    assets, and market state.
-   **Python** - performs authoritative validation, filtering,
    matching, and optimization.
-   **FastAPI + SSE** - streams analysis progress to the frontend.
-   **React** - Gets wallet input and presents the analysis as it happens.

LLM-generated protocol suggestions are never treated as market data.
Market selection is grounded in data retrieved from The Graph and
evaluated deterministically.

## LangGraph Agent Workflow

``` text
START
  ↓
analyze_wallet
  ↓
discover_protocol_candidates
  ↓
discover_opportunities
  ↓
optimize_eligible_markets
  ↓
recommend
  ↓
END
```

## Tech Stack

**Backend**

-   Python
-   LangGraph
-   Claude Sonnet 5 (Anthropic)
-   FastAPI
-   Pydantic

**Onchain data**

-   The Graph Token API
-   The Graph Subgraph MCP
-   The Graph Subgraphs

**Frontend**

-   React
-   TypeScript
-   Vite

**Deployment**

-   Vercel - frontend
-   Render - API

## Running Locally

### Requirements

-   Python
-   `uv`
-   Node.js / npm

### Backend

Clone the repository and install the Python dependencies:

``` bash
uv sync
```

Create a `.env` file in the project root and follow the `.env.example` file.

Start the API:

``` bash
uv run uvicorn oao.api:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend

From the frontend directory:

``` bash
cd frontend
npm install
```

Create a `.env` file in the frontend folder and follow the `.env.example` file there.

Start Vite:

``` bash
npm run dev
```

Then open the local URL printed by Vite.

## API

OAO exposes a streaming analysis endpoint:

``` http
GET /analyze?wallet_address=0x...
```