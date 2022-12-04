import React, {useContext, useEffect} from "react";
import {AppContext} from "../contexts/AppContext";
import Loading from "./Loading";
// import * as sampleRes from '../assets/sampleResponse.json';
import './styles/results.css';
import Player from "./Player";
import SugestionBox from "./SugestionBox";

const apiBaseUrl = 'http://localhost:5055/query';

const asyncFetch = async (url) => {
    const res = await fetch(url);
    const data = await res.json();
    // const data = sampleRes.default;
    await new Promise(r => setTimeout(r, 1000));
    return data;
    // return {};
}

const Results = (props) => {
    const {loading, toFetch, dispatch, query, queryResults} = useContext(AppContext);

    useEffect(()=>{
        if(toFetch === false) return;
        dispatch({type: 'SET_LOADING', value: true});
        const url = new URL(apiBaseUrl);
        url.searchParams.append('question', query.question);
        if(query.videoId){
            url.searchParams.append('videoId', query.videoId);
        }
        asyncFetch(url).then((data)=>{
            // console.log(data);
            dispatch({type: 'SET_QUERY_RESULT', value: data});
        })
        .catch((err)=>{
            console.log(`Error: ${err}`);
            dispatch({type: 'SET_QUERY_RESULT', value: null});
            
        }).finally(()=>{
            dispatch({type: 'SET_LOADING', value: false});
        });
        
    }, [toFetch, query, dispatch]);

    const error = queryResults === null || Object.keys(queryResults).length === 0;
    return (
        <div className="results">
            {loading && <Loading/>}
            {error && <div className="error">Error! Try again.</div>}
            {(loading || error) || <div className="layout">
                <div className="col-1">
                    <Player queryResults={queryResults}/>
                </div>
                <div className="col-2">
                    <SugestionBox queryResults={queryResults}/>
                </div>
            </div>}
        </div>
    )
}

export default Results;