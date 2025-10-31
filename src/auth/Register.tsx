import Steva from "../image/Steva.jpg";
import { Navigate, useNavigate } from "react-router-dom";
import "./Register.css";
import Group from "../image/Group.png"
   import axios from 'axios';
import { useState } from 'react';


   

function Register() {
     
    const navigate= useNavigate();
     
  const [formData, setFormData] = useState({
     email: '',
    first_name: '',
    last_name: '', 
    phone_number: '',
    password: '',
    confirm_password: '',
    role: 'parent'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password != formData.confirm_password){
      alert("Passwords dont match");
       return;
    }
        


    console.log("Submitting form data:", formData);
    axios.post('https://8463b2433bf0.ngrok-free.app/api/v1/auth/register/',  formData, {
  headers: {
    'Content-Type': 'application/json',
     'Accept': 'application/json',
    'ngrok-skip-browser-warning': 'true'
  }


})
      .then(() => {
         alert('Registration successful');
       navigate("/VerifySuccess"); 
  })
      .catch(err => {
  console.error('Full error:', err);
  console.error('Response data:', err.response?.data);
  alert(`Registration failed: ${JSON.stringify(err.response?.data?.errors || err.response?.data || 'Please try again.')}`);
});
      

    
  };



    return(
        <>

        <div className="LoginUpper">
            <img style={{width:"200px", borderRadius:"10px", height:"auto"}} src={Steva} />
        <h1 style={{marginTop:"7px"}}>Create account</h1>
        <p>Please fill in the details below</p>

     <form onSubmit={handleSubmit}>
         <div className="Entries">
        <input type="email" name="email" value={formData.email} onChange={handleChange}   placeholder="Email"/>
        <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} placeholder="FirstName"/>
        <input type="text" name="last_name" value={formData.last_name} onChange={handleChange}    placeholder="Surname"/>
        <input type="tel" name="phone_number" value={formData.phone_number} onChange={handleChange} placeholder="phonenumber" />
      
        <input type="password" name="password" value={formData.password} onChange={handleChange}  placeholder="Password"/>
        <input type="password" name="confirm_password" value={formData.confirm_password} onChange={handleChange} placeholder="Confirm Password" />

     </div>
    
    
         <p>By Clicking Register you agree to the <span>terms</span> and <span>conditions</span></p>

         <div className="divider">
            <div className="line"></div>
                <p>or sign up with</p>
            <div className="line"></div>
         </div>

         <button className="Register-btn" type="submit"> Register</button> 
   </form>
         <div className="lower-btns">
           <img src="https://tse2.mm.bing.net/th/id/OIP.jYUEQ5iDArrERw6TrwY5xwHaHk?r=0&rs=1&pid=ImgDetMain&o=7&rm=3"/> 
           <img src="https://i.pinimg.com/originals/65/22/5a/65225ab6d965e5804a632b643e317bf4.jpg"/> 
           <img src="https://th.bing.com/th/id/OIP.VgfWevmVdjRKHG8bfhpVsgHaHa?r=0&o=7rm=3&rs=1&pid=ImgDetMain&o=7&rm=3"/>

          </div>

          <p style={{fontSize:"12px", color: "#000000"}}>Already have an account? <span><a href="/">Login</a></span></p>
        </div>

           <img className="CornerStyle" style ={{}}src={Group}/>
       
        </>

    )
  }

export default Register;