import "../css/ProviderManagement.css";
import getApiBaseUrl from "./apiConfig";
import React, { useState, useEffect } from "react";
import secureApi from "./SecureApi";

const ProviderManagement = () => {
  const [tableData, setTableData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [loadingProvider, setLoadingProvider] = useState(null);
  const [deleteProgress, setDeleteProgress] = useState(0);
  const [taskId, setTaskId] = useState(null);

  const fetchData = async () => {
    try {
      const response = await secureApi.get(`${getApiBaseUrl()}/get-providers`);
      const data = await response.data;
      setTableData(data);
    } catch (error) {
      console.error("Error fetching provider data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRowClick = (index) => {
    if (selectedRows.includes(index)) {
      setSelectedRows(selectedRows.filter((row) => row !== index));
    } else {
      setSelectedRows([...selectedRows, index]);
    }
  };

  // Function to poll progress
  const pollProgress = async (taskId) => {
    try {
      const response = await secureApi.get(
        `${getApiBaseUrl()}/delete-progress?task_id=${taskId}`
      );
      
      const progressData = response.data;
      setDeleteProgress(parseFloat(progressData.progress || 0));
      setLoadingProvider(progressData.provider);

      if (progressData.completed) {
        setLoadingProvider(null);
        setDeleteProgress(0);
        fetchData();
        return true;
      }
      return false;
    } catch (error) {
      console.error("Error polling progress:", error);
      return true; // Stop polling on error
    }
  };

  const handleDeleteProvider = async () => {
    const selectedProviders = selectedRows.map((index) => tableData[index]);
    setLoadingProvider(true);
    
    try {
      const response = await secureApi.post(
        `${getApiBaseUrl()}/delete-providers`,
        selectedProviders
      );

      if (response.status === 200) {
        const data = response.data;
        const task_id = data.task_id;
        setTaskId(task_id);

        // Start polling
        const pollInterval = setInterval(async () => {
          const shouldStop = await pollProgress(task_id);
          if (shouldStop) {
            clearInterval(pollInterval);
          }
        }, 1000);

      } else {
        console.error("Failed to initiate deletion:", response.statusText);
        setLoadingProvider(null);
      }
    } catch (err) {
      console.error("Error deleting providers:", err);
      setLoadingProvider(null);
    }
  };

  return (
    <div className="provider-management">
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Path</th>
              <th>Username</th>
              <th>Password</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {tableData.map((row, index) => (
              <tr
                key={index}
                className={selectedRows.includes(index) ? "selected-row" : ""}
                onClick={() => handleRowClick(index)}
              >
                <td>{row.name}</td>
                <td>{row.path}</td>
                <td>{row.username}</td>
                <td>{row.password}</td>
                <td>
                  <a href={row.link} target="_blank" rel="noopener noreferrer">
                    {row.link}
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="button-container">
        <button
          onClick={handleDeleteProvider}
          className="delete-provider-button"
        >
          Delete Provider
        </button>
      </div>

      {loadingProvider && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-message">
            Deleting: {loadingProvider} ({deleteProgress.toFixed(1)}%)
          </div>
        </div>
      )}
    </div>
  );
};

export default ProviderManagement;