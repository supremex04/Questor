import React, { useState } from 'react';
import Search from './Search';
import Answer from './Answer';

const QueryComponent = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(false);

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
