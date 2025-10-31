import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Group from "../image/Group.png"
import Steva from "../image/Steva.jpg"
type Props = {
  parentId: string;
};

function ProfileUpdate({ parentId }: Props) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    axios.get(`/api/v1/parents/${parentId}`)
      .then(res => {
        console.log('Fetched profile:', res.data);
        setFormData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading profile:', err);
        setError('Failed to load profile');
        setLoading(false);
      });
  }, [parentId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submitting update:', formData);

    axios.patch(`/api/v1/parents/${parentId}`, formData, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then(() => {
        alert('Profile updated successfully');
      })
      .catch(err => {
        console.error('Update failed:', err);
        alert('Failed to update profile. Please try again.');
      });
  };

  if (loading) return <p>Loading profile...</p>;
  if (error) return <p>{error}</p>;

  return (
    <>
    <form onSubmit={handleSubmit} className="profile-update-form">
      <div className="LoginUpper">
        <img style={{width:"230px", height:"auto", marginLeft:"30px"}} src={Steva} />
        <label style={{marginTop:"40px"}}>
          Name:
          <input
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Email:
          <input
            name="email"
            value={formData.email}
            onChange={handleChange}
            type="email"
            required
          />
        </label>
        <label>
          Phone:
          <input
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            type="tel"
            required
          />
        </label>
        <button style={{marginLeft:"32px"}} type="submit">Update Profile</button>
      </div>
    </form>

    <img className='CornerStyle' src={Group}/>
    
    
    
    </>
    
  );
}

export default ProfileUpdate;