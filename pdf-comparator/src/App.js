import React, { useState } from "react";
import axios from "axios";

function App() {
    const [file1, setFile1] = useState(null);
    const [file2, setFile2] = useState(null);
    const [results, setResults] = useState([]);

    const handleUpload = async () => {
        if (!file1 || !file2) {
            alert("Please upload both files");
            return;
        }

        const formData = new FormData();
        formData.append("file1", file1);
        formData.append("file2", file2);

        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/compare",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            setResults(response.data);
        } catch (error) {
            console.error("Error uploading files", error);
        }
    };

    return (
        <div>
            <h1>PDF Comparison Tool</h1>
            <input type="file" onChange={(e) => setFile1(e.target.files[0])} />
            <input type="file" onChange={(e) => setFile2(e.target.files[0])} />
            <button onClick={handleUpload}>Compare</button>

            {results.length > 0 && (
                <table border="1">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Description</th>
                            <th>Your Estimate</th>
                            <th>Carrier Estimate</th>
                            <th>Difference</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results.map((row, index) => (
                            <tr key={index}>
                                <td>{row.Category}</td>
                                <td>{row.Description}</td>
                                <td>{row.RCV_Value_Your_Estimate}</td>
                                <td>{row.RCV_Value_Carrier_Estimate}</td>
                                <td>{row.Difference_RCV}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default App;
