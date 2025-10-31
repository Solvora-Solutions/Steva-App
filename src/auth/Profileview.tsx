import { useState, useEffect } from "react";
import axios from 'axios';


function Profileview({ parentId }: { parentId: string }) {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    axios.get(`/api/v1/parents/${parentId}`)
      .then(res => setProfile(res.data))
      .catch(err => console.error('Error fetching profile:', err));
  }, [parentId]);

  return (
    <div className="LoginUpper">

   
    <div className="profile-view">
      <h2>Parent Profile</h2>
      {profile ? (
        <ul>
          <li><strong>Name:</strong> {profile.name}</li>
          <li><strong>Email:</strong> {profile.email}</li>
          <li><strong>Phone:</strong> {profile.phone}</li>
          {/* Add more fields as needed */}
        </ul>
      ) : (
        <p>Loading...</p>
      )}
    </div>
     </div>
  );
}

export default Profileview;