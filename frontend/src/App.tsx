import { useState } from 'react'

import './App.css'

import type { AnalyzeResponse, Holding, Opportunity, ProtocolAnalysis, Recommendation } from './types/api'

type ProgressEvent = {
  type: 'progress'
  stage: string
  message: string
  data?: {
    holdings?: Holding[]
    protocols?: string[]
    protocol_analyses?: ProtocolAnalysis[]
    eligible_markets?: Opportunity[]
    opportunities?: Opportunity[]
  }
}

type ProtocolStatus =
  | 'waiting'
  | 'scanning'
  | 'completed'
  | 'failed'

type ProtocolProgress = {
  protocol: string
  status: ProtocolStatus
  analysis?: ProtocolAnalysis
}

type CompleteEvent = {
  type: 'complete'
  data: AnalyzeResponse
}

type ProtocolStartedEvent = {
  type: 'protocol_started'
  protocol: string
}

type ProtocolCompletedEvent = {
  type: 'protocol_completed'
  protocol: string
  analysis: ProtocolAnalysis
}

type ProtocolFailedEvent = {
  type: 'protocol_failed'
  protocol: string
}

type StreamEvent = ProgressEvent | ProtocolStartedEvent | ProtocolCompletedEvent | ProtocolFailedEvent | CompleteEvent

type PipelineStage =
  | 'wallet'
  | 'protocols'
  | 'markets'
  | 'optimize'
  | 'recommend'

type PipelineStatus =
  | 'waiting'
  | 'running'
  | 'complete'

const PIPELINE_STAGES: {
  id: PipelineStage
  number: string
  label: string
}[] = [
    { id: 'wallet', number: '01', label: 'Wallet' },
    { id: 'protocols', number: '02', label: 'Protocols' },
    { id: 'markets', number: '03', label: 'Markets' },
    { id: 'optimize', number: '04', label: 'Optimize' },
    { id: 'recommend', number: '05', label: 'Recommend' },
  ]

type StageDetails = {
  wallet?: {
    holdings: Holding[]
  }
  protocols?: {
    protocols: string[]
  }
  markets?: {
    protocolProgress: ProtocolProgress[]
    eligibleMarkets: Opportunity[]
  }
  optimize?: {
    opportunities: Opportunity[]
  }
  recommend?: {
    recommendation: Recommendation
  }
}

