import { useState, useEffect } from 'react'
import './App.css'
import TabNavigation from './components/TabNavigation'
import CampaignTab from './components/tabs/CampaignTab'
import UserTab from './components/tabs/UserTab'
import { generateCampaign, getAllUsers } from './services/api'

// Samsung S20 Campaign Configuration
const CAMPAIGN_CONFIG = {
  product_description: 'Samsung Galaxy S20 - Premium Smartphone with 5G, 64MP Camera, 120Hz Display',
  campaign_theme: 'Samsung S20 Launch Campaign',
  company_values: ['innovative', 'premium', 'technology-focused', 'modern']
}

function App() {
  const [activeTab, setActiveTab] = useState('campaign')
  const [uploadedImage, setUploadedImage] = useState(null)
  const [campaignResult, setCampaignResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [users, setUsers] = useState([])

  // Load users on mount
  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await getAllUsers()
      setUsers(data.users || [])
    } catch (err) {
      console.error('Failed to load users:', err)
    }
  }

  const handleImageUpload = (file) => {
    setUploadedImage(file)
    // Reset previous results when new image is uploaded
    setCampaignResult(null)
    setError(null)
  }

  const handleRunCampaign = async () => {
    if (!uploadedImage) return

    setIsLoading(true)
    setError(null)

    try {
      const campaignData = {
        image: uploadedImage,
        product_description: CAMPAIGN_CONFIG.product_description,
        campaign_theme: CAMPAIGN_CONFIG.campaign_theme,
        company_values: CAMPAIGN_CONFIG.company_values
      }

      console.log('Starting campaign generation...', campaignData)
      const result = await generateCampaign(campaignData)
      console.log('Campaign generated successfully:', result)

      setCampaignResult(result)
      setError(null)
    } catch (err) {
      console.error('Campaign generation failed:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate campaign')
      setCampaignResult(null)
    } finally {
      setIsLoading(false)
    }
  }

  const getUserResult = (userId) => {
    if (!campaignResult?.results) return null
    return campaignResult.results.find(r => r.user_id === userId)
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'campaign':
        return (
          <CampaignTab
            uploadedImage={uploadedImage}
            onImageUpload={handleImageUpload}
            onRunCampaign={handleRunCampaign}
            campaignConfig={CAMPAIGN_CONFIG}
            campaignResult={campaignResult}
            isLoading={isLoading}
            error={error}
          />
        )
      case 'user1':
        return (
          <UserTab
            user={users[0]}
            userResult={getUserResult(1)}
            campaignResult={campaignResult}
          />
        )
      case 'user2':
        return (
          <UserTab
            user={users[1]}
            userResult={getUserResult(2)}
            campaignResult={campaignResult}
          />
        )
      case 'user3':
        return (
          <UserTab
            user={users[2]}
            userResult={getUserResult(3)}
            campaignResult={campaignResult}
          />
        )
      case 'user4':
        return (
          <UserTab
            user={users[3]}
            userResult={getUserResult(4)}
            campaignResult={campaignResult}
          />
        )
      case 'user5':
        return (
          <UserTab
            user={users[4]}
            userResult={getUserResult(5)}
            campaignResult={campaignResult}
          />
        )
      default:
        return (
          <CampaignTab
            uploadedImage={uploadedImage}
            onImageUpload={handleImageUpload}
            onRunCampaign={handleRunCampaign}
            campaignConfig={CAMPAIGN_CONFIG}
            campaignResult={campaignResult}
            isLoading={isLoading}
            error={error}
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
