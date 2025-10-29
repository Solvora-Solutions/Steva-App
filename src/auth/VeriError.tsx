import fallicon from "../image/fallicon.png"
import huicon from "../image/huicon.png"
import icon from "../image/icon.png"
import Ellipse from "../image/Ellipse.png"
import { Navigate, useNavigate } from "react-router-dom"
import "./VeriError.css"
import Group from "../image/Group.png"
function VeriError(){
    const navigate = useNavigate();
     const VeriSuccess = () => {
        navigate("/VerifySuccess");
     }
    return(
        <>
     
            <div className="errorimg">
               <img src={fallicon} style={{width: "100px", height:"100px",left:"170px"}}/>
            <img src={huicon} style={{width: "200px", height: "200px", left:"161px"}}/>
            </div>

              <div className="LoginUpper">
                <div className="TextWrapper">
                  <p style={{color:"#000000"}}>Please enter your wards student's ID to verify and link</p>
            <p style={{color:"#000000",}}> them to your account </p>
                </div>
                 
            
             <div className="Entries">
             <input type="number" placeholder="Enter Student ID"/>
                </div>
               
                   <div className="TextWrapper">
                     <p style={{color: "#c5080b"}}>Invalid Student ID. Please make sure you've entered</p>
                     <p style={{color:"#c5080b", marginTop:"0px"}} >the correct ID </p>
                   </div>
               
            
           
            <div className="ButtonWrapper">
              <img src={Ellipse} className="Ellipseicon"/>
        <button className="Verify-btn" onClick={VeriSuccess} >
                Verify <img className="iconimg" src={icon}/>
        </button>

            </div>
       

              </div>
            
        <img className="CornerStyle" style ={{}}src={Group}/>


        
       
        </>
    )
}
export default VeriError;