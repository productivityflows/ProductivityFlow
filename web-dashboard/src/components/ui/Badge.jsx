import React from 'react';

export const Badge = ({ children, variant = 'default' }) => {
    const variantStyles = {
        default: "bg-indigo-600 text-white",
        secondary: "bg-gray-200 text-gray-800",
        outline: "border text-gray-600",
    };

    return (
        <span className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${variantStyles[variant]}`}>
            {children}
        </span>
    );
};