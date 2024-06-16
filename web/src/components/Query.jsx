import React, { useState } from 'react';
import Search from './Search';
import Answer from './Answer';

const QueryComponent = () => {
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white">
            <Answer answer={answer} loading={loading} />
            <Search setAnswer={setAnswer} setLoading={setLoading} />
        </div>
    );
};

export default QueryComponent;
