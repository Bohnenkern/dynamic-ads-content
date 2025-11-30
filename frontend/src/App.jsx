import { useState, useEffect } from 'react'
import './App.css'
import TabNavigation from './components/TabNavigation'
import CampaignTab from './components/tabs/CampaignTab'
import UserTab from './components/tabs/UserTab'
import PreviewTab from './components/tabs/PreviewTab'
import { generateCampaign, getAllUsers } from './services/api'

function App() {
  const [activeTab, setActiveTab] = useState('campaign')
  const [uploadedImage, setUploadedImage] = useState(null)
  const [campaignResult, setCampaignResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [users, setUsers] = useState([])
  const [productDescription, setProductDescription] = useState('')
  const [campaignTheme, setCampaignTheme] = useState('')
  const [stylePreset, setStylePreset] = useState('highly_stylized')

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
    if (!uploadedImage || !productDescription || !campaignTheme) return

    setIsLoading(true)
    setError(null)

    try {
      const campaignData = {
        image: uploadedImage,
        product_description: productDescription,
        campaign_theme: campaignTheme,
        style_preset: stylePreset,
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
            productDescription={productDescription}
            setProductDescription={setProductDescription}
            campaignTheme={campaignTheme}
            setCampaignTheme={setCampaignTheme}
            stylePreset={stylePreset}
            setStylePreset={setStylePreset}
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
      case 'preview':
        return <PreviewTab campaignResult={campaignResult} />
      default:
        return (
          <CampaignTab
            uploadedImage={uploadedImage}
            onImageUpload={handleImageUpload}
            onRunCampaign={handleRunCampaign}
            productDescription={productDescription}
            setProductDescription={setProductDescription}
            campaignTheme={campaignTheme}
            setCampaignTheme={setCampaignTheme}
            stylePreset={stylePreset}
            setStylePreset={setStylePreset}
            campaignResult={campaignResult}
            isLoading={isLoading}
            error={error}
          />
        )
    }
  }

  return (
    <div className={`app ${activeTab === 'preview' ? 'preview-mode' : ''}`}>
      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
      <main className="app-content">
        {renderTabContent()}
      </main>
    </div>
  )
}

export default App
