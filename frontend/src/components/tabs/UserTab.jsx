import './UserTab.css'

const UserTab = ({ user, userResult, campaignResult }) => {
  // Helper function to get age group in English
  const getAgeGroup = (age) => {
    if (age < 13) return 'Child'
    if (age < 20) return 'Teenager'
    if (age < 30) return 'Young Adult'
    if (age < 50) return 'Adult'
    if (age < 65) return 'Middle-Aged'
    return 'Senior'
  }

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

  // Get top 3 interests
  const topInterests = user?.interests?.slice(0, 3) || []

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
              {getAgeGroup(user?.age)} • {user?.location}
            </p>
          </div>
        </div>
      </div>

      <div className="user-content">
        {/* User Profile Card - Simplified to only essential info */}
        <div className="section">
          <h3>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width="24" height="24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Profile
          </h3>
          <div className="profile-grid">
            <div className="profile-item">
              <div className="profile-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                </svg>
              </div>
              <div className="profile-content">
                <div className="profile-label">Age Group</div>
                <div className="profile-value">{getAgeGroup(user?.age)}</div>
              </div>
            </div>

            <div className="profile-item">
              <div className="profile-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                </svg>
              </div>
              <div className="profile-content">
                <div className="profile-label">Location</div>
                <div className="profile-value">{user?.location}</div>
              </div>
            </div>

            <div className="profile-item">
              <div className="profile-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802" />
                </svg>
              </div>
              <div className="profile-content">
                <div className="profile-label">Language</div>
                <div className="profile-value">{user?.language?.toUpperCase()}</div>
              </div>
            </div>

            <div className="profile-item profile-item-wide">
              <div className="profile-icon">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11.48 3.499a.562.562 0 011.04 0l2.125 5.111a.563.563 0 00.475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 00-.182.557l1.285 5.385a.562.562 0 01-.84.61l-4.725-2.885a.563.563 0 00-.586 0L6.982 20.54a.562.562 0 01-.84-.61l1.285-5.386a.562.562 0 00-.182-.557l-4.204-3.602a.563.563 0 01.321-.988l5.518-.442a.563.563 0 00.475-.345L11.48 3.5z" />
                </svg>
              </div>
              <div className="profile-content">
                <div className="profile-label">Top 3 Interests</div>
                <div className="profile-value">{topInterests.join(', ')}</div>
              </div>
            </div>
          </div>
        </div>

        {/* Generated Images - One per Interest */}
        <div className="section">
          <h3>Generated Ads ({userResult.images_count || 0}/3)</h3>
          <div className="generated-ads-grid">
            {userResult.generated_images && userResult.generated_images.length > 0 ? (
              userResult.generated_images.map((image, idx) => (
                <div key={idx} className="ad-card">
                  {image.image_url ? (
                    <>
                      <div className="ad-image-container">
                        <img
                          src={image.image_url}
                          alt={`Ad for ${image.interest}`}
                          className="ad-image"
                        />
                      </div>
                      <div className="ad-info">
                        <h4>{image.interest}</h4>
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
                      <h4>{image.interest || 'Interest'}</h4>
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
                <small>Run a campaign to generate personalized ads</small>
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
