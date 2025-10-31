import  Group from "../image/Group.png"

function Classesfee(){
    return(
        <>
           <div className="LoginUpper">
                 <div className="TextWrapper">
                    <h1 style={{marginTop:"150px"}}><strong>Classes Fee Details</strong></h1>
                 </div>
              
               <div className="pWrapper">
              <p>Student name</p>
               </div>
          
         <input type="text" placeholder="Eg: Asante Lydia "/>

           <div className="pWrapper">
              <p>Class/Stage</p>
               </div>
              <input type="text" placeholder="Eg: Basic 6"/>
          
       
         
           <div className="pWrapper">
             < p>Academic Year</p>
                </div>
         <input type="text"  />
        
         
         <button>Payment</button>
        </div>
         
         
        <img className="CornerStyle" style ={{}}src={Group}/>
        </>
    )
}
export default Classesfee;