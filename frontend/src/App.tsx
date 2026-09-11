import { useState } from 'react'

import './App.css'

import type { AnalyzeResponse } from './types/api'

import {
  formatRate,
  formatUsd,
  getSelectionReason,
} from './utils/format'

type ProgressEvent = {
  type: 'progress'
  stage: string
  message: string
}

type CompleteEvent = {
  type: 'complete'
  data: AnalyzeResponse
}

type StreamEvent = ProgressEvent | CompleteEvent

function App() {
  const [walletAddress, setWalletAddress] = useState('')
  const [progressMessage, setProgressMessage] = useState('')
  const [analysis, setAnalysis] =
    useState<AnalyzeResponse | null>(null)

  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isValidWalletAddress =
    /^0x[a-fA-F0-9]{40}$/.test(walletAddress)

  function handleAnalyze() {
    if (!isValidWalletAddress) {
      return
    }

    setIsLoading(true)
    setError(null)
    setAnalysis(null)
    setProgressMessage('Starting analysis...')

    const url =
      'http://127.0.0.1:8000/analyze/stream' +
      `?wallet_address=${encodeURIComponent(walletAddress)}`

    const stream = new EventSource(url)

    stream.onmessage = (event) => {
      const message: StreamEvent = JSON.parse(event.data)

      if (message.type === 'progress') {
        setProgressMessage(message.message)
      }

      if (message.type === 'complete') {
        setAnalysis(message.data)
        setIsLoading(false)
        setProgressMessage('')
        stream.close()
      }
    }

    stream.onerror = () => {
      setError(
        'Unable to analyze this wallet. Please try again.',
      )
      setIsLoading(false)
      setProgressMessage('')
      stream.close()
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <div>
          <h1>OAO</h1>
          <p className="subtitle">
            Onchain portfolio optimizer
          </p>

          <p className="description">
            Analyze your Ethereum wallet for lending
            opportunities.
          </p>
        </div>

        <div className="wallet-form">
          <input
            className="wallet-input"
            type="text"
            value={walletAddress}
            onChange={(event) =>
              setWalletAddress(event.target.value)
            }
            placeholder="0x wallet address"
            disabled={isLoading}
          />

          <button
            className="analyze-button"
            type="button"
            onClick={handleAnalyze}
            disabled={!isValidWalletAddress || isLoading}
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {isLoading && (
          <p className="status-message">
            {progressMessage}
          </p>
        )}

        {error && (
          <p className="error-message">
            {error}
          </p>
        )}

        {analysis && (
          <div className="analysis-results">
            <section className="result-section">
              <h2>Wallet holdings</h2>

              <div className="result-list">
                {analysis.holdings.map((holding) => (
                  <div
                    className="result-row"
                    key={
                      holding.contract_address ??
                      holding.symbol
                    }
                  >
                    <span>
                      {holding.symbol}
                    </span>

                    <strong>
                      {holding.amount}
                    </strong>
                  </div>
                ))}
              </div>
            </section>

            <section className="result-section">
              <h2>Best opportunities</h2>

              <div className="card-grid">
                {analysis.opportunities.map(
                  (opportunity) => (
                    <article
                      className="opportunity-card"
                      key={opportunity.market_id}
                    >
                      <h3>
                        {opportunity.protocol}
                      </h3>

                      <p>
                        {opportunity.symbol}
                      </p>

                      <div className="result-row">
                        <span>Supply rate</span>

                        <strong>
                          {formatRate(
                            opportunity.supply_rate,
                          )}
                        </strong>
                      </div>

                      <div className="result-row">
                        <span>TVL</span>

                        <strong>
                          {formatUsd(
                            opportunity.tvl_usd,
                          )}
                        </strong>
                      </div>

                      <div className="result-row">
                        <span>Subgraph</span>

                        <strong>
                          {
                            opportunity.subgraph_name
                          }
                        </strong>
                      </div>
                    </article>
                  ),
                )}
              </div>
            </section>

            <section className="result-section">
              <h2>Protocols analyzed</h2>

              <div className="card-grid">
                {analysis.protocol_analyses.map(
                  (protocol) => (
                    <article
                      className="protocol-card"
                      key={protocol.protocol}
                    >
                      <h3>
                        {protocol.protocol}
                      </h3>

                      <p>
                        Markets found:{' '}
                        {protocol.market_count}
                      </p>

                      {protocol.validated_subgraphs
                        .length > 0 ? (
                        <ul>
                          {protocol.validated_subgraphs.map(
                            (subgraph) => (
                              <li key={subgraph}>
                                {subgraph}
                              </li>
                            ),
                          )}
                        </ul>
                      ) : (
                        <p>
                          No validated Ethereum
                          Subgraphs
                        </p>
                      )}
                    </article>
                  ),
                )}
              </div>
            </section>

            <section className="result-section">
              <h2>How this was chosen</h2>

              <div className="card-grid">
                {analysis.selection_analyses.map(
                  (selection) => (
                    <article
                      className="selection-card"
                      key={selection.symbol}
                    >
                      <h3>
                        {selection.symbol}
                      </h3>

                      <div className="result-row">
                        <span>
                          Selected protocol
                        </span>

                        <strong>
                          {
                            selection.selected_protocol
                          }
                        </strong>
                      </div>

                      <div className="result-row">
                        <span>
                          Selected rate
                        </span>

                        <strong>
                          {formatRate(
                            selection.selected_rate,
                          )}
                        </strong>
                      </div>

                      <div className="result-row">
                        <span>Best rate</span>

                        <strong>
                          {formatRate(
                            selection.best_rate,
                          )}
                        </strong>
                      </div>

                      <div className="result-row">
                        <span>Selected TVL</span>

                        <strong>
                          {formatUsd(
                            selection.selected_tvl_usd,
                          )}
                        </strong>
                      </div>

                      <p className="selection-reason">
                        {getSelectionReason(
                          selection.best_rate,
                          selection.selected_rate,
                          selection.competitive_market_count,
                        )}
                      </p>
                    </article>
                  ),
                )}
              </div>
            </section>

            <section className="result-section">
              <h2>Recommendation</h2>

              <p className="recommendation-summary">
                {analysis.recommendation.summary}
              </p>

              <ul>
                {analysis.recommendation.details.map(
                  (detail, index) => (
                    <li key={index}>
                      {detail}
                    </li>
                  ),
                )}
              </ul>
            </section>
          </div>
        )}
      </section>
    </main>
  )
}

export default App