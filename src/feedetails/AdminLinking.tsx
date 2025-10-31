
import Linking from "../image/Linking.png"
import Connecting from "../image/Connecting.png"
import Ellipse from "../image/Ellipse.png"
import "./AdminLinking.css"
import Group from "../image/Group.png"
function AdminLinking (){
    return (
        <>
        <div className="LoginUpper">
             <h1><strong> Add the Student </strong></h1>
             <h1 style={{marginTop:"0"}}><strong> you'll make payment for</strong></h1>
        <img className="link-img" src={Linking}/>
        <input style={{marginBottom:"20px"}} type = "text" placeholder="First Name"/>

        <input style={{marginBottom:"20px"}} type="text"  placeholder="Last Name "/>

        <input type="number" placeholder=""/>
        <div className="Para">
           <p style={{fontSize:"13px", marginLeft:"-100px", marginTop:"0"}}>Current academic class or grade level</p>
        </div>
          
        
        
      <div className="ButtonWrapper">
            <img className="Ellipse-icon" src={Ellipse}/>
           <button className="link-btn" >Link <img className="Connecting-img" src={Connecting}/></button>
      </div>
        </div>

        <img className="CornerStyle" src={Group}/>
        </>
    )
}  export default AdminLinking;