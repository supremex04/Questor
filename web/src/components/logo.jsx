import React from 'react';

const Logo = () => {
    return (
        <div className="flex items-center space-x-2">
            <div className="relative w-12 h-12">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 100 100"
                    className="w-full h-full"
                >
                    <circle cx="45" cy="45" r="40" stroke="#1E40AF" strokeWidth="5" fill="none" />
                    <line x1="75" y1="75" x2="95" y2="95" stroke="#1E40AF" strokeWidth="5" />
                    
                    {/* Nodes and connections */}
                    <circle cx="30" cy="30" r="4" fill="#16A34A" />
                    <circle cx="60" cy="30" r="4" fill="#16A34A" />
                    <circle cx="45" cy="55" r="4" fill="#16A34A" />
                    <line x1="30" y1="30" x2="60" y2="30" stroke="#16A34A" strokeWidth="2" />
                    <line x1="30" y1="30" x2="45" y2="55" stroke="#16A34A" strokeWidth="2" />
                    <line x1="60" y1="30" x2="45" y2="55" stroke="#16A34A" strokeWidth="2" />
                </svg>
            </div>
            <div className="text-2xl font-semibold text-white">Questor</div>
        </div>
    );
};

export default Logo;
