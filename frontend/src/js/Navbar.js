import React, { useState, useCallback, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import WatchList from './WatchList';
import '../css/Navbar.css';
import getApiBaseUrl from './apiConfig';
import axios from 'axios';
import secureApi from './SecureApi';

function Navbar({ watchList, removeItem, clearList, setIsAuthenticated }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showWatchList, setShowWatchList] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);  // State to track admin status
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await secureApi.get(`${getApiBaseUrl()}/auth/check_admin`, {
        });
        setIsAdmin(response.data.is_admin);  // Assuming the response has a field `isAdmin`
      } catch (error) {
        console.error('Error checking admin status:', error);
        setIsAdmin(false);  // Hide Admin Portal if the check fails
      }
    };
    
    checkAdminStatus();
  }, []);

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${getApiBaseUrl()}/auth/logout`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      localStorage.removeItem('access_token');
      setIsAuthenticated(false);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      localStorage.removeItem('access_token');
      setIsAuthenticated(false);
      navigate('/login');
    }
  };

  const fetchSuggestions = useCallback(async (query) => {
    if (!query) {
      setSuggestions([]);
      return;
    }
    setLoading(true);
    try {
      const response = await secureApi.get(`${getApiBaseUrl()}/search?query=${query}`);
      setSuggestions(response.data);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (searchQuery) {
      fetchSuggestions(searchQuery);
    } else {
      setSuggestions([]);
    }
  }, [searchQuery, fetchSuggestions]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
    setShowSuggestions(true);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    navigate(`/search?query=${encodeURIComponent(searchQuery)}`);
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion.name);
    setShowSuggestions(false);

    if (suggestion.image) {
      navigate(`/series/${suggestion.id}`);
    } else if (suggestion.logo) {
      navigate(`/movies/${suggestion.id}`);
    }
  };

  const toggleWatchList = () => setShowWatchList(!showWatchList);

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <span className="navbar-title">M3U4STRM</span>
        </Link>

        <button className="btn btn-outline-light ms-3" onClick={toggleWatchList}>
          Watch List
        </button>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
              <Link className="nav-link" to="/">Home</Link>
            </li>
            <li className={`nav-item ${location.pathname === '/movies' ? 'active' : ''}`}>
              <Link className="nav-link" to="/movies">Movies</Link>
            </li>
            <li className={`nav-item ${location.pathname === '/series' ? 'active' : ''}`}>
              <Link className="nav-link" to="/series">Series</Link>
            </li>
            {isAdmin && (
              <li className={`nav-item ${location.pathname === '/admin' ? 'active' : ''}`}>
                <Link className="nav-link" to="/admin">Admin Portal</Link>
              </li>
            )}
          </ul>
          <div className="position-relative">
            <form className="d-flex ms-auto" onSubmit={handleSearchSubmit}>
              <input
                className="form-control me-2"
                type="search"
                placeholder="Search"
                aria-label="Search"
                value={searchQuery}
                onChange={handleSearchChange}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                onFocus={() => setShowSuggestions(true)}
              />
              <button className="btn btn-outline-light" type="submit">Search</button>
            </form>
            {showSuggestions && searchQuery && (
              <div className="suggestions-dropdown">
                <ul>
                  {loading ? (
                    <li>Loading...</li>
                  ) : (
                    suggestions.length > 0 ? (
                      suggestions.map((suggestion, index) => (
                        <li key={index} onClick={() => handleSuggestionClick(suggestion)}>
                          {suggestion.name}
                        </li>
                      ))
                    ) : (
                      <li>No suggestions found.</li>
                    )
                  )}
                </ul>
              </div>
            )}
          </div>
          <button 
            className="btn btn-outline-danger ms-3" 
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>
      {showWatchList && (
        <div className="watch-list-dropdown">
          <WatchList
            items={watchList}
            removeItem={removeItem}
            clearList={clearList}
          />
        </div>
      )}
    </nav>
  );
}

export default Navbar;
