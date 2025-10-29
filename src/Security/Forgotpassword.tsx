import Steva from "../image/Steva.jpg"
import Group  from "../image/Group.png"
import "./Forgotpassword.css"


function Forgotpassword (){
    return(
          <>
          <div className="LoginUpper">
              <img className="Steva-img" src={Steva}/>
         <p>Forgot password </p>
         <p>Please enter your email to reset your password</p>

         <input className="FP-Input" type="email" placeholder="Email"/>
         <p>Login using Password? <a href="/">Login</a> </p>

         <button className="pass-reset" >Reset Passsword</button>
          </div>
        <img className="CornerStyle" src={Group}/>

        </>
    )
      
    
}  export default Forgotpassword;