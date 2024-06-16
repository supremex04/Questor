import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const Search = ({ setAnswer, setLoading }) => {
    const [question, setQuestion] = useState('');
    const textareaRef = useRef(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [question]);

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
        <div className="fixed bottom-20 w-full flex justify-center px-4">
            <form onSubmit={handleSubmit} className="w-full max-w-3xl flex space-x-4">
                <textarea
                    ref={textareaRef}
                    id="question"
                    name="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    className="w-full py-3 px-4 bg-gray-700 border border-gray-600 rounded-3xl text-white focus:outline-none focus:border-blue-500 resize-none overflow-hidden"
                    autoComplete="off"
                    rows="1"
                    style={{ minHeight: '3rem', lineHeight: '1.5rem' }}
                />
                <button
                    type="submit"
                    className="h-12 py-3 px-4 bg-blue-600 hover:bg-blue-700 rounded-full transition duration-200"
                    style={{ alignSelf: 'flex-start' }}
                >
                    Submit
                </button>
            </form>
        </div>
    );
};

export default Search;
