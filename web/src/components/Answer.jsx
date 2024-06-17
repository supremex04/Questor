import React from 'react';

const Answer = ({ history, loading }) => {
    return (
        <div className="flex flex-col items-center justify-center w-full max-w-4xl p-6 space-y-6 h-full">
            {loading && <div className="loader"></div>}
            {history.length > 0 ? (
                <div className="flex flex-col space-y-4 w-full max-w-4xl">
                    {history.map((item, index) => (
                        <div key={index} className="bg-gray-800 p-4 rounded-2xl shadow-lg transition transform hover:scale-102 duration-200">
                            <div className="mb-4">
                                <h3 className="text-lg font-semibold">Question:</h3>
                                <p className="mb-2">{item.question}</p>
                                <h3 className="text-lg font-semibold">Answer:</h3>
                                <p>{item.answer}</p>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-gray-500"></p>
            )}
        </div>
    );
};

export default Answer;
