import {Navigate, useNavigate} from "react-router-dom";
import Steva from "../image/Steva.jpg";
import "./Signup.css";
import Group from "../image/Group.png"
import Facebook from "../image/Facebook.jpg"
import apple from "../image/apple.jpg"
import google from "../image/google.png"
import { useState } from "react";
import { BASE_URL } from '../config';
function Signup(){

  const [email, setEmail]= useState("");
  const [password, setPassword] = useState("");

async function LoginUser(credentials : {email: string, password : string}){
      const response = await fetch(`${BASE_URL}/api/v1/auth/login/`, {
        method : 'POST',
        headers : { 'Content-Type' : 'application/json' },
        body : JSON.stringify({credentials,
          email: credentials.email,
          password: credentials.password,
          type:"email"
        }),
      } );

     
           const data = await response.json();
           console.log("Login response :", data);

            if(!response.ok) throw new Error(data.detail || 'Login Failed');

           localStorage.setItem('accessToken', data.access);
           localStorage.setItem('refreshToken', data.refresh);
  }
  const navigate = useNavigate ();
      const nexthomepage = async () => {
  console.log("Login clicked")

  try{
    await LoginUser({ email, password})
     navigate("/Homepage");
  }
    catch(error){
      console.log("Login failed:",  error)
      alert("Login Failed. Please check your email and password");
    }

    }

    


    return(
        <>
       
        <div className="LoginUpper">
             <img className="Steva-img" src={Steva}/>
             <div className="TextWrapper">
               <h1 style={{marginTop:"4px", marginLeft:"-70px", marginBottom:"7px"}} className="alignedtext">Login account</h1>
               <p style={{fontSize:"13px", color:"black", marginLeft:"-60px"}} className="alignedtext"> Please enter login details below </p>
             </div>

           <div className="Entries">
            <input type="email" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)}/>
            <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}/>
           </div>  
            
       
             <div className="options">
                <div style={{textWrap:"nowrap", display: "flex",flexDirection:"row", alignItems: "center"}}>
                 <input type="checkbox" />
                 <p style={{marginTop: "-5px"}}>Remember me</p>
                </div>
                <div>
                  <p style={{marginTop: "4px"}}>Forgotten password?</p>
                 </div>
           </div>

             <div style={{marginTop: "10px"}}>
                <p style={{color: "#000000"}}>By clicking Login you agree to our  <span> terms</span> and <span>Conditions</span></p>
            </div>
      
        <button type="button" className="Login-btn" onClick={nexthomepage}>Log in</button>

           <div className="divider">
               <div className="line"></div>
                   <p>or Login with</p>
               <div className="line"></div>
            </div> 

          <div className="lower-btns">
           <a href="/auth/login/google-oauth2/">
             <img style={{cursor:"pointer"}} src={google}/> 
           </a>
           
           <img style={{cursor:"pointer"}} src={apple}/> 

           <div className="facebook-wrapper">
              <img style={{cursor:"pointer"}} className="facebook" src={Facebook}/>
           </div>
          

          </div>
          
            <p style={{fontSize:"12px", color: "#000000"}}>Don't have an account? <span style={{color:"#F24900"}}><a href="/Register">Register</a></span></p>
           
             <p style={{fontSize:"12px"}}><a href="/Forgotpassword">Forgot Password</a></p>
        </div>

        

        <img className="CornerStyle" style ={{}}src={Group}/>

    
        

        
        </>
    

    )
   
}
export default Signup;