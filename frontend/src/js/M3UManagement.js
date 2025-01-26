import '../css/M3UManagement.css';
import getApiBaseUrl from './apiConfig';
import React, { useState, useEffect } from 'react';

const M3UManagement = () => {
  const [tableData, setTableData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [fileInput, setFileInput] = useState(null); // State to hold file input
  const [uploadProgress, setUploadProgress] = useState(0); // State for upload progress

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${getApiBaseUrl()}/m3us/`);
        const data = await response.json();
        const formattedData = Object.entries(data).map(([file, { file_path, creation_date }]) => ({
          file,
          path: file_path,
          creationTime: creation_date,
        }));
        setTableData(formattedData);
      } catch (error) {
        console.error('Error fetching data:', error);
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
    const files = event.target.files; // Get the selected files
    if (files.length > 0) {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
      }
  
      const xhr = new XMLHttpRequest();
      xhr.open('POST', `${getApiBaseUrl()}/upload-m3u`, true);
  
      // Update progress
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setUploadProgress(percentComplete); // Update the progress state
        }
      };
  
      xhr.onload = () => {
        if (xhr.status === 200) {
          const newFiles = JSON.parse(xhr.responseText);
          console.log('M3Us added successfully:', newFiles);
          setTableData(prevData => [...prevData, ...newFiles]); // Update table with new files
          setFileInput(null); // Clear file input
          setUploadProgress(0); // Reset progress
        } else {
          console.error('Error uploading M3Us:', xhr.statusText);
        }
      };
  
      xhr.onerror = () => {
        console.error('Error during the upload:', xhr.statusText);
      };
  
      xhr.send(formData);
    }
  };

  const handleUploadProgress = (event) => {
    if (event.lengthComputable) {
      const percentComplete = (event.loaded / event.total) * 100;
      setUploadProgress(percentComplete); // Update the progress state
    }
  };

  const handleDeleteM3U = async () => {
    const selectedData = selectedRows.map(index => ({
      fileName: tableData[index].file,
      filePath: tableData[index].path,
    }));

    try {
      const response = await fetch(`${getApiBaseUrl()}/delete-m3us`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('M3Us deleted successfully:', result);
        setTableData(prevData => prevData.filter((_, index) => !selectedRows.includes(index)));
        setSelectedRows([]);
      } else {
        console.error('Error deleting M3Us:', response.statusText);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleLoadM3U = async () => {
    const selectedM3Us = selectedRows.map(index => ({
      fileName: tableData[index].file,
      filePath: tableData[index].path,
    }));

    if (selectedM3Us.length > 0) {
      try {
        const response = await fetch(`${getApiBaseUrl()}/load-m3u`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(selectedM3Us),
        });

        if (response.ok) {
          const result = await response.json();
          console.log('M3Us loaded successfully:', result);
        } else {
          console.error('Error loading M3Us:', response.statusText);
        }
      } catch (error) {
        console.error('Error:', error);
      }
    } else {
      console.warn('No M3Us selected to load.');
    }
  };

  return (
    <div className="m3u-management">
      <input
        type="file"
        multiple
        accept=".m3u,.m3u8"
        style={{ display: 'none' }} // Hide the file input
        onChange={handleAddM3U} // Call handleAddM3U when files are selected
        id="file-upload" // Add an ID for the label to reference
      />

      <div className="table-container">
        <table>
          <thead>
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
                className={selectedRows.includes(index) ? 'selected-row' : ''}
                onClick={() => handleRowClick(index)}
              >
                <td>{row.file}</td>
                <td>{row.path}</td>
                <td>{row.creationTime}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="button-container">
        <button onClick={() => document.getElementById('file-upload').click()} className="add-m3u-button">
          Add M3U
        </button>
        <button onClick={handleDeleteM3U} className="add-m3u-button">Delete M3Us</button>
        <button onClick={handleLoadM3U} className="add-m3u-button">Load M3U</button>
      </div>

      {/* Progress Bar */}
      {uploadProgress > 0 && (
        <div className="progress-container">
          <div className="progress-bar" style={{ width: `${uploadProgress}%` }}></div>
          <span>{Math.round(uploadProgress)}% uploaded</span>
        </div>
      )}
    </div>
  );
};

export default M3UManagement;