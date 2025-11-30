import React from 'react';
import './PreviewTab.css';

const PreviewTab = ({ campaignResult }) => {
  const previewData = campaignResult?.preview_formats;

  const CartoonLines = ({ count = 3 }) => (
    <div className="cartoon-text-block">
      {[...Array(count)].map((_, i) => {
        // Generate a stable pseudo-random width between 30% and 98%
        // Using prime multipliers to create an irregular pattern
        const width = 30 + ((i * 47 + 19) % 69);
        // Vary opacity slightly for texture
        const opacity = 0.5 + ((i * 13) % 5) / 10;
        
        return (
          <div 
            key={i} 
            className="cartoon-line"
            style={{ 
              width: `${width}%`,
              opacity: opacity
            }}
          />
        );
      })}
    </div>
  );

  return (
    <div className="preview-tab">
      {previewData ? (
        <>
          <div className="preview-header">
            <h2 style={{color: '#888', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '2px'}}>
              Campaign Preview for: {previewData.user_name}
            </h2>
            <div className="preview-banner-container">
              {previewData.banner?.image_url ? (
                <img src={previewData.banner.image_url} alt="Banner Ad" className="preview-banner-img" />
              ) : (
                <div style={{padding: '20px', color: '#666'}}>Banner Generation Failed</div>
              )}
            </div>
          </div>

          <div className="preview-content">
            <div className="preview-left">
              <CartoonLines count={12} />
              <div className="preview-rect-container">
                {previewData.rectangular?.image_url ? (
                  <img src={previewData.rectangular.image_url} alt="Rectangular Ad" className="preview-rect-img" />
                ) : (
                  <div style={{padding: '20px', color: '#666'}}>Rectangular Generation Failed</div>
                )}
              </div>
              <CartoonLines count={15} />
            </div>

            <div className="preview-right">
              <div className="preview-vertical-container">
                {previewData.vertical?.image_url ? (
                  <img src={previewData.vertical.image_url} alt="Vertical Ad" className="preview-vertical-img" />
                ) : (
                  <div style={{padding: '20px', color: '#666'}}>Vertical Generation Failed</div>
                )}
              </div>
              <CartoonLines count={20} />
            </div>
          </div>
        </>
      ) : (
        <div style={{color: '#666', marginTop: '50px'}}>
          No preview data available. Please run a campaign first.
        </div>
      )}
    </div>
  );
};

export default PreviewTab;
