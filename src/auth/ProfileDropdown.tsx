import React, { useState, useRef, useEffect } from 'react';
import Vector from '../image/Vector.png';

function ProfileDropdown({ onViewProfile, onUpdateProfile }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e : MouseEvent) => {
      if (dropdownRef.current && e.target instanceof Node && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
      <div className='Top'>

    
       <div style={{ position: 'relative' }} ref={dropdownRef}>
      <img
        src={Vector}
        alt="Profile"
        style={{ cursor: 'pointer', width: '20px', height: '20px' }}
        onClick={() => { console.log("Image Clicked"); setOpen(prev => !prev)} }
        
      />

      {open && (
        <div style={{
          position: 'absolute',
          top: '40px',
          right: 0,
          backgroundColor: '#fff',
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          zIndex: 1000,
          minWidth: '160px',
          alignItems: 'center',
          textAlign: 'center'
        }}>
          <button onClick={onViewProfile} style={menuItemStyle}>👤 View Profile</button>
          <button onClick={onUpdateProfile} style={menuItemStyle}>✏️ Update Profile</button>
        </div>
      )}
    </div>
      </div>
  );
}

const menuItemStyle: React.CSSProperties = {
  display: 'block',
  width: '100%',
  padding: '10px',
  background: 'none',
  border: 'none',
  textAlign: 'left',
  cursor: 'pointer',
  fontSize: '14px'
};

export default ProfileDropdown;