import "./payment.css"
import home_fill from "./image/home_fill.png"
import Group from "../image/Group.png"
import Ellipse37 from "../image/Ellipse37.png"
function Paymentdetails (){
           return(
            <>
            <div className="LoginUpper">
               <p style={{marginTop:"80px",fontSize:"30px", color:"black"}}>Select a Payment Option from the list below</p>
            

           <div className="ellipseoption">
            <img style={{width:"5px", height:"5px", marginRight:"5px", marginTop:"25px"}}src={Ellipse37}/><p style={{marginTop:"20px"}}><a href="/schoolfeesdetails">School fees</a></p>
           </div>

            <div className="ellipseoption">
            <img style={{width:"5px", height:"5px", marginRight:"5px", marginTop:"20px"}}src={Ellipse37}/><p><a href="/Classesfee">Classes fees</a></p>
            </div>


              <div className="ellipseoption">
                <img style={{width:"5px", height:"5px",marginRight:"5px",marginTop:"20px"}}src={Ellipse37}/><p><a href="/Feedingfee">Feeding fees</a></p>
              </div>

             <div className="ellipseoption">
                 <img style={{width:"5px", height:"5px",marginRight:"5px", marginTop:"20px"}}src={Ellipse37}/> <p><a href="/Busfees">Bus fees</a></p>
             </div>

               <div className="ellipseoption">
                  <img style={{width:"5px", height:"5px",marginRight:"5px", marginTop:"20px"}}src={Ellipse37}/><p><a href="/Stationary"> Stationary</a></p>
               </div>

              <div className="ellipseoption" >
                   <img style={{width:"5px", height:"5px",marginRight:"5px", marginTop:"25px"}}src={Ellipse37}/><p><a href="/ExtraCarriculum">Extra Curriculum</a></p>
              </div>

               <div className="ellipseoption">
                   <img style={{width:"5px", height:"5px",marginRight:"5px", marginTop:"15px"}}src={Ellipse37}/><p><a href="/Examfeedetails">Exam fees</a></p>
               </div>
            
            </div>
           







            <img className="CornerStyle" style ={{}}src={Group}/>
       
            </>
           )
}
export default Paymentdetails;



               