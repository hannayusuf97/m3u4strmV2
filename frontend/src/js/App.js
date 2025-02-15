import React, { useState, useEffect } from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css';
import Navbar from './Navbar';
import Footer from './Footer';
import Home from './Home';
import Movies from './Movies';
import Series from './Series';
import SeriesInfo from './SeriesInfo';
import MovieInfo from './MovieInfo';
import SearchResults from './SearchResults';
import ProtectedRoute from './ProtectedRoute';
import LoginPage from './LoginPage';
import '../css/App.css';
import '../css/styles.css';
import '../css/transitions.css';
import '../css/MovieInfo.css';
import '../css/SeriesInfo.css';

const RouteChangeTracker = () => {
  const location = useLocation();

  React.useEffect(() => {
    NProgress.start();
    const handleRouteChange = () => NProgress.done();
    window.addEventListener('popstate', handleRouteChange);

    return () => {
      NProgress.done();
      window.removeEventListener('popstate', handleRouteChange);
    };
  }, [location.pathname]);

  return null;
};

function App() {
  const [watchList, setWatchList] = useState(() => {
    const savedWatchList = localStorage.getItem('watchList');
    return savedWatchList ? JSON.parse(savedWatchList) : [];
  });

  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const addToWatchList = (item) => {
    setWatchList((prevList) => {
      const isDuplicate = prevList.some((listItem) => listItem.id === item.id);
      if (isDuplicate) {
        alert('This item is already in your watch list.');
        return prevList;
      }
      const updatedList = [...prevList, item];
      localStorage.setItem('watchList', JSON.stringify(updatedList));
      return updatedList;
    });
  };

  const removeFromWatchList = (index) => {
    setWatchList((prevList) => {
      const updatedList = prevList.filter((_, i) => i !== index);
      localStorage.setItem('watchList', JSON.stringify(updatedList));
      return updatedList;
    });
  };

  const clearWatchList = () => {
    setWatchList([]);
    localStorage.removeItem('watchList');
  };

  if (!isAuthenticated) {
    return (
      <div className="App bg-dark text-light">
        <div className="container-fluid">
          <Routes>
            <Route 
              path="/login" 
              element={
                <LoginPage 
                  isAuthenticated={isAuthenticated} 
                  setIsAuthenticated={setIsAuthenticated} 
                />
              } 
            />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </div>
      </div>
    );
  }

  return (
    <div className="App bg-dark text-light">
      <Navbar
        watchList={watchList}
        removeItem={removeFromWatchList}
        clearList={clearWatchList}
        setIsAuthenticated={setIsAuthenticated}
      />
      <RouteChangeTracker />
      <div className="container-fluid">
        <div className="row">
          <div className="col-md-9">
            <Routes>
              <Route path="/" element={<Home addToWatchList={addToWatchList} />} />
              <Route path="/movies" element={<Movies addToWatchList={addToWatchList} />} />
              <Route path="/series" element={<Series addToWatchList={addToWatchList} />} />
              <Route
                path="/search"
                element={<SearchResults addToWatchList={addToWatchList} watchList={watchList} />}
              />
              <Route
                path="/series/:id"
                element={<SeriesInfo addToWatchList={addToWatchList} watchList={watchList} />}
              />
              <Route
                path="/movies/:id"
                element={<MovieInfo addToWatchList={addToWatchList} watchList={watchList} />}
              />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute isAuthenticated={isAuthenticated}></ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}

export default App;