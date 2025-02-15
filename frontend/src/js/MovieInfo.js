import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import NProgress from 'nprogress'; // Import NProgress
import '../css/MovieInfo.css'; // Import the CSS file
import getApiBaseUrl from './apiConfig'; // Import the utility function
import secureApi from './SecureApi';

const MovieInfo = ({ addToWatchList }) => {
  const { id } = useParams();
  const [movie, setMovie] = useState(null);
  const placeholderImage = '/movieimage.jpg'; // Path to the placeholder image in the public directory

  useEffect(() => {
    const fetchMovieInfo = async () => {
      NProgress.start(); // Start the loading bar
      try {
        const response = await secureApi.get(`${getApiBaseUrl()}/movies/${id}`);
        const data = await response.data;
        setMovie(data);
      } catch (error) {
        console.error('Error fetching movie info:', error);
      } finally {
        NProgress.done(); // Stop the loading bar
      }
    };
    fetchMovieInfo();
  }, [id]);

  const handleAddMovie = () => {
    if (movie) {
      const movieModel = {
        id: movie.id, // Assuming the movie object has an id property
        name: movie.name,
        type: movie.type || 'Movie', // Ensure type is set correctly
        path: movie.path,
        logo: movie.logo || placeholderImage, // Use the logo or placeholder if not available
        url: movie.url || '', // Ensure URL is included
        resolution: movie.resolution || null, // Include resolution if available
      };

      // Log the movie model to verify its structure
      addToWatchList(movieModel); // Call the function to add the movie model to the watch list
    }
  };

  const handleGetMovieInfo = async () => {
    if (movie && movie.url) {
      try {
        const response = await secureApi.get(`${getApiBaseUrl()}/media_info/${encodeURIComponent(movie.url)}?media_id=${movie.id}&media_type=movie`);
        const { duration: newDuration, resolution: newResolution } = await response.data;

        // Update the state if new data is fetched
        if (newDuration && newDuration !== "Error") setMovie(prev => ({ ...prev, duration: newDuration }));
        if (newResolution && newResolution !== "Error") setMovie(prev => ({ ...prev, resolution: newResolution }));
      } catch (error) {
        console.error('Error fetching movie info:', error);
      }
    }
  };

  if (!movie) return <div>Loading...</div>;

  // Determine duration and resolution for display
  const displayDuration = movie.duration && movie.duration !== "Error" ? movie.duration : "Error";
  const displayResolution = movie.resolution && movie.resolution !== "Error" ? movie.resolution : "Error";

  return (
    <div className="movie-container">
      <h1 className="movie-title">{movie.name}</h1>
      <img
        className="movie-image"
        src={movie.logo || placeholderImage}
        alt={movie.name}
        onError={(e) => { e.target.onerror = null; e.target.src = placeholderImage; }} // Fallback to placeholder
      />
      <button className="btn btn-secondary" onClick={handleAddMovie}>Add to Watch List</button>
      <button className="btn btn-secondary" onClick={handleGetMovieInfo}>Get Movie Info</button>
      <div>
        <p><strong>Duration:</strong> {displayDuration}</p>
        <p><strong>Resolution:</strong> {displayResolution}</p>
      </div>
    </div>
  );
};

export default MovieInfo;
