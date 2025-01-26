  import React from 'react';
  import axios from 'axios';
  import '../css/WatchList.css';
  import getApiBaseUrl from './apiConfig';
  const WatchList = ({ items, removeItem, clearList }) => {
    const handleSubmit = async () => {
      try {
        // Remove duplicates before sending to the backend
        const uniqueItems = Array.from(new Map(items.map(item => [item.id, item])).values());
        
        // Send the watchlist to the backend
        const response = await axios.post(`${getApiBaseUrl()}/watchlist/`, uniqueItems);
        console.log(response.data);
      // Log the response from the backend
        clearList();
        alert('Watch list submitted successfully!');
      } catch (error) {
        alert('Failed to submit watch list. Please try again.');
      }
    };

    return (
      <div className="watch-list bg-dark text-light h-100">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h3 className="mb-0">Watch List</h3>
          <button 
            className="btn btn-outline-danger btn-sm" 
            onClick={clearList}
            disabled={items.length === 0}
          >
            Clear List
          </button>
        </div>
        <ul className="list-group list-group-flush">
          {items.map((item, index) => (
            <li key={index} className="list-group-item bg-dark text-light d-flex justify-content-between align-items-center">
              <span>
                {item.type === 'Season' ? `${item.seriesName}: ${item.name}` : item.name} 
                ({item.type === 'Episode' ? 'Episode' : item.type === 'Season' ? 'Season' : item.type === 'Series' ? 'Series' : 'Movie'})
              </span>
              <button 
                className="btn btn-outline-danger btn-sm" 
                onClick={() => removeItem(index)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
        {items.length === 0 && (
          <div className="card-body text-center">
            <p className="text-muted">Your watch list is empty.</p>
          </div>
        )}
        <div className="card-footer">
          <button 
            className="btn btn-primary btn-block w-100" 
            onClick={handleSubmit} 
            disabled={items.length === 0}
          >
            Submit List
          </button>
        </div>
      </div>
    );
  };

  export default WatchList;
