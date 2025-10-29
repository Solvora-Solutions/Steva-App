import codereq from "../image/codereq.png"
import Group from "../image/Group.png"
import "./Coderequest.css"
function Coderequest(){
    return(
        <>
        <div className="LoginUpper">
           <img className="key-girl" src={codereq}/>
        <p>Forgot  Password</p>
        <p>Please check your mail and enter the five digit code to reset</p>
        <p>your password</p>


        <p>Didn't recieve the code? Resend </p>

        <button className="pass-reset">Reset Password</button>
        </div>
         
        <img className="CornerStyle" src={Group}/>

        </>
    )
}
export default Coderequest;