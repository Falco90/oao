import { useState } from 'react'
import type { AnalyzeResponse } from './types/api'
import {
  formatRate,
  formatUsd,
  getSelectionReason,
} from './utils/format'
import './App.css'

function App() {
  const [walletAddress, setWalletAddress] = useState('')
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null)

  const isValidWalletAddress =
    /^0x[a-fA-F0-9]{40}$/.test(walletAddress)

  async function handleAnalyze() {
    const response = await fetch(
      'http://127.0.0.1:8000/analyze',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
        }),
      },
    )

    const data: AnalyzeResponse = await response.json()

    setAnalysis(data)
  }

  return (
    <main className="app">
      <section className="hero">
        <h1 className="title">OAO</h1>

        <p className="subtitle">
          Onchain portfolio optimizer
        </p>

        <p className="description">
          Analyze your Ethereum wallet for lending opportunities.
        </p>

        <div className="wallet-form">
          <input
            className="wallet-input"
            type="text"
            placeholder="0x wallet address..."
            value={walletAddress}
            onChange={(event) => {
              setWalletAddress(event.target.value)
            }}
          />

          <button
            className="analyze-button"
            type="button"
            disabled={!isValidWalletAddress}
            onClick={handleAnalyze}
          >
            Analyze
          </button>
        </div>
        {analysis && (
          <div className="analysis-results">
            <section className="result-section">
              <h2>Wallet holdings</h2>

              <div className="result-list">
                {analysis.holdings.map((holding) => (
                  <div
                    className="result-row"
                    key={`${holding.symbol}-${holding.contract_address}`}
                  >
                    <strong>{holding.symbol}</strong>
                    <span>{holding.amount}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="result-section">
              <h2>Best opportunities</h2>

              <div className="card-grid">
                {analysis.opportunities.map((opportunity) => (
                  <article
                    className="opportunity-card"
                    key={`${opportunity.protocol}-${opportunity.market_id}`}
                  >
                    <h3>
                      {opportunity.protocol} — {opportunity.symbol}
                    </h3>

                    <p>
                      Supply rate: {formatRate(opportunity.supply_rate)}
                    </p>

                    <p>
                      TVL: {formatUsd(opportunity.tvl_usd)}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="result-section">
              <h2>How this was chosen</h2>

              <div className="card-grid">
                {analysis.selection_analyses.map((selection) => (
                  <article
                    className="selection-card"
                    key={selection.symbol}
                  >
                    <h3>
                      {selection.symbol} → {selection.selected_protocol}
                    </h3>

                    <p>Market: {selection.selected_subgraph}</p>

                    <p>
                      Best rate: {formatRate(selection.best_rate)}
                    </p>

                    <p>
                      Selected rate: {formatRate(selection.selected_rate)}
                    </p>

                    <p>
                      TVL: {formatUsd(selection.selected_tvl_usd)}
                    </p>

                    <p>
                      Competitive markets: {selection.competitive_market_count}
                    </p>

                    <p className="selection-reason">
                      {getSelectionReason(
                        selection.best_rate,
                        selection.selected_rate,
                        selection.competitive_market_count,
                      )}
                    </p>
                  </article>
                ))}
              </div>
            </section>

            <section className="result-section recommendation-card">
              <h2>Recommendation</h2>

              <p className="recommendation-summary">
                {analysis.recommendation.summary}
              </p>

              <ul>
                {analysis.recommendation.details.map((detail, index) => (
                  <li key={index}>
                    {detail}
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </section>
    </main>
  )
}

export default App