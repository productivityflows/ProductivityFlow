import React from 'react';

export const Card = ({ children, className }) => <div className={`bg-white border rounded-xl shadow-sm ${className}`}>{children}</div>;
export const CardHeader = ({ children, className }) => <div className={`p-6 border-b ${className}`}>{children}</div>;
export const CardTitle = ({ children, className }) => <h3 className={`text-lg font-semibold text-gray-800 ${className}`}>{children}</h3>;
export const CardContent = ({ children, className }) => <div className={`p-6 ${className}`}>{children}</div>;