import React, { useContext } from "react";
import './styles/home.css';
import Lottie from "react-lottie";
import * as animData from "../assets/question-anim2.json";
import { AppContext } from "../contexts/AppContext";
import { useNavigate } from "react-router-dom";

const Home = (props) => {
    const {dispatch, query} = useContext(AppContext);
    const navigate = useNavigate();
    const submitHandler = (e)=>{
        e.preventDefault();
        let question = e.target.question.value.trim();
        if(question){
            query.question = question;
            query.videoId = null;
            dispatch({type: 'SET_TO_FETCH', value: true});
            navigate('/results');
        }
    };
    return (
        <div className="home">
            <div className="anim">
                <Lottie options={{
                    loop: false,
                    autoplay: true,
                    animationData: animData
                }}
                height={320}
                width={320} />
            </div>
            <div className="search-bar">
            <form onSubmit={submitHandler}>
                <input type="search" name="question" id="question" 
                placeholder="Type your question here"
                autoComplete="Off"/>
                <button type="submit">Search</button>
            </form>
            </div>
            <div className="texts">
                
            </div>
        </div>
    )
}

export default Home;