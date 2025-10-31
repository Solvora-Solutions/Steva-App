import Group  from "../image/Group.png"
import Icecream from "../image/Icecream.png"
function Feedingfee(){
    return(
        <>
          <div className="LoginUpper">
                 <div className="TextWrapper">
                    <h1 style={{marginTop:"150px"}}><strong>Feeding Fee Details</strong></h1>
                 </div>
              
               <div className="pWrapper">
              <p>Student name</p>
               </div>
          <div className="InputWrapper">
            <input type="text" placeholder="Eg: Asante Lydia "/>
            <img src={Icecream}/>
          </div>
      

           <div className="pWrapper">
              <p>Class/Stage</p>
               </div>
              <input type="text" placeholder="Eg: Basic 6"/>
          
       
         
           <div className="pWrapper">
             < p>Cost for meal</p>
                </div>
         <label>Choose a Price: </label> 
         <select>
            <option value="">- Select Meal Type -- </option>
            <option value="full payment"> Full payment</option>
            <option value="Partial payment"> Partial payment</option>
         </select>
        
         <button>Payment</button>
         
        </div>
         
         
        <img className="CornerStyle" style ={{}}src={Group}/>
        </>
    )
} 
export default Feedingfee;