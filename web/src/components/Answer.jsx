import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBook, faGlobe } from '@fortawesome/free-solid-svg-icons';

const Answer = ({ history, loading }) => {
    return (
        <div className="flex flex-col items-center justify-center w-full max-w-4xl p-6 space-y-6 h-full">
            {loading && <div className="loader"></div>}
            {history.length > 0 ? (
                <div className="flex flex-col space-y-4 w-full max-w-4xl">
                    {history.map((item, index) => (
                        <div key={index} className="relative bg-gray-800 p-4 rounded-2xl shadow-lg transition transform hover:scale-101 duration-200">
                            <div className="icon-container">
                                {item.urls && item.urls.length > 0 ? (
                                    <FontAwesomeIcon icon={faGlobe} className="icon text-blue-500" />
                                ) : (
                                    <FontAwesomeIcon icon={faBook} className="icon text-blue-500" />
                                )}
                            </div>
                            <div>
                                <p className="mb-2 font-semibold text-xl">{item.question}</p>
                                <div className="text-left text-gray-200">
                                    {Array.isArray(item.answer) ? (
                                        <ul className="list-disc list-inside">
                                            {item.answer.map((point, i) => (
                                                <li key={i}>{point}</li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <p>{item.answer}</p>
                                    )}
                                </div>
                                {item.urls && item.urls.length > 0 && (
                                    <ul className="url-list text-sm mt-2 list-disc" >
                                        {item.urls.map((url, urlIndex) => (
                                            <li key={urlIndex} className="text-left">
                                                <a href={url} className="text-blue-400" target="_blank" rel="noopener noreferrer">{url}</a>
                                            </li>
                                        ))}
                                    </ul>
                                )}
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
