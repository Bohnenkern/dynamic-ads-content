import ImageUpload from '../ImageUpload'
import './CampaignTab.css'

const CampaignTab = ({ uploadedImage, onImageUpload, onRunCampaign }) => {
  return (
    <div className="campaign-tab">
      <div className="campaign-header">
        <h1>Campaign Management</h1>
        <p>Upload your campaign image to get started</p>
      </div>

      <div className="campaign-content">
        <ImageUpload 
          uploadedImage={uploadedImage}
          onImageUpload={onImageUpload} 
        />

        {uploadedImage && (
          <div className="campaign-actions">
            <button className="run-campaign-button" onClick={onRunCampaign}>
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
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default CampaignTab
