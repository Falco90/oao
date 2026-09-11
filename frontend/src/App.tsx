import { useState } from 'react'
import type { AnalyzeResponse } from './types/api'
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
          <section className="results">
            <h2>Wallet holdings</h2>

            {analysis.holdings.map((holding) => (
              <div key={`${holding.symbol}-${holding.contract_address}`}>
                <strong>{holding.symbol}</strong>
                <span>{holding.amount}</span>
              </div>
            ))}
          </section>
        )}
      </section>
    </main>
  )
}

export default App