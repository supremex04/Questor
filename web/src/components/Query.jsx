import React, { useState, useEffect } from 'react';
import Search from './Search';
import Answer from './Answer';

const QueryComponent = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        // Add dummy data for testing
        const dummyData = [
            {
                question: "What is the capital of France?",
                answer: "The capital of France is Paris.",
                urls: [
                    "https://example.com/france-capital",
                    "https://example.com/paris-info"
                ]
            },
            {
                question: "What is the tallest mountain in the world?",
                answer: "The tallest mountain in the world is Mount Everest.",
                urls: [
                    "https://example.com/mount-everest",
                    "https://example.com/tallest-mountains"
                ]
            }
        ];
        setHistory(dummyData);
    }, []);

    const addHistory = (question, answer, urls) => {
        setHistory((prevHistory) => [{ question, answer, urls }, ...prevHistory]);
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-start bg-gray-900 text-white p-4 space-y-6">
            <Search addHistory={addHistory} setLoading={setLoading} />
            <Answer history={history} loading={loading} />
        </div>
    );
};

export default QueryComponent;
