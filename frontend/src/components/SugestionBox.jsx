import React, { useContext } from "react";
import { AppContext } from "../contexts/AppContext";
import './styles/sugestionBox.css';

const VideoCard = (props) => {
    const {dispatch, query} = useContext(AppContext);
    const videoId = props.videoId;
    const name = `Video_pv${videoId}`;
    const clickHandler = ()=>{
        query.videoId = videoId;
        dispatch({type: 'SET_TO_FETCH', value: true});
    }
    return (
        <div className="video-card" onClick={clickHandler}>
            <div className="thumbnail">
                <img src={`/thumbnail/pv${videoId}.jpg`} alt={name} />
            </div>
            <div className="details">
                <div className="name">{name}</div>
                <div className="others">
                    <div>Admin</div>
                    <div>03/12/2022</div>
                </div>
            </div>
        </div>
    )
}

const SugestionBox = (props) => {
    const queryResults = props.queryResults;
    const relatedVids = queryResults.relatedVideoIds;
    return (
        <div className="sugestion-box">
            <div className="heading">Related videos</div>
            <div className="list">
                {relatedVids.map((id)=>(
                    <VideoCard videoId={id} key={id} />
                ))}
            </div>
        </div>
    )
}

export default SugestionBox;