import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Steva from "../image/Steva.jpg"
import Group from "../image/Group.png"

function Confirmresetpassword() {
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post(`/auth/password-reset-confirm/${uid}/${token}/`, {
      password: newPassword
    })
      .then(() => {
        alert('Password reset successful');
        navigate('/'); // Redirect to login or home
      })
      .catch(err => alert('Failed to reset password'));
  };

  return (
    <>
    <div className='LoginUpper'>
        <img style={{width:"230px", height:"auto"}}src={Steva}/>
    <form onSubmit={handleSubmit}>
      <h2>Set New Password</h2>
      <div style={{display:"flex", flexDirection:"column"}}>
       <input
        type="password"
        name="password"
        placeholder="New password"
        value={newPassword}
        onChange={e => setNewPassword(e.target.value)}
        required
      />
      <button type="submit">Reset Password</button>
      </div>   
    </form>


    </div>
    
    <img className="CornerStyle"src={Group}/>
    
    
    </>
    
  );
}  export default Confirmresetpassword;