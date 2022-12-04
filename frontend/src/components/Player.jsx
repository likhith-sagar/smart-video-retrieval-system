import React, { useEffect, useRef } from "react";
import './styles/player.css';

const convertTs = (ts)=>{
    //ts: hh:mm:ss
    let nums = ts.split(':');
    let s = 60*60;
    let ans = 0;
     nums.forEach(n => {
        ans+=(s * Number(n));
        s /= 60;
     });
    return ans
}

const AnsCard = (props) =>{
    const ans = props.answer;
    const clickHandler = ()=>{
        const seekTime = convertTs(ans[1]);
        props.seek(seekTime);
    }
    return (
        <div className="ans-card">
            <div className="answer">
                {ans[0]}
            </div>
            <div className="meta">
                <div className="timestamps">
                    {`${ans[1]} -- ${ans[2]}`}
                </div>
                <button onClick={clickHandler}>Play</button>
            </div>
        </div>
    )
};

const Player = (props) => {
    const queryResults = props.queryResults;
    const videoId = queryResults.videoId;
    const ansref = queryResults.answers;
    const answers = [ansref.bestAnswer, ansref.longAnswer, ...ansref.otherAnswers];
    const vidElement = useRef(null);
    const seek = (time) => {
        vidElement.current.currentTime = time;
    }
    useEffect(()=>{
        const bestAns = answers[0];
        let bestStartTime = convertTs(bestAns[1]);
        bestStartTime = bestStartTime - 3 >= 0 ? bestStartTime - 3 : bestStartTime;
        seek(bestStartTime);
    }, []);
    return (
        <div className="player">
            <div className="video-box"> 
                <video id="videoPlayer" ref={vidElement} controls autoPlay >
                    <source src={`/video/pv${videoId}.mp4`} type="video/mp4" />
                </video>
            </div>
            <div className="video-details">
                <div className="name">{`Video_pv${videoId}`}</div>
                <div className="others">
                <div>12/11/2023</div>
                <div>Admin</div>
                <button onClick={()=>seek(0)}>Play from start</button>
                </div>
            </div>
            <div className="answer-box">
                <div className="heading">Answers</div>
                <div className="ans-list">
                    {answers.map((answer, i)=>(
                        <AnsCard answer={answer} key={i} seek={seek}/>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Player;