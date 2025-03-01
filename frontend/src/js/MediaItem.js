import React, { useState, useEffect } from 'react';
import '../css/styles.css'; // Ensure specific styles are imported
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import getApiBaseUrl from './apiConfig';
import secureApi from './SecureApi';
const placeholderImageSeries = '/tvshowimage.jpg';
const placeholderImageMovie = '/movieimage.jpg';

const MediaItem = ({ item, addToWatchList }) => {
  const navigate = useNavigate(); // Initialize useNavigate
  const [imageSrc, setImageSrc] = useState(() => {
    if (item.image) return item.image; // Series
    if (item.logo) return item.logo;   // Movie
    return item.isSeries ? placeholderImageSeries : placeholderImageMovie;
  });

  const [duration, setDuration] = useState("Unknown");
  const [resolution, setResolution] = useState("Unknown");

  const handleError = () => {
    setImageSrc(item.isSeries ? placeholderImageSeries : placeholderImageMovie);
  };

  const mediaType = item.image ? 'Series' : item.logo ? 'Movie' : 'Unknown';

  const handleWatchNow = () => {
    console.log(`Watch Now clicked for ${item.name}`);
    // Implement your watch now functionality here
  };

  const handleAddToList = () => {
    addToWatchList(item);
    console.log(`Added ${item.name} to Watch List`);
  };

  const handleViewEpisodes = (id) => {
    console.log(`View Episodes clicked for ${item.name}`);
    navigate(`/series/${id}`); // Update the URL to the series page
  };

  const handleViewDetails = () => {
    navigate(`/movies/${item.id}`); // Navigate to the MovieInfo page
  };

  const handleGetMovieInfo = async () => {
    try {
      const response = await secureApi.get(`${getApiBaseUrl()}/media_info/${encodeURIComponent(item.url)}?media_id=${item.id}&media_type=movie`); // Send both url and id
      const { duration: newDuration, resolution: newResolution } = await response.data;

      // Update state with fetched values or default to "Unknown"
      setDuration(newDuration && newDuration !== "Unknown" ? newDuration : "Unknown");
      setResolution(newResolution && newResolution !== "Unknown" ? newResolution : "Unknown");
    } catch (error) {
      console.error('Error fetching movie info:', error);
    }
  };

  const handleGetSeriesInfos = async () => {
    // Check if series and seasons exist
    if (!item.seasons || item.seasons.length === 0) {
      console.error('No seasons found in the series');
      return;
    }

    // Get the first season
    const firstSeason = item.seasons[0];

    // Check if the first season has episodes
    if (!firstSeason.episodes || firstSeason.episodes.length === 0) {
      console.error('No episodes found in the first season');
      return;
    }

    // Get the first episode of the first season
    const firstEpisode = firstSeason.episodes[0];

    // Check if the first episode has a URL
    if (!firstEpisode.url) {
      console.error('No URL found for the first episode');
      return;
    }

    try {
      const response = await secureApi.get(
        `${getApiBaseUrl()}/media_info/${encodeURIComponent(firstEpisode.url)}?media_id=${item.id}&media_type=series`
      );
      
      if (!response.statusCode === 200) {
        throw new Error('Network response was not ok');
      }

      const { duration: newDuration, resolution: newResolution } = await response.data;

      // Update the series state with new values
      setDuration(newDuration && newDuration !== "Unknown" ? newDuration : "Unknown");
      setResolution(newResolution && newResolution !== "Unknown" ? newResolution : "Unknown");

    } catch (error) {
      console.error('Error fetching series info:', error);
    }
  };

  // Update duration and resolution state on component mount
  useEffect(() => {
    // Check if item has duration and resolution
    if (item.duration && item.duration !== "Unknown") {
      setDuration(item.duration);
    } else {
      setDuration("Unknown");
    }
    
    if (item.resolution && item.resolution !== "Unknown") {
      setResolution(item.resolution);
    } else {
      setResolution("Unknown");
    }
  }, [item]);

  return (
    <div className="col-md-4 mb-4">
      <div className="card bg-dark text-light">
        <img
          src={imageSrc}
          className="card-img-top"
          alt={item.name}
          onError={handleError}
        />
        <div className="card-overlay">
          <div className="card-info">
            <h5 className="card-title">{item.name}</h5>
            <p className="card-text">{mediaType}</p>
            <p>Duration: {duration}</p>
            <p>Resolution: {resolution}</p>
          </div>
          <div className="button-overlay">
            <button className="btn btn-secondary btn-sm" onClick={handleWatchNow}>Watch Now</button>
            <button className="btn btn-secondary btn-sm" onClick={handleAddToList}>Add to List</button>
            {mediaType === 'Series' && (
              <>
                <button className="btn btn-info btn-sm" onClick={() => handleViewEpisodes(item.id)}>View Episodes</button>
                <button className="btn btn-secondary btn-sm" onClick={handleGetSeriesInfos}>Get Series Info</button>
              </>
            )}
            {mediaType === 'Movie' && (
              <>
                <button className="btn btn-info btn-sm" onClick={handleViewDetails}>View Details</button>
                <button className="btn btn-secondary btn-sm" onClick={handleGetMovieInfo}>Get Media Info</button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MediaItem;
