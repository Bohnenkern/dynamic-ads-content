import './UserTab.css'

const UserTab = ({ user, userResult, campaignResult }) => {
  if (!campaignResult) {
    return (
      <div className="user-tab">
        <div className="user-tab-content">
          <div className="empty-state">
            <div className="empty-icon">👤</div>
            <h2>{user?.name || 'User'}</h2>
            <p>Run a campaign first to see personalized ads</p>
          </div>
        </div>
      </div>
    )
  }

  if (!userResult) {
    return (
      <div className="user-tab">
        <div className="user-tab-content">
          <div className="empty-state">
            <div className="empty-icon">⚠️</div>
            <h2>No Results</h2>
            <p>This user was not targeted in the campaign</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="user-tab">
      <div className="user-header">
        <div className="user-info">
          <div className="user-avatar">
            {user?.name?.charAt(0) || '?'}
          </div>
          <div className="user-details">
            <h2>{user?.name || 'Unknown User'}</h2>
            <p className="user-meta">
              {user?.age} years • {user?.location} • {user?.demographics?.occupation}
            </p>
          </div>
        </div>
      </div>

      <div className="user-content">
        {/* Matched Interests */}
        <div className="section">
          <h3>🎯 Matched Interests</h3>
          <div className="interests-grid">
            {userResult.matched_interests?.map((interest, idx) => (
              <div key={idx} className="interest-card">
                <div className="interest-name">{interest.interest}</div>
                <div className="interest-trend">{interest.trend}</div>
                <div className="interest-score">Score: {interest.score}%</div>
              </div>
            ))}
          </div>
        </div>

        {/* Generated Images */}
        <div className="section">
          <h3>🖼️ Generated Ads ({userResult.images_count || 0})</h3>
          <div className="generated-ads-grid">
            {userResult.generated_images && userResult.generated_images.length > 0 ? (
              userResult.generated_images.map((image, idx) => (
                <div key={idx} className="ad-card">
                  {image.image_url ? (
                    <>
                      <div className="ad-image-container">
                        <img
                          src={image.image_url}
                          alt={`Ad for ${image.trend_category}`}
                          className="ad-image"
                        />
                        <div className="ad-overlay">
                          <span className="ad-status">✓ Generated</span>
                        </div>
                      </div>
                      <div className="ad-info">
                        <h4>{image.trend_category}</h4>
                        <p className="ad-prompt">{image.prompt_used?.substring(0, 100)}...</p>
                      </div>
                    </>
                  ) : (
                    <div className="ad-placeholder">
                      <div className="placeholder-icon">🎨</div>
                      <h4>{image.trend_category || 'Ad'}</h4>
                      <p>{image.message || 'Image generation in progress...'}</p>
                      <small>{image.status || 'pending'}</small>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="ad-placeholder">
                <div className="placeholder-icon">🎨</div>
                <p>No images generated for this user</p>
                <small>User may not have matched any filtered trends</small>
              </div>
            )}
          </div>
        </div>

        {/* Technical Details (Collapsible) */}
        <details className="section collapsible">
          <summary>
            <h3>🔧 Technical Details</h3>
          </summary>
          <div className="technical-details">
            <div className="detail-item">
              <h4>Generated Images</h4>
              <pre>{JSON.stringify(userResult.generated_images, null, 2)}</pre>
            </div>
          </div>
        </details>
      </div>
    </div>
  )
}

export default UserTab
