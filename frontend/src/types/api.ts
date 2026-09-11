export type Holding = {
  symbol: string
  amount: string
  network: string
  contract_address: string | null
}

export type Opportunity = {
  protocol: string
  subgraph_name: string
  symbol: string
  asset_address: string
  market_id: string
  tvl_usd: string
  supply_rate: string
  is_active: boolean
}

export type ProtocolAnalysis = {
  protocol: string
  validated_subgraphs: string[]
  market_count: number
}

export type SelectionAnalysis = {
  symbol: string
  selected_protocol: string
  selected_subgraph: string
  best_rate: string
  selected_rate: string
  selected_tvl_usd: string
  competitive_market_count: number
}

export type Recommendation = {
  summary: string
  details: string[]
}

export type AnalyzeResponse = {
  wallet_address: string
  holdings: Holding[]
  opportunities: Opportunity[]
  protocol_analyses: ProtocolAnalysis[]
  selection_analyses: SelectionAnalysis[]
  recommendation: Recommendation
}