import React, { useState, useCallback } from 'react';
import axios from 'axios';
import InfiniteScroll from 'react-infinite-scroller';
import NProgress from 'nprogress';
import 'nprogress/nprogress.css'; // Import NProgress styles
import MediaItem from './MediaItem'; // Import the MediaItem component
import getApiBaseUrl from './apiConfig'; // Import the utility function
import secureApi from './SecureApi';

const Movies = ({ addToWatchList }) => {
  const [media, setMedia] = useState([]);
  const [, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const fetchMedia = useCallback(async (page) => {
    if (loading) return;

    setLoading(true);
    NProgress.start(); // Start the loading bar

    try {
      const response = await secureApi.get(`${getApiBaseUrl()}/movies?page=${page}&size=10`);
      const newMedia = response.data;

      // Ensure that media items have the correct type
      const formattedMedia = newMedia.map(item => ({
        ...item,
        isSeries: false,
        isMovie: true,
      }));

      setMedia(prev => {
        const mediaMap = new Map(prev.map(item => [item.id, item]));
        formattedMedia.forEach(item => mediaMap.set(item.id, item));
        return Array.from(mediaMap.values());
      });

      setHasMore(newMedia.length > 0);
    } catch (error) {
      console.error('Error fetching movies:', error);
      setHasMore(false);
    } finally {
      setLoading(false);
      NProgress.done(); // Stop the loading bar
    }
  }, [loading]);

  const loadMore = useCallback(() => {
    if (hasMore && !loading) {
      setPage(prevPage => {
        const newPage = prevPage + 1;
        fetchMedia(newPage);
        return newPage;
      });
    }
  }, [fetchMedia, hasMore, loading]);

  return (
    <div>
      <InfiniteScroll
        pageStart={1}
        loadMore={loadMore}
        hasMore={hasMore}
        loader={<p key={0}>Loading...</p>}
        useWindow={true}
        threshold={10}
      >
        <div className="row">
          {media.length > 0 ? (
            media.map(item => (
              <MediaItem key={item.id || 'default_key'} item={item} addToWatchList={addToWatchList} />
            ))
          ) : (
            <p>No movies found.</p>
          )}
        </div>
      </InfiniteScroll>
      {loading && <p>Loading more...</p>}
    </div>
  );
};

export default Movies;
