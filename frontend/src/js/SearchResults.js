import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css'; // Import NProgress styles
import InfiniteScroll from 'react-infinite-scroller'; // Import InfiniteScroll component
import MediaItem from './MediaItem'; // Import the MediaItem component
import getApiBaseUrl from './apiConfig'; // Import the utility function
import secureApi from './SecureApi';

const SearchResults = ({ addToWatchList }) => {
  const location = useLocation();
  const [media, setMedia] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const size = 50;
  const query = new URLSearchParams(location.search).get('query');

  // Fetch media function
  const fetchMedia = async (pageToLoad) => {
    if (loading || !hasMore) return; // Prevent fetching if loading or no more results

    setLoading(true);
    NProgress.start(); // Start the loading progress bar

    try {
      let response;
      if (!query) {
        response = await secureApi.get(`${getApiBaseUrl()}/media?page=${pageToLoad}&size=7`);
      } else {
        response = await secureApi.get(`${getApiBaseUrl()}/search/?query=${query}&page=${pageToLoad}&size=${size}`);
      }

      const newMedia = response.data;

      // Use a Map to track unique items
      const mediaMap = new Map(media.map(item => [item.id, item]));

      // Add new media to the Map
      newMedia.forEach(item => {
        mediaMap.set(item.id, item); // This will overwrite duplicates
      });

      // Convert the Map back to an array
      const uniqueMedia = Array.from(mediaMap.values());

      // Update state with unique media
      setMedia(uniqueMedia);

      // If fewer than `size` results are returned, there are no more pages
      if (newMedia.length < size) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching search results:', error);
      setHasMore(false); // Stop loading more if there's an error
    } finally {
      setLoading(false);
      NProgress.done(); // End the loading progress bar
    }
  };

  useEffect(() => {
    // Reset media list, page, and loading states when the query changes
    setMedia([]);
    setPage(1);
    setHasMore(true);
    fetchMedia(1); // Fetch the first page of results
  }, [query]);

  // Function to load more media when scrolling
  const loadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      fetchMedia(nextPage); // Load the next page of results
      setPage(nextPage); // Update the page state after fetching
    }
  };

  return (
    <div className="home-container">
      <InfiniteScroll
        pageStart={1} // Start loading from page 1
        loadMore={loadMore} // Function to load more data
        hasMore={hasMore} // Whether to keep loading more
        loader={<p key={0}>Loading...</p>} // Loader when fetching more data
        useWindow={true} // Use the window scroll event
        threshold={50} // Load more 50px before reaching the bottom
      >
        <div className="media-list row">
          {media.length > 0 ? (
            media.map((item) => (
              <MediaItem
                key={item.id || 'default_key'}
                item={item}
                addToWatchList={addToWatchList}
              />
            ))
          ) : !hasMore && media.length === 0 ? (
            <p>No media found.</p>
          ) : null}
        </div>
      </InfiniteScroll>
    </div>
  );
};

export default SearchResults;
