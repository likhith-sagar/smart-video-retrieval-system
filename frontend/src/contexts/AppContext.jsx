import React, {useReducer, createContext} from "react";

export const AppContext = createContext();

const myReducer = (state, action)=>{
    switch (action.type) {
        case "SET_LOADING":
            return {...state, loading: action.value};

        case "SET_TO_FETCH":
            if(action.value)
                return {...state, toFetch: action.value, queryResults: {}};
            return {...state, toFetch: action.value};

        case "SET_QUERY_RESULT":
            return {...state, queryResults: {...action.value}, toFetch: false};

        default:
            return state;
    }
}

const initState = {
    query: {}, //{question: ---, videoId: ---}
    queryResults: {},
    loading: false,
    toFetch: false
};

const AppContextProvider = (props)=>{
    const [state, dispatch] = useReducer(myReducer, initState);
    // console.log(state);
    return (
        <AppContext.Provider value={{...state, dispatch}}>
            {props.children}
        </AppContext.Provider>
    )
}

export default AppContextProvider;