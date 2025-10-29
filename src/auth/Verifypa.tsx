import { Navigate, useNavigate } from "react-router-dom";
import Verify from "../image/Verify.png";
import "./Verify.css";
import Group from "../image/Group.png"
import icon from "../image/icon.png"

function Verifypage(){
     const navigate = useNavigate();
     const VeriSuccess = () => {
        navigate("/VerifySuccess");
     }
 
    return(
        <>
        <div className= "LoginUpper">
        <img style={{width: "200px", height:"200px"}} src={Verify}/>

        <p>Please enter your ward's students ID to verify and link </p>
        <p>them to your account</p>
           
           <div className="Entries">
             <input type="number" placeholder="Enter Student ID"/>
                </div>
            
            <div className="ButtonWrapper">
        <button className="Verify-btn" onClick={VeriSuccess} >
                Verify <img className="iconimg" src={icon}/>
        </button>

            </div>
       
        

           <img className="CornerStyle" src={Group}/>

        
         </div>
        </>
    )
}
export default Verifypage;