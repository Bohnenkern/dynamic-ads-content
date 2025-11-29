import ImageUpload from '../ImageUpload'
import './CampaignTab.css'

const CampaignTab = ({
  uploadedImage,
  onImageUpload,
  onRunCampaign,
  campaignConfig,
  campaignResult,
  isLoading,
  error
}) => {
  return (
    <div className="campaign-tab">
      <div className="campaign-header">
        <h1>Campaign Management</h1>
        <p>Upload your campaign image to get started</p>
      </div>

      {/* Campaign Configuration Info */}
      <div className="campaign-info">
        <div className="info-card">
          <div className="info-icon">📱</div>
          <div className="info-content">
            <h3>Product</h3>
            <p>{campaignConfig.product_description}</p>
          </div>
        </div>
        <div className="info-card">
          <div className="info-icon">🎯</div>
          <div className="info-content">
            <h3>Campaign Theme</h3>
            <p>{campaignConfig.campaign_theme}</p>
          </div>
        </div>
        <div className="info-card">
          <div className="info-icon">✨</div>
          <div className="info-content">
            <h3>Company Values</h3>
            <p>{campaignConfig.company_values.join(', ')}</p>
          </div>
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
        {uploadedImage && (
          <div className="campaign-actions">
            <button
              className="run-campaign-button"
              onClick={onRunCampaign}
              disabled={isLoading}
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
          </div>
        )}
      </div>
    </div>
  )
}

export default CampaignTab
