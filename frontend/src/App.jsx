import { useState } from 'react'
import './App.css'
import TabNavigation from './components/TabNavigation'
import CampaignTab from './components/tabs/CampaignTab'
import UserTab from './components/tabs/UserTab'

function App() {
  const [activeTab, setActiveTab] = useState('campaign')
  const [uploadedImage, setUploadedImage] = useState(null)

  const handleImageUpload = (file) => {
    setUploadedImage(file)
  }

  const handleRunCampaign = () => {
    if (uploadedImage) {
      console.log('Running campaign with image:', uploadedImage.name)
      // Hier später API-Call zum Backend
    }
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'campaign':
        return (
          <CampaignTab 
            uploadedImage={uploadedImage}
            onImageUpload={handleImageUpload}
            onRunCampaign={handleRunCampaign}
          />
        )
      case 'user1':
        return <UserTab userName="User 1" />
      case 'user2':
        return <UserTab userName="User 2" />
      case 'user3':
        return <UserTab userName="User 3" />
      case 'user4':
        return <UserTab userName="User 4" />
      case 'user5':
        return <UserTab userName="User 5" />
      default:
        return (
          <CampaignTab 
            uploadedImage={uploadedImage}
            onImageUpload={handleImageUpload}
            onRunCampaign={handleRunCampaign}
          />
        )
    }
  }

  return (
    <div className="app">
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="app-content">
        {renderTabContent()}
      </main>
    </div>
  )
}

export default App
