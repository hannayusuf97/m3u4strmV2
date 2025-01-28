import React, { useState } from 'react';
import { Sidenav, Nav } from 'rsuite';
import 'rsuite/dist/rsuite.min.css'; // Import RSuite styles
import '../css/AdminSettings.css'; // Import custom styles
import M3UManagement from './M3UManagement';
import ProviderManagement from './ProviderManagement';


const AdminSettings = () => {
  // State to track the selected tab
  const [activeKey, setActiveKey] = useState('1'); // Default to the first tab

  const handleSelect = (eventKey) => {
    setActiveKey(eventKey); // Update the selected tab
  };

  // Define content for each tab
  const renderContent = () => {
    switch (activeKey) {
      case '1':
        return <M3UManagement/>;
      case '2':
        return <ProviderManagement/>;
      case '3':
        return <p>General Settings: Change Admin password, and set paths.</p>;
      default:
        return <p>Select an option from the side navigation to view details.</p>;
    }
  };

  return (
    <div className="admin-settings-container">
      <Sidenav
        defaultOpenKeys={['1']}
        style={{ width: 250 }}
        appearance="subtle"
        className="custom-sidenav"
      >
        <Sidenav.Header>
          <div className="logo">Admin Panel</div>
        </Sidenav.Header>
        <Sidenav.Body>
          <Nav
            activeKey={activeKey} // Bind activeKey to the current state
            onSelect={handleSelect} // Handle tab selection
            className="custom-nav"
          >
            <Nav.Item eventKey="1" className={`nav-item ${activeKey === '1' ? 'selected' : ''}`}>
              M3U Management
            </Nav.Item>
            <Nav.Item eventKey="2" className={`nav-item ${activeKey === '2' ? 'selected' : ''}`}>
              Provider Management
            </Nav.Item>
            <Nav.Item eventKey="3" className={`nav-item ${activeKey === '3' ? 'selected' : ''}`}>
              General Settings
            </Nav.Item>
          </Nav>
        </Sidenav.Body>
      </Sidenav>
      <div className="content">
        <h2>{activeKey === '1' ? 'M3U Management' : activeKey === '2' ? 'Provider Management' : 'General Settings'}</h2>
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminSettings;
