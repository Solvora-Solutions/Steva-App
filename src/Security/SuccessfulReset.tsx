import Steva from "../image/Steva.jpg"
import fluent from "../image/fluent.png"
import Group from "../image/Group.png"
import "./SuccessfulReset.css"
function SuccessfulReset (){
    return(
        <>
        <div className="LoginUpper">
           <img className="Steva-img" src={Steva}/>
          <h1 style={{marginTop:"4px"}}>Forgot Password</h1>
          <p>Your Password has been reset login to your account</p>

          <img className="fluent-img" src={fluent}/>
          <p>You have successfully changed your password wait to be redirected </p>
          <p>to the login</p>
        </div>
          <img className="CornerStyle"src={Group}/>
        </>        
    )
} 
export default SuccessfulReset;