import './UserTab.css'

const UserTab = ({ userName }) => {
  return (
    <div className="user-tab">
      <div className="user-tab-content">
        <div className="empty-state">
          <div className="empty-icon">👤</div>
          <h2>{userName}</h2>
          <p>This section is coming soon</p>
        </div>
      </div>
    </div>
  )
}

export default UserTab
