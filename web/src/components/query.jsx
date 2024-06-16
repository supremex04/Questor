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
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
            <div className="flex flex-col items-center justify-center w-full max-w-3xl p-6 space-y-6">
                {answer && (
                    <div className="bg-gray-800 p-4 rounded-2xl shadow-lg w-full">
                        <h3 className="text-lg font-semibold">Answer:</h3>
                        <p>{answer}</p>
                    </div>
                )}
                {loading && <p>Loading...</p>}
            </div>
            <form onSubmit={handleSubmit} className="w-full max-w-3xl p-6 fixed bottom-10 flex items-center space-x-2">
                <input
                    type="text"
                    id="question"
                    name="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="flex-grow py-3 px-4 bg-gray-700 border border-gray-600 rounded-full text-white focus:outline-none focus:border-blue-500"
                    autoComplete="off"
                />
                <button
                    type="submit"
                    className="py-3 px-4 bg-blue-600 hover:bg-blue-700 rounded-full transition duration-200"
                >
                    Submit
                </button>
            </form>
        </div>
    );
};

export default QueryComponent;
