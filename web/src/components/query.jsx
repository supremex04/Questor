import React, { useState } from 'react';
import axios from 'axios';

const QueryComponent = () => {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setAnswer('');
        try {
            const response = await axios.post('http://localhost:5000/query', { question });
            setAnswer(response.data.generation);
        } catch (error) {
            console.error("There was an error submitting the question!", error);
            setAnswer('There was an error processing your request. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label>
                    Question:
                    <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {loading && <p>Loading...</p>}
            {answer && (
                <div>
                    <h3>Answer:</h3>
                    <p>{answer}</p>
                </div>
            )}
        </div>
    );
};

export default QueryComponent;
