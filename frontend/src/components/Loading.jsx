import './styles/loading.css';
import React from "react";
import Lottie from "react-lottie";
import * as animData from "../assets/search-loading.json";

const Loading = (props) => {
    return (
        <div className="loading-screen">
            <div className="anim">
                <Lottie options={{
                    loop: true,
                    autoplay: true,
                    animationData: animData
                }}
                height={360}
                width={360} />
            </div>
            <div className="text">Hang on! We're finding the best answer for you...</div>
        </div>
    )
}

export default Loading;