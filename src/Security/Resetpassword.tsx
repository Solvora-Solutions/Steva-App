import Steva from "../image/Steva.jpg"
import Group  from "../image/Group.png"
import "./Resetpassword.css"
import { useState } from "react"

     import axios from 'axios';

     

function Resetpassword() {
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    axios.post('/auth/password-reset/', { email })
      .then(() => alert('Reset link sent to your email'))
      .catch(err => alert('Failed to send reset link'));
  };

  return (
    <>
    <div className="LoginUpper">
     <img style={{width:"250px", height:"auto", marginTop:"30px"}} src={Steva}/>
    <form onSubmit={handleSubmit}>
      <h2>Reset Your Password</h2>
      <div style={{display:"flex", flexDirection:"column"}}>
       <input
        type="email"
        name="email"
        placeholder="Enter your email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />
      <button type="submit">Send Reset Link</button>
      </div>
      
    </form>
    </div>
      <img className="CornerStyle" src={Group}/>
    </>
    

        
  );
}




  
export default Resetpassword;