import './UserTab.css'

const UserTab = ({ user, userResult, campaignResult }) => {
  if (!campaignResult) {
    return (
      <div className="user-tab">
        <div className="user-tab-content">
          <div className="empty-state">
            <div className="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
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
            <div className="empty-icon">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </div>
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
          <h3>Matched Interests</h3>
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
          <h3>Generated Ads ({userResult.images_count || 0})</h3>
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
                          <span className="ad-status">Generated</span>
                        </div>
                      </div>
                      <div className="ad-info">
                        <h4>{image.trend_category}</h4>
                        <p className="ad-prompt">{image.prompt_used?.substring(0, 100)}...</p>
                      </div>
                    </>
                  ) : (
                    <div className="ad-placeholder">
                      <div className="placeholder-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                        </svg>
                      </div>
                      <h4>{image.trend_category || 'Ad'}</h4>
                      <p>{image.message || 'Image generation in progress...'}</p>
                      <small>{image.status || 'pending'}</small>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="ad-placeholder">
                <div className="placeholder-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                  </svg>
                </div>
                <p>No images generated for this user</p>
                <small>User may not have matched any filtered trends</small>
              </div>
            )}
          </div>
        </div>

        {/* Technical Details (Collapsible) */}
        <details className="section collapsible">
          <summary>
            <h3>Technical Details</h3>
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
