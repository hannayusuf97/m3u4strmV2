const getApiBaseUrl = () => {
    // Check if the current hostname is localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '0.0.0.0' || window.location.hostname === '192.168.100.242') {
      return `http://${window.location.hostname}:8001/api`;
    } else {
      // Use the current hostname for production or other environments
      return `https://${window.location.hostname}:8001/api`;
    }
  };
  
  export default getApiBaseUrl;