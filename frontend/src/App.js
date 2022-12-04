import './App.css';
import AppContextProvider from './contexts/AppContext';
import {BrowserRouter, Route, Routes} from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Results from './components/Results';

function App() {
  return (
    <BrowserRouter>
      <AppContextProvider>
        <div className="App">
          <Navbar/>
          <Routes>
            <Route path='/' element={<Home/>}/>
            <Route path='/results' element={<Results/>}/>
          </Routes>
        </div>
      </AppContextProvider>
    </BrowserRouter>
  );
}

export default App;
