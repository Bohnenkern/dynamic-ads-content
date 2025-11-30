import './TabNavigation.css'

const TabNavigation = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'campaign', label: 'Campaign', isPrimary: true },
    { id: 'user1', label: 'User 1', isPrimary: false },
    { id: 'user2', label: 'User 2', isPrimary: false },
    { id: 'user3', label: 'User 3', isPrimary: false },
    { id: 'user4', label: 'User 4', isPrimary: false },
    { id: 'user5', label: 'User 5', isPrimary: false },
    { id: 'preview', label: 'Preview', isPrimary: false },
  ]

  return (
    <nav className="tab-navigation">
      <div className="nav-content">
        <div className="nav-logo">
          OnPoint
        </div>
        <div className="tab-container">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab ${activeTab === tab.id ? 'active' : ''} ${
                tab.isPrimary ? 'primary' : ''
              }`}
              onClick={() => onTabChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="nav-actions"></div>
      </div>
    </nav>
  )
}

export default TabNavigation
