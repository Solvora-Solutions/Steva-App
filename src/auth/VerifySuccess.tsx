import image1 from "../image/image1.png"
import Steva from "../image/Steva.jpg"
import Group from "../image/Group.png"
import "./Verisuccess.css"
import check from"../image/check.png"
function VerifySuccess(){
        return(
            <>
            <div className="LoginUpper">
                <div className="VeriUpper">
                  <img style={{width:"228px", paddingTop:"20px", paddingBottom:"10px", height:"auto"}}src={Steva}/>
                    <img style={{width: "370px", textAlign:"center", left:"-32.58px", top:"441.42px", height:"auto"}}src={image1}/>
                </div>
                
                 <p style={{color:"#319f43"}}>Verified Successfully <img className="check" src={check}/> </p>
           </div>
            <div>
            <img className="CornerStyle" style ={{}}src={Group}/>
                
            </div>
            </>
        )
}
 export default VerifySuccess