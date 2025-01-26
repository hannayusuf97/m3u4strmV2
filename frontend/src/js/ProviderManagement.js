import "../css/ProviderManagement.css";
import getApiBaseUrl from "./apiConfig";
import React, { useState, useEffect } from "react";

const ProviderManagement = () => {
  const [tableData, setTableData] = useState([]); // State to hold provider data
  const [selectedRows, setSelectedRows] = useState([]); // State to track selected rows
  const [loadingProvider, setLoadingProvider] = useState(null); // State to track the currently loading provider
  const [deleteProgress, setDeleteProgress] = useState(0); // State to track deletion progress
  const [taskId, setTaskId] = useState(null); // State to store the task ID for progress tracking

  // Fetch provider data
  const fetchData = async () => {
    try {
      const response = await fetch(`${getApiBaseUrl()}/get-providers`);
      const data = await response.json(); // Parse JSON response
      setTableData(data); // Set provider data directly (no need to reformat)
    } catch (error) {
      console.error("Error fetching provider data:", error);
    }
  };

  // Fetch provider data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Handle row selection
  const handleRowClick = (index) => {
    if (selectedRows.includes(index)) {
      setSelectedRows(selectedRows.filter((row) => row !== index)); // Deselect row
    } else {
      setSelectedRows([...selectedRows, index]); // Select row
    }
  };

  // Handle provider deletion with progress tracking
  const handleDeleteProvider = async () => {
    const selectedProviders = selectedRows.map((index) => tableData[index]);
    setLoadingProvider(true); // Set loading state

    try {
      const response = await fetch(`${getApiBaseUrl()}/delete-providers`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(selectedProviders),
      });

      if (response.ok) {
        const data = await response.json();
        const task_id = data.task_id;
        setTaskId(task_id);

        const eventSource = new EventSource(
          `${getApiBaseUrl()}/delete-progress?task_id=${task_id}`
        );

        eventSource.onmessage = (event) => {
          try {
            const progressData = JSON.parse(event.data);
            const progress = parseFloat(progressData.data || 0);
            setDeleteProgress(progress);

            // Update the current provider
            const currentProvider = progressData.provider;
            if (currentProvider) {
              setLoadingProvider(currentProvider);
            }

            if (progressData.completed) {
              eventSource.close();
              setLoadingProvider(null);
              setDeleteProgress(0);
              fetchData(); // Refresh the provider list
            }
          } catch (err) {
            console.error("Error parsing progress data:", err);
            eventSource.close();
          }
        };

        eventSource.onerror = () => {
          console.error("Error receiving progress updates.");
          eventSource.close();
          setLoadingProvider(null);
          setDeleteProgress(0);
        };
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

      {/* Loading Indicator for Deletion */}
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
