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
  campaignResult,
  isLoading,
  error
}) => {
  const isFormValid = uploadedImage && productDescription && campaignTheme

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
            placeholder="e.g., Samsung Galaxy S20 - Premium Smartphone with 5G, 64MP Camera, 120Hz Display"
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
            placeholder="e.g., Samsung S20 Launch Campaign"
            value={campaignTheme}
            onChange={(e) => setCampaignTheme(e.target.value)}
            disabled={isLoading}
          />
          <span className="form-hint">Name or theme for your marketing campaign</span>
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
