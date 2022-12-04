import React from "react";
import './styles/navbar.css';
import {Route, Routes, Link} from 'react-router-dom';
import SearchBarTop from "./SearchBarTop";

const Navbar = (props) => {
    return (
        <nav>
            <div className="icon">
                <Link to={'/'}>VRnQA</Link>
            </div>
            <Routes>
                <Route path="/results" element={<SearchBarTop/>}/>
                <Route path="*" element={<div></div>}/>
            </Routes>
            <div className="btns">
                <div>About</div>
            </div>
        </nav>
    )
}

export default Navbar;