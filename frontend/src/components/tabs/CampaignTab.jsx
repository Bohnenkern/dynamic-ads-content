import ImageUpload from '../ImageUpload'
import './CampaignTab.css'

const CampaignTab = ({
  uploadedImage,
  onImageUpload,
  onRunCampaign,
  productDescription,
  setProductDescription,
  campaignTheme,
  setCampaignTheme,
  stylePreset,
  setStylePreset,
  campaignResult,
  isLoading,
  error
}) => {
  const isFormValid = uploadedImage && productDescription && campaignTheme

  const getStyleLabel = (value) => {
    switch(value) {
      case 'realistic': return 'Realistic'
      case 'semi_realistic': return 'Semi-Realistic'
      case 'highly_stylized': return 'Highly Stylized'
      default: return 'Highly Stylized'
    }
  }

  return (
    <div className="campaign-tab">
      <div className="campaign-header">
        <h1>Campaign Management</h1>
        <p>Configure your campaign settings and upload an image</p>
      </div>

      {/* Campaign Configuration Form */}
      <div className="campaign-form">
        <div className="form-group">
          <label htmlFor="productDescription">
            <span className="label-text">Product Description</span>
            <span className="label-required">*</span>
          </label>
          <textarea
            id="productDescription"
            className="form-textarea"
            value={productDescription}
            onChange={(e) => setProductDescription(e.target.value)}
            rows={3}
            disabled={isLoading}
          />
          <span className="form-hint">Describe the product you want to advertise</span>
        </div>

        <div className="form-group">
          <label htmlFor="campaignTheme">
            <span className="label-text">Campaign Theme</span>
            <span className="label-required">*</span>
          </label>
          <input
            id="campaignTheme"
            type="text"
            className="form-input"
            value={campaignTheme}
            onChange={(e) => setCampaignTheme(e.target.value)}
            disabled={isLoading}
          />
          <span className="form-hint">Name or theme for your marketing campaign</span>
        </div>

        <div className="form-group">
          <label htmlFor="stylePreset">
            <span className="label-text">Visual Style</span>
            <span className="label-value">{getStyleLabel(stylePreset)}</span>
          </label>
          <div className="style-slider-container">
            <input
              id="stylePreset"
              type="range"
              min="0"
              max="2"
              step="1"
              className="style-slider"
              value={stylePreset === 'realistic' ? 0 : stylePreset === 'semi_realistic' ? 1 : 2}
              onChange={(e) => {
                const val = parseInt(e.target.value)
                if (val === 0) setStylePreset('realistic')
                else if (val === 1) setStylePreset('semi_realistic')
                else setStylePreset('highly_stylized')
              }}
              disabled={isLoading}
            />
            <div className="style-labels">
              <span className={stylePreset === 'realistic' ? 'active' : ''}>Realistic</span>
              <span className={stylePreset === 'semi_realistic' ? 'active' : ''}>Semi</span>
              <span className={stylePreset === 'highly_stylized' ? 'active' : ''}>Stylized</span>
            </div>
          </div>
          <span className="form-hint">Choose the artistic level of the generated images</span>
        </div>
      </div>

      <div className="campaign-content">
        <ImageUpload
          uploadedImage={uploadedImage}
          onImageUpload={onImageUpload}
        />

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
              />
            </svg>
            <div>
              <h4>Campaign Generation Failed</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Success Display */}
        {campaignResult && !isLoading && (
          <div className="success-message">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h4>Campaign Generated Successfully!</h4>
              <p>
                {campaignResult.images_generated} images generated for {campaignResult.users_targeted} users
                <br />
                <small>Check the user tabs to see personalized ads</small>
              </p>
            </div>
          </div>
        )}

        {/* Campaign Actions */}
        <div className="campaign-actions">
          <button
            className="run-campaign-button"
            onClick={onRunCampaign}
            disabled={isLoading || !isFormValid}
          >
            {isLoading ? (
              <>
                <div className="spinner"></div>
                Generating Campaign...
              </>
            ) : (
              <>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z"
                  />
                </svg>
                Run Campaign
              </>
            )}
          </button>
          {!isFormValid && (
            <p className="validation-hint">
              Please fill in all required fields and upload an image
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default CampaignTab
