export async function predict(file) {
  const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  const url = `${base.replace(/\/$/, '')}/predict`
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(url, {
    method: 'POST',
    body: fd,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed with ${res.status}`)
  }
  const data = await res.json()
  const disease =
    data.disease ??
    data.label ??
    data.class ??
    data.prediction ??
    'Unknown'
  let confidence =
    data.confidence ??
    data.score ??
    data.prob ??
    data.probability
  if (Array.isArray(data.confidences)) {
    confidence = Math.max(...data.confidences)
  }
  if (typeof confidence !== 'number') {
    confidence = Number(confidence)
  }
  if (!Number.isFinite(confidence)) {
    confidence = 0
  }
  let recommendations =
    data.recommendations ??
    data.remedies ??
    data.tips ??
    data.suggestions ??
    []
  if (typeof recommendations === 'string') {
    recommendations = recommendations.split(/\r?\n/).filter(Boolean)
  }
  return {
    disease,
    confidence,
    recommendations,
    raw: data,
  }
}
