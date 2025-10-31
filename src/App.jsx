
import Signup from "./auth/Signup";
import TermsofService from "./auth/TermsofService";
import Homepage from "./auth/Homepage";
import Register from "./auth/Register";
import Verifypage from "./auth/Verifypa";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import VerifySuccess from "./auth/VerifySuccess";
import VeriError from "./auth/VeriError"
import Paymentdetails from "./Security/payment";
import Forgotpassword from "./Security/Forgotpassword"
import Coderequest from "./Security/Coderequest";
import Resetpassword from "./Security/Resetpassword";
import SuccessfulReset from "./Security/SuccessfulReset";
import Schoolfeesdetails from "./feedetails/Schoolfeesdetails";
import Classesfee from "./feedetails/Classesfee";
import Feedingfee from "./feedetails/Feedingfee";
import Busfees from "./feedetails/Busfees";
import AdminLinking from "./feedetails/AdminLinking";
import Profileview from "./auth/Profileview";
import ProfileUpdate from "./auth/ProfileUpdate";
import Confirmresetpassword from "./Security/Confirmresetpassword";
import Stationary from "./feedetails/Stationary"
import ExtraCarriculum from "./feedetails/ExtraCarriculum";
import Examfeedetails from "./feedetails/Examfeedetails";
function App (){
  return(
    <>
    <Router>
      <Routes>
        <Route path="/" element={<Signup/>}/>
        <Route path="/Homepage" element={<Homepage/>}/>
        <Route path="/TermsofService" element={<TermsofService/>}/>
        <Route path="/Register" element={< Register/>}/>
        <Route path="/Verifypage" element={<Verifypage/>}/>
        <Route path="/VerifySuccess" element={<VerifySuccess/>}/>
        <Route path="/VeriError"  element={<VeriError/>}/>
        <Route path="/Paymentdetails" element={<Paymentdetails/>}/>
        <Route path="/Forgotpassword" element={<Forgotpassword/>}/>
        <Route path="/Coderequest" element={<Coderequest/>}/>
        <Route path="/Resetpassword" element={<Resetpassword/>}/>
        <Route path="/SuccessfulReset" element={<SuccessfulReset/>}/>
        <Route path = "/Schoolfeesdetails" element={<Schoolfeesdetails/>}/>
        <Route path="/Classesfee" element={<Classesfee/>}/>
        <Route path="/Feedingfee" element={< Feedingfee/>}/>
        <Route path="/Busfees" element={<Busfees/>}/>
        <Route path="/AdminLinking" element={<AdminLinking/>}/>
        <Route path="/Profileview"  element={<Profileview/>}/>
        <Route path= "/ProfileUpdate" element={<ProfileUpdate/>}/>
        <Route path="/Confirmresetpassword" element={<Confirmresetpassword/>}/>
        <Route path="/Stationary" element={<Stationary/>}/>
        <Route path="/ExtraCarriculum" element={<ExtraCarriculum/>}/>
        <Route path="/Examfeedetails" element={<Examfeedetails/>}/>
        </Routes>
    </Router>
    
    </>

  )
 
}
export default App;