export function formatRate(value: string): string {
  const rate = Number(value)

  return `${rate.toFixed(2)}%`
}

export function formatUsd(value: string): string {
  const amount = Number(value)

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 2,
  }).format(amount)
}

export function getSelectionReason(
  bestRate: string,
  selectedRate: string,
  competitiveMarketCount: number,
): string {
  const best = Number(bestRate)
  const selected = Number(selectedRate)

  if (best === selected) {
    if (competitiveMarketCount > 1) {
      return (
        'This market had the best rate and was selected from ' +
        `${competitiveMarketCount} competitive markets.`
      )
    }

    return 'This market had the best eligible rate.'
  }

  return (
    'This market was within the allowed rate tolerance of the best rate ' +
    'and had the highest TVL among the competitive markets.'
  )
}