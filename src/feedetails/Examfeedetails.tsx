import Group from "../image/Group.png"
function Examfeedetails(){
    return(
        <>
          <div className="LoginUpper">

    <h1><strong>Exam fee Details</strong></h1>
    <p>Student name</p>
    <input type="text" placeholder="Eg: Asante Lydia"/>

    <p>Class/Stage</p>
    <input type="text" placeholder="Eg: Basic 6"/>

    <p>Academic Year</p>
    <input type="number" />
     
     <div style={{display:"flex", flexDirection:"row",alignItems:"center" }}>
        <p>Students Stationary</p>   <p style={{marginLeft:"40px", fontSize:"10px", marginTop:"17px"}}><span>* Compulsory</span></p>
     </div>
   
     <select style={{width:"220px", textAlign:"center", marginLeft:"-7px", height:"23px"}}>
        <option value="">[Pay in full]</option>
        <option value="Full payment">Full payment</option>
        <option  value="Half the Price">Half the Price</option>
     </select>

     <button>Payment</button>
    </div>
    
    <img className="CornerStyle" src={Group}/>

    </>
        
    )
}
export default Examfeedetails;