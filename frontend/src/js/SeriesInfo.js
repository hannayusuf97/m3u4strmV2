import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import NProgress from 'nprogress'; // Import NProgress
import '../css/SeriesInfo.css'; // Import the CSS file
import getApiBaseUrl from './apiConfig';
import secureApi from './SecureApi';

const SeriesInfo = ({ addToWatchList }) => {
  const { id } = useParams();
  const [series, setSeries] = useState(null);
  const [expandedSeason, setExpandedSeason] = useState(null);

  useEffect(() => {
    const fetchSeriesInfo = async () => {
      NProgress.start(); // Start the loading bar
      try {
        const response = await secureApi.get(`${getApiBaseUrl()}/series/${id}`);
        const data = await response.data;
        setSeries(data);
      } catch (error) {
        console.error('Error fetching series info:', error);
      } finally {
        NProgress.done(); // Stop the loading bar
      }
    };
    fetchSeriesInfo();
  }, [id]);

  const toggleSeason = (seasonIndex) => {
    setExpandedSeason(expandedSeason === seasonIndex ? null : seasonIndex);
  };

  const handleAddSeason = (season) => {
    const seasonId = `${id}-${season.season}`; // Unique ID for the season
    addToWatchList({ id: seasonId, name: `Season ${season.season}`, type: 'Season', seriesName: series.name, path: season.path, season: season.season });
  };

  const handleAddEpisode = (seasonNumber, episode) => {
    const episodeId = `${id}-${seasonNumber}-${episode.episode}`; // Unique ID for the episode
    addToWatchList({ id: episodeId, name: episode.name, type: 'Episode', path: episode.path, season: episode.season, episode: episode.episode });
  };

  const handleAddSeries = () => {
    addToWatchList({ id, name: series.name, type: 'Series', path: series.path });
  };

  const handleGetSeriesInfo = async () => {
    // Check if series and seasons exist
    if (!series || !series.seasons || series.seasons.length === 0) {
      console.error('No seasons found in the series');
      return;
    }

    // Get the first season
    const firstSeason = series.seasons[0];

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
      NProgress.start(); // Start loading indicator
      const response = await secureApi.get(
        `${getApiBaseUrl()}/media_info/${encodeURIComponent(firstEpisode.url)}?media_id=${series.id}&media_type=series`
      );
      
      if (!response.status === 200) {
        throw new Error('Network response was not ok');
      }

      const { duration: newDuration, resolution: newResolution } = await response.data;

      // Update the series state with new values
      setSeries(prev => ({
        ...prev,
        duration: newDuration !== "Error" ? newDuration : "Error",
        resolution: newResolution !== "Error" ? newResolution : "Error"
      }));

    } catch (error) {
      console.error('Error fetching series info:', error);
      setSeries(prev => ({
        ...prev,
        duration: "Error",
        resolution: "Error"
      }));
    } finally {
      NProgress.done(); // End loading indicator
    }
  };


  const placeholderImage = '/tvshowimage.jpg'; // Path to the placeholder image

  if (!series) return <div>Loading...</div>;

  // Determine duration and resolution for display
  const displayDuration = series.duration && series.duration !== "Error" ? series.duration : "Error";
  const displayResolution = series.resolution && series.resolution !== "Error" ? series.resolution : "Error";

  return (
    <div className="series-container">
      <h1 className="series-title">{series.name}</h1>
      <button className="btn btn-secondary" onClick={handleAddSeries}>Add to Watch List</button>
      <button className="btn btn-secondary" onClick={handleGetSeriesInfo}>Get Series Info</button>
      <img 
        className="series-image" 
        src={series.image || placeholderImage} 
        alt={series.name} 
        onError={(e) => { e.target.onerror = null; e.target.src = placeholderImage; }}
      />
      <div>
        <p><strong>Duration:</strong> {displayDuration}</p>
        <p><strong>Resolution:</strong> {displayResolution}</p>
      </div>
      {series.seasons.map((season, index) => (
        <div className="season-card" key={index}>
          <h2 className="season-title" onClick={() => toggleSeason(index)}>
           Season {season.season}
          </h2>
          <div className="button-container" style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-secondary btn-sm" onClick={() => handleAddSeason(season)}>Add Season</button>
          </div>
          {expandedSeason === index && (
            <ul className="episode-list">
              {season.episodes.map((episode, epIndex) => (
                <li className="episode-item" key={epIndex}>
                  <span>{episode.name}</span>
                  <button className="btn btn-secondary btn-sm add-button" onClick={() => handleAddEpisode(episode.season, episode)}>Add to Watch List</button>
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
};

export default SeriesInfo;
