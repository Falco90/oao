import './App.css'

function App() {
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
          />

          <button
            className="analyze-button"
            type="button"
          >
            Analyze
          </button>
        </div>
      </section>
    </main>
  )
}

export default App