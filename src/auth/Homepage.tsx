import Group from "../image/Group.png"
import "./Homepage.css"
import Ellipse37 from "../image/Ellipse37.png"
import payment from "../image/payment.png"
import description from "../image/description.png"
import receipt from "../image/receipt.png"
import { Navigate, useNavigate } from "react-router-dom"
import ProfileDropdown from "./ProfileDropdown"
import male from "../image/male.png.png"
import female from "../image/female.png.png"
function Homepage(){
    const navigate = useNavigate()
    const paymentde = () => {
        navigate ("/Paymentdetails")
    };
    const Adminlinking = () => {
        navigate("/AdminLinking")
    }
    
    return(
        <> 
        
         <div className="top">
            <p>Dashboard</p>
            <ProfileDropdown
            onViewProfile={() => navigate("/Profileview")}
            onUpdateProfile={() => navigate("/ProfileUpdate")}
            
            /> 
        </div>
    <div className="maincollection">
      <div className="inner">
       <p><strong>Welcome back</strong> </p>

    <p>Activty</p>

    <div className="StatusBoard">
         <p style={{color:"black",fontSize:"24px"}}>Status : </p>
         <p style={{color:"#F24900", fontSize:"24px"}}>Fully Paid</p>
    </div>

    <p>Shortcuts</p>

    <div className="Shortcutbuttons">
       <button className="receipt-btn" onClick={Adminlinking} style={{cursor:"pointer"}}> <img src={receipt}/>Link Student</button>
       <button  className="payment-btn" onClick={paymentde} style={{cursor: "pointer"}}> <img src={payment}/>Payment</button>
       <button className="history-btn" style={{cursor:"pointer"}}> <img src={description}/>Payment History</button>
     
    </div>

    </div>

    <div className="Rightside">
        <div className="upper">
           <p style={{width:"74px", height:"29px",fontSize:"24px"}}><strong>Wards</strong></p>
        <img style={{width:"40px", height:"auto"}} src={male}/>
        <img style={{width:"40px", height:"auto", marginLeft:"6px"}}src={female}/>
        </div>
       
        <div className="Wardinfo">
           <p><img src={Ellipse37}/>  </p>
           <p><img src={Ellipse37}/></p>
        <button > View all </button>
        </div>

    </div>
    
    </div>
   
     <img className="CornerStyle" src={Group}/>
       
        
        </>
   



    )

}
export default Homepage;