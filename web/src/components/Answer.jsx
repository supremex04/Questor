import React from 'react';

const Answer = ({ answer, loading }) => {
    return (
        <div className="flex flex-col items-center justify-center w-full max-w-3xl p-6 space-y-6">
            {answer && (
                <div className="bg-gray-800 p-4 rounded-2xl shadow-lg w-full">
                    <h3 className="text-lg font-semibold">answer:</h3>
                    <p>{answer}</p>
                </div>
            )}
            {loading && <div className="loader"></div>}
        </div>
    );
};

export default Answer;
