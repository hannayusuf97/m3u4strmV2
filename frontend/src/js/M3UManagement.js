import "../css/M3UManagement.css";
import getApiBaseUrl from "./apiConfig";
import secureApi from "./SecureApi";
import React, { useState, useEffect } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import M3UProgress from "./M3UProgress";

const M3UManagement = () => {
  const [tableData, setTableData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [fileInput, setFileInput] = useState(null);
  const [uploadProgress, setUploadProgress] = useState({
    total_progress: 0,
    currentFile: '',
    message: '',
    totalM3Us: 0,
    currentM3U: 0,
    is_complete: false,
    error: null
  });
  const [loadingTaskId, setLoadingTaskId] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Log the API URL being called
        const apiUrl = `${getApiBaseUrl()}/m3us/`;
        console.log("Fetching data from:", apiUrl);

        const response = await secureApi.get(apiUrl);
        console.log("API Response:", response);

        if (!response.data) {
          throw new Error("No data received from server");
        }

        const data = response.data;
        const formattedData = Object.entries(data).map(
          ([file, { file_path, creation_date }]) => ({
            file,
            path: file_path,
            creationTime: creation_date,
          })
        );
        setTableData(formattedData);
        setError(null);
      } catch (error) {
        console.error("Error details:", {
          message: error.message,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data,
        });

        const errorMessage =
          error.response?.data?.message ||
          error.message ||
          "Failed to fetch M3U data";
        setError(errorMessage);
        setTableData([]);
      }
    };
    fetchData();
  }, []);

  const handleRowClick = (index) => {
    if (selectedRows.includes(index)) {
      setSelectedRows(selectedRows.filter((row) => row !== index));
    } else {
      setSelectedRows([...selectedRows, index]);
    }
  };

  const handleAddM3U = async (event) => {
    const files = event.target.files;
    if (!files.length) return;
  
    setUploadProgress({
      total_progress: 0,
      currentFile: files[0].name,
      message: 'Starting upload...',
      totalM3Us: files.length,
      currentM3U: 1,
      is_complete: false,
      error: null
    });
  
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('m3u_files', file);
      });
  
      // Using secureApi (Axios) with progress tracking
      const response = await secureApi.post(`${getApiBaseUrl()}/upload-m3u`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentComplete = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          
          setUploadProgress(prev => ({
            ...prev,
            total_progress: percentComplete,
            message: `Uploading: ${percentComplete}%`
          }));
        }
      });
  
      console.log("Upload response:", response.data);
      
      // Handle successful upload
      setUploadProgress(prev => ({
        ...prev,
        total_progress: 100,
        message: 'Upload complete!',
        is_complete: true
      }));
      
      // Refresh the table after successful upload
      const apiUrl = `${getApiBaseUrl()}/m3us/`;
      const refreshResponse = await secureApi.get(apiUrl);
      
      if (refreshResponse.data) {
        const data = refreshResponse.data;
        const formattedData = Object.entries(data).map(
          ([file, { file_path, creation_date }]) => ({
            file,
            path: file_path,
            creationTime: creation_date,
          })
        );
        setTableData(formattedData);
      }
      
    } catch (error) {
      console.error("Upload error:", error);
      setUploadProgress(prev => ({
        ...prev,
        error: error.response?.data?.detail || error.message || "Upload failed",
        is_complete: true
      }));
    } finally {
      // Reset upload state after a delay
      setTimeout(() => {
        setUploadProgress({
          total_progress: 0,
          currentFile: '',
          message: '',
          totalM3Us: 0,
          currentM3U: 0,
          is_complete: false,
          error: null
        });
        // Clear the file input
        document.getElementById('file-upload').value = '';
      }, 3000);
    }
  };

  const handleDeleteM3U = async () => {
    const selectedData = selectedRows.map((index) => ({
      fileName: tableData[index].file,
      filePath: tableData[index].path,
    }));

    try {
      const deleteUrl = `${getApiBaseUrl()}/delete-m3us`;
      console.log("Deleting at:", deleteUrl, "with data:", selectedData);

      await secureApi.post(deleteUrl, selectedData);
      setTableData((prevData) =>
        prevData.filter((_, index) => !selectedRows.includes(index))
      );
      setSelectedRows([]);
      setError(null);
    } catch (error) {
      console.error("Delete error details:", error);
      const errorMessage =
        error.response?.data?.message ||
        error.message ||
        "Failed to delete files";
      setError(errorMessage);
    }
  };

  useEffect(() => {
    let pollInterval;
    if (loadingTaskId) {
      pollInterval = setInterval(async () => {
        try {
          const progressUrl = `${getApiBaseUrl()}/load-m3u/progress/${loadingTaskId}`;
          const response = await secureApi.get(progressUrl);
          const progress = response.data;
          console.log("Progress update:", progress);

          setLoadingProgress(progress); // Set the new progress data

          if (progress.is_complete) {
            clearInterval(pollInterval);
            setLoadingTaskId(null);
            setTimeout(() => setLoadingProgress(null), 2000); // Clear after a delay
          } else if (progress.error) {
            clearInterval(pollInterval);
            setLoadingTaskId(null);
            setError(progress.error);
          }
        } catch (error) {
          console.error("Progress polling error:", error);
          const errorMessage =
            error.response?.data?.message ||
            error.message ||
            "Failed to fetch progress";
          setError(errorMessage);
          setLoadingProgress(null);
          clearInterval(pollInterval);
          setLoadingTaskId(null);
        }
      }, 1000);
    }
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [loadingTaskId]);

  const handleLoadM3U = async () => {
    const selectedM3Us = selectedRows.map((index) => ({
      fileName: tableData[index].file,
      filePath: tableData[index].path,
    }));

    if (selectedM3Us.length > 0) {
      try {
        const loadUrl = `${getApiBaseUrl()}/load-m3u`;
        console.log("Loading M3Us at:", loadUrl, "with data:", selectedM3Us);

        setLoadingProgress({
          current_stage: "Initializing...",
          total_progress: 0,
          error: null,
        });

        const response = await secureApi.post(loadUrl, selectedM3Us);
        console.log("Load M3U response:", response.data);

        setLoadingTaskId(response.data.task_id);
        setError(null);
      } catch (error) {
        console.error("Load error details:", error);
        const errorMessage =
          error.response?.data?.message ||
          error.message ||
          "Failed to start loading process";
        setError(errorMessage);
        setLoadingProgress(null);
      }
    } else {
      setError("No M3Us selected to load.");
    }
  };

  return (
    <div className="container mt-4">
      {error && (
        <div
          className="alert alert-danger alert-dismissible fade show"
          role="alert"
        >
          {error}
          <button
            type="button"
            className="btn-close"
            onClick={() => setError(null)}
            aria-label="Close"
          ></button>
        </div>
      )}

      <div className="row">
        <div className="col">
          <input
            type="file"
            multiple
            accept=".m3u,.m3u8"
            style={{ display: "none" }}
            onChange={handleAddM3U}
            id="file-upload"
          />

          <div className="table-responsive">
            <table className="table table-hover">
              <thead className="table-light">
                <tr>
                  <th>M3U File</th>
                  <th>M3U Full Path</th>
                  <th>Creation Time</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, index) => (
                  <tr
                    key={index}
                    className={
                      selectedRows.includes(index) ? "table-active" : ""
                    }
                    onClick={() => handleRowClick(index)}
                    style={{ cursor: "pointer" }}
                  >
                    <td>{row.file}</td>
                    <td>{row.path}</td>
                    <td>{row.creationTime}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="btn-group mt-3 mb-3">
            <button
              onClick={() => document.getElementById("file-upload").click()}
              className="btn btn-primary"
            >
              Add M3U
            </button>
            <button
              onClick={handleDeleteM3U}
              className="btn btn-danger"
              disabled={selectedRows.length === 0}
            >
              Delete M3Us
            </button>
            <button
              onClick={handleLoadM3U}
              className="btn btn-success"
              disabled={selectedRows.length === 0 || loadingProgress !== null}
            >
              {loadingProgress ? "Loading..." : "Load M3U"}
            </button>
          </div>

          {loadingProgress && (
            <div className="card mt-4">
              <div className="card-body">
                <h5 className="card-title">Loading Progress</h5>
                <div className="mb-3">
                  <div className="text-muted small mb-2">
                    Status: {loadingProgress.current_stage}
                  </div>
                  <div className="progress" style={{ height: "25px" }}>
                    <div
                      className="progress-bar bg-success progress-bar-striped progress-bar-animated fw-bold"
                      role="progressbar"
                      style={{
                        width: `${loadingProgress.total_progress || 0}%`,
                        borderRadius: "0.25rem",
                        transition: "width 0.5s ease",
                      }}
                      aria-valuenow={loadingProgress.total_progress || 0}
                      aria-valuemin="0"
                      aria-valuemax="100"
                    >
                      {Math.round(loadingProgress.total_progress || 0)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <M3UProgress processingProgress={uploadProgress} />
        </div>
      </div>
    </div>
  );
};

export default M3UManagement;

