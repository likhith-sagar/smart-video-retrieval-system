import './styles/searchBarTop.css';
import React, { useContext } from "react";
import { AppContext } from '../contexts/AppContext';

const SearchBarTop = (props) => {
    const {query, dispatch} = useContext(AppContext);
    const submitHandler = (e)=>{
        e.preventDefault();
        let question = e.target.search.value.trim();
        if(question){
            query.question = question;
            query.videoId = null;
            dispatch({type: 'SET_TO_FETCH', value: true});
        }
    };
    return (
        <div className="search-bar-top">
            <form onSubmit={submitHandler}>
                <input type="search" name="search" id="seach" 
                placeholder="Search"
                defaultValue={query.question}
                autoComplete='off'/>
                <button type="submit">Go</button>
            </form>
        </div>
    )
}

export default SearchBarTop;