function App() {
  const [walletAddress, setWalletAddress] = useState('')
  const [progressMessages, setProgressMessages] = useState<string[]>([])
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [protocols, setProtocols] = useState<string[]>([])
  const [protocolAnalyses, setProtocolAnalyses] =
    useState<ProtocolAnalysis[]>([])
  const [analysis, setAnalysis] =
    useState<AnalyzeResponse | null>(null)
  const [protocolProgress, setProtocolProgress] =
    useState<ProtocolProgress[]>([])
  const [eligibleMarkets, setEligibleMarkets] =
    useState<Opportunity[]>([])
  const [currentStage, setCurrentStage] =
    useState<PipelineStage | null>(null)
  const [stageDetails, setStageDetails] =
    useState<StageDetails>({})

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
    setProgressMessages([])
    setHoldings([])
    setProtocols([])
    setProtocolAnalyses([])
    setProtocolProgress([])
    setEligibleMarkets([])
    setCurrentStage('wallet')
    setStageDetails({})

    const url =
      'http://127.0.0.1:8000/analyze' +
      `?wallet_address=${encodeURIComponent(walletAddress)}`

    const stream = new EventSource(url)

    stream.onmessage = (event) => {
      const message: StreamEvent = JSON.parse(event.data)

      if (message.type === 'progress') {
        setProgressMessages((current) => [
          ...current,
          message.message,
        ])

        if (
          message.stage === 'analyze_wallet' &&
          message.data?.holdings
        ) {
          setHoldings(message.data.holdings)


          setStageDetails((current) => ({
            ...current,
            wallet: {
              holdings: message.data!.holdings!,
            },
          }))

          setCurrentStage('protocols')
        }

        if (
          message.stage === 'discover_protocol_candidates' &&
          message.data?.protocols
        ) {
          setProtocols(message.data.protocols)

          setStageDetails((current) => ({
            ...current,
            protocols: {
              protocols: message.data!.protocols!,
            },
          }))

          setCurrentStage('markets')

          const initialProgress = message.data.protocols.map(
            (protocol) => ({
              protocol,
              status: 'waiting' as const,
            }),
          )

          setProtocolProgress(initialProgress)
        }

        if (
          message.stage === 'discover_opportunities' &&
          message.data?.protocol_analyses
        ) {
          setProtocolAnalyses(
            message.data.protocol_analyses,
          )
          setCurrentStage('optimize')
        }

        if (
          message.stage === 'discover_opportunities' &&
          message.data?.eligible_markets
        ) {
          setEligibleMarkets(
            message.data.eligible_markets,
          )

          setStageDetails((current) => ({
            ...current,
            markets: {
              protocolProgress,
              eligibleMarkets:
                message.data!.eligible_markets!,
            },
          }))

        }

        if (
          message.stage === 'optimize_eligible_markets' &&
          message.data?.opportunities
        ) {
          setStageDetails((current) => ({
            ...current,
            optimize: {
              opportunities: message.data!.opportunities!,
            },
          }))

          setCurrentStage('recommend')
        }
      }

      if (message.type === 'protocol_started') {
        setProtocolProgress((current) => {
          const updated = current.map((item) =>
            item.protocol === message.protocol
              ? {
                ...item,
                status: 'scanning' as const,
              }
              : item,
          )


          return updated
        })
      }

      if (message.type === 'protocol_completed') {
        setProtocolProgress((current) =>
          current.map((item) =>
            item.protocol === message.protocol
              ? {
                ...item,
                status: 'completed',
                analysis: message.analysis,
              }
              : item,
          ),
        )
      }

      if (message.type === 'protocol_failed') {
        setProtocolProgress((current) =>
          current.map((item) =>
            item.protocol === message.protocol
              ? {
                ...item,
                status: 'failed',
              }
              : item,
          ),
        )
      }

      if (message.type === 'complete') {
        setStageDetails((current) => ({
          ...current,
          recommend: {
            recommendation: message.data.recommendation,
          },
        }))

        setCurrentStage(null)

        setAnalysis(message.data)
        setIsLoading(false)
        stream.close()
      }
    }

    stream.onerror = () => {
      setError(
        'Unable to analyze this wallet. Please try again.',
      )
      setIsLoading(false)
      setProgressMessages([])
      stream.close()
    }
  }

  function getPipelineStatus(
    stage: PipelineStage,
  ): PipelineStatus {
    if (!isLoading && analysis) {
      return 'complete'
    }

    if (!currentStage) {
      return 'waiting'
    }

    const currentIndex = PIPELINE_STAGES.findIndex(
      (item) => item.id === currentStage,
    )

    const stageIndex = PIPELINE_STAGES.findIndex(
      (item) => item.id === stage,
    )

    if (stageIndex < currentIndex) {
      return 'complete'
    }

    if (stageIndex === currentIndex) {
      return 'running'
    }

    return 'waiting'
  }

  return (
    <main className="app">
      <header className="hero">
        <div className="hero-copy">
          <div className="brand">
            <h1>OAO</h1>
            <span>
              Onchain Asset Optimizer
            </span>
          </div>

          <p className="description">
            Analyze your Ethereum wallet for lending
            opportunities.
          </p>
        </div>

        <form className="wallet-form"
          onSubmit={handleAnalyze}>
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
        </form>
      </header>

      {(isLoading || analysis) && (
        <>
          <div className="analysis-pipeline">
            {PIPELINE_STAGES.map((stage, index) => {
              const status = getPipelineStatus(stage.id)

              return (
                <div
                  className="pipeline-item"
                  key={stage.id}
                >
                  <div
                    className={`pipeline-stage pipeline-stage--${status}`}
                  >
                    <div className="pipeline-label">
                      <span>{stage.number}</span>
                      {stage.label}
                    </div>

                    <div className="pipeline-status">
                      {status === 'complete' && '✓ COMPLETE'}
                      {status === 'running' && '● RUNNING'}
                      {status === 'waiting' && 'WAITING'}
                    </div>
                  </div>

                  {index < PIPELINE_STAGES.length - 1 && (
                    <span className="pipeline-arrow">
                      →
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          <div className="pipeline-details-grid">
            <div className="stage-detail">
              {stageDetails.wallet && (
                <>
                  <div className="stage-detail-title">
                    &gt; holdings
                  </div>

                  {stageDetails.wallet.holdings.map(
                    (holding) => (
                      <div
                        className="stage-detail-row"
                        key={`${holding.network}-${holding.symbol}`}
                      >
                        <span>{holding.symbol}</span>
                        <span>{holding.amount}</span>
                      </div>
                    ),
                  )}
                </>
              )}

              {currentStage === 'wallet' && (
                <p className="stage-running-text">&gt; analyzing wallet holdinngs
                  <span className="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                  </span>
                </p>
              )}
            </div>

            <div className="stage-detail">
              {stageDetails.protocols && (
                <>
                  <div className="stage-detail-title">
                    &gt; protocols
                  </div>

                  {stageDetails.protocols.protocols.map(
                    (protocol) => (
                      <div
                        className="stage-detail-row"
                        key={protocol}
                      >
                        <span>{protocol}</span>
                      </div>
                    ),
                  )}
                </>
              )}

              {currentStage === 'protocols' && (
                <p className="stage-running-text">&gt; discovering lending protocols
                  <span className="loading-dots">
                    <span>.</span>
                    <span>.</span>
                    <span>.</span>
                  </span>
                </p>
              )}
            </div>

            <div className="stage-detail">
              {protocolProgress.length > 0 && (
                <>
                  <div className="stage-detail-title">
                    &gt; markets
                  </div>

                  {protocolProgress.map((item) => (
                    <div
                      className="stage-detail-row"
                      key={item.protocol}
                    >
                      <span>{item.protocol}</span>

                      <span>
                        {item.status === 'waiting' &&
                          'WAITING'}

                        {item.status === 'scanning' &&
                          (
                            <>
                              <span className="scanning-dot">●</span>
                              {' SCANNING'}
                            </>
                          )}

                        {item.status === 'completed' &&
                          `✓ ${item.analysis?.market_count ?? 0}`}

                        {item.status === 'failed' &&
                          '✕ FAILED'}
                      </span>
                    </div>
                  ))}
                </>
              )}



              {currentStage === 'markets' &&
                protocolProgress.length === 0 && (
                  <p className="stage-running-text">&gt; preparing market scan
                    <span className="loading-dots">
                      <span>.</span>
                      <span>.</span>
                      <span>.</span>
                    </span>
                  </p>
                )}
            </div>

            <div className="stage-detail">
              {stageDetails.optimize && (
                <>
                  <div className="stage-detail-title">
                    &gt; selected
                  </div>

                  {stageDetails.optimize.opportunities.map(
                    (opportunity) => (
                      <div
                        className="stage-detail-row"
                        key={opportunity.market_id}
                      >
                        <span>{opportunity.symbol}</span>
                        <span>{opportunity.protocol}</span>
                      </div>
                    ),
                  )}
                </>
              )}

              {currentStage === 'optimize' &&
                !stageDetails.optimize && (
                  <p className="stage-running-text">&gt; selecting best opportunities
                    <span className="loading-dots">
                      <span>.</span>
                      <span>.</span>
                      <span>.</span>
                    </span>
                  </p>
                )}
            </div>
            <div className="stage-detail">
              {stageDetails.recommend && (
                <>
                  <div className="stage-detail-title">
                    &gt; recommendation
                  </div>

                  <p className="stage-detail-summary">
                    {stageDetails.recommend.recommendation.summary}
                  </p>
                </>
              )}

              {currentStage === 'recommend' &&
                !stageDetails.recommend && (
                  <p className="stage-running-text">&gt; generating recommendation
                    <span className="loading-dots">
                      <span>.</span>
                      <span>.</span>
                      <span>.</span>
                    </span>
                  </p>
                )}
            </div>
          </div>
        </>
      )}

      {analysis && (
        <section className="recommendation-panel">
          <div className="recommendation-panel-header">
            <div>
              <span className="recommendation-eyebrow">
                FINAL OUTPUT
              </span>

              <h2>Recommendation</h2>
            </div>

            <span className="recommendation-status">
              ✓ ANALYSIS COMPLETE
            </span>
          </div>

          <div className="recommendation-body">
            <p className="recommendation-summary">
              {analysis.recommendation.summary}
            </p>

            {analysis.recommendation.details.length > 0 && (
              <div className="recommendation-details">
                {analysis.recommendation.details.map(
                  (detail, index) => (
                    <div
                      className="recommendation-detail"
                      key={`${index}-${detail}`}
                    >
                      <span>&gt;</span>
                      <p>{detail}</p>
                    </div>
                  ),
                )}
              </div>
            )}
          </div>
        </section>
      )}
    </main>
  )
}

export default App