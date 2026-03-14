import { useEffect, useMemo, useState } from 'react'
import { predict } from '../lib/api'
import './HomePage.css'

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [error, setError] = useState('')
  const [view, setView] = useState('upload')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [apiError, setApiError] = useState('')

  const SUGGESTIONS = {
    Healthy: ['No action needed', 'Monitor plant regularly', 'Maintain proper nutrition'],
    'Bacterial Blight': [
      'Remove and destroy infected leaves',
      'Use copper-based bactericide as directed',
      'Avoid overhead irrigation',
    ],
    'Curl Virus': [
      'Control vector insects (e.g., whiteflies)',
      'Remove heavily infected plants',
      'Use virus-free planting material',
    ],
    'Fusarium Wilt': [
      'Improve soil drainage',
      'Rotate with non-host crops',
      'Use resistant varieties',
      'Disinfect tools regularly',
    ],
    Default: [
      'Isolate infected plants',
      'Improve field hygiene and sanitation',
      'Avoid wetting foliage when watering',
    ],
  }

  const previewUrl = useMemo(() => {
    if (!selectedFile) return ''
    return URL.createObjectURL(selectedFile)
  }, [selectedFile])

  useEffect(() => {
    if (!previewUrl) return

    return () => {
      URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handleFile = (file) => {
    setError('')

    if (!file) {
      setSelectedFile(null)
      return
    }

    const isImage = file.type?.startsWith('image/')
    if (!isImage) {
      setSelectedFile(null)
      setError('Please upload an image file (JPG, PNG, etc.).')
      return
    }

    const maxBytes = 8 * 1024 * 1024
    if (file.size > maxBytes) {
      setSelectedFile(null)
      setError('Image is too large. Please upload a file up to 8 MB.')
      return
    }

    setSelectedFile(file)
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setView('result')
    setLoading(true)
    setResult(null)
    setApiError('')
    try {
      const data = await predict(selectedFile)
      setResult({
        disease: data.disease,
        confidence: data.confidence,
        recommendations: Array.isArray(data.recommendations) ? data.recommendations : [],
      })
    } catch (e) {
      setApiError(e.message || 'Failed to analyze image')
    } finally {
      setLoading(false)
    }
  }

  const handleBack = () => {
    setView('upload')
  }

  return (
    <div className="homepage">
      <header className="homepage__header">
        <div className="homepage__container homepage__headerInner">
          <div className="brand">
            <div className="brand__logo" aria-hidden="true">
              CD
            </div>
            <div className="brand__text">
              <div className="brand__title">Cotton Disease Detection</div>
              <div className="brand__subtitle">Leaf image-based screening</div>
            </div>
          </div>

          <a className="btn btn--primary" href="#upload">
            Upload leaf image
          </a>
        </div>
      </header>

      <main className="homepage__container homepage__main">
        <section className="heroGrid">
          <div className="hero">
            <h1 className="hero__title">Detect cotton diseases early with a leaf photo</h1>
            <p className="hero__subtitle">
              {/* Upload a clear image of a leaf to get an instant screening. This is a landing page UI —
              you can connect the "Analyze" button to your model/API next. */}
            </p>

            <div className="featureGrid">
              <div className="featureCard">
                <div className="featureCard__title">Fast</div>
                <div className="featureCard__text">Quick upload and preview</div>
              </div>
              <div className="featureCard">
                <div className="featureCard__title">Simple</div>
                <div className="featureCard__text">Works on mobile and desktop</div>
              </div>
              <div className="featureCard">
                <div className="featureCard__title">Actionable</div>
                <div className="featureCard__text">Add remedy tips after prediction</div>
              </div>
            </div>
          </div>

          <section id="upload" className="uploadCard">
            <div className="uploadCard__top">
              <div>
                <h2 className="uploadCard__title">Upload leaf image</h2>
                <p className="uploadCard__subtitle">Use a well-lit photo and keep the leaf centered.</p>
              </div>

              {selectedFile ? (
                <button type="button" onClick={() => handleFile(null)} className="btn btn--secondary">
                  Remove
                </button>
              ) : null}
            </div>

            <div className="uploadCard__body">
              <div className="mobileActions" aria-label="Mobile image upload actions">
                <label className="btn btn--primary mobileActions__btn" htmlFor="leaf-image-capture">
                  Capture image
                </label>
                <input
                  id="leaf-image-capture"
                  name="leaf-image-capture"
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="mobileActions__input"
                  onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                />

                <label className="btn btn--secondary mobileActions__btn" htmlFor="leaf-image-upload">
                  Upload image
                </label>
                <input
                  id="leaf-image-upload"
                  name="leaf-image-upload"
                  type="file"
                  accept="image/*"
                  className="mobileActions__input"
                  onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                />
              </div>

              <label htmlFor="leaf-image" className="dropzone">
                <input
                  id="leaf-image"
                  name="leaf-image"
                  type="file"
                  accept="image/*"
                  className="dropzone__input"
                  onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
                />

                {selectedFile ? (
                  <div className="dropzone__content">
                    <div className="preview">
                      <img src={previewUrl} alt="Selected leaf preview" className="preview__image" />
                    </div>
                    <div className="fileMeta">
                      <div className="fileMeta__name">{selectedFile.name}</div>
                      <div className="fileMeta__hint">
                        Click to replace the image •{' '}
                        <a href={previewUrl} target="_blank" rel="noreferrer">View full size</a>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="dropzone__content">
                    <div className="dropzone__title">Click to upload</div>
                    <div className="dropzone__hint">PNG, JPG up to 8 MB</div>
                  </div>
                )}
              </label>

              {error ? <div className="alert">{error}</div> : null}

              <button
                type="button"
                disabled={!selectedFile}
                onClick={handleAnalyze}
                className="btn btn--analyze"
              >
                Analyze
              </button>
              <p className="uploadCard__note">
                We don’t upload anything yet — connect this to your backend/model when ready.
              </p>
            </div>
          </section>
        </section>

        {view === 'result' ? (
          <section className="heroGrid" style={{ marginTop: '1rem' }}>
            <div className="hero">
              <h2 className="hero__title">Analysis</h2>
              <p className="hero__subtitle">Screening result based on your uploaded leaf image.</p>

              <div className="featureGrid">
                <div className="featureCard">
                  <div className="featureCard__title">Disease</div>
                  <div className="featureCard__text analysis__value analysis__value--disease">
                    {loading ? 'Analyzing…' : result ? result.disease : '—'}
                  </div>
                </div>
                <div className="featureCard">
                  <div className="featureCard__title">Accuracy</div>
                  <div className="featureCard__text analysis__value analysis__value--confidence">
                    {result ? `${(result.confidence * 100).toFixed(2)}%` : '—'}
                  </div>
                </div>
              </div>

              {apiError ? <div className="alert">{apiError}</div> : null}

              {!loading && result ? (
                <div style={{ marginTop: '1rem' }}>
                  <div className="featureCard">
                    <div className="featureCard__title">Suggested Actions</div>
                    <div className="featureCard__text">
                      <ul className="analysis__list">
                        {(result.recommendations && result.recommendations.length
                          ? result.recommendations
                          : SUGGESTIONS[result.disease] || SUGGESTIONS.Default
                        ).map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ) : null}

              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                <button type="button" className="btn btn--secondary" onClick={handleBack}>
                  Back
                </button>
                <label className="btn btn--primary" htmlFor="replace-image">
                  Replace image
                </label>
                <input
                  id="replace-image"
                  name="replace-image"
                  type="file"
                  accept="image/*"
                  style={{ position: 'absolute', width: 1, height: 1, opacity: 0, pointerEvents: 'none' }}
                  onChange={(e) => {
                    const f = e.target.files?.[0] ?? null
                    handleFile(f)
                    if (f) {
                      setView('upload')
                    }
                  }}
                />
              </div>
            </div>

            <section className="uploadCard">
              <div className="preview">
                {selectedFile ? (
                  <img src={previewUrl} alt="Selected leaf" className="preview__image" />
                ) : (
                  <img src={previewUrl} alt="" className="preview__image" />
                )}
              </div>
              <div className="fileMeta">
                <div className="fileMeta__name">{selectedFile?.name ?? 'No image selected'}</div>
                <div className="fileMeta__hint">
                  {loading ? 'Processing…' : 'Analysis summary shown on the left'}{' '}
                  {previewUrl ? (
                    <>
                      • <a href={previewUrl} target="_blank" rel="noreferrer">View full size</a>
                    </>
                  ) : null}
                </div>
              </div>
            </section>
          </section>
        ) : null}

        <footer className="footer">
          <div className="footer__inner">
            <div>© {new Date().getFullYear()} Crop Disease Detection</div>
            <div className="footer__hint">Built with React + Vite + Tailwind</div>
          </div>
        </footer>
      </main>
    </div>
  )
}
