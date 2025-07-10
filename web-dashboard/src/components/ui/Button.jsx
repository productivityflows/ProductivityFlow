import React from 'react';

export const Button = ({ children, variant = 'default', size = 'default', ...props }) => {
  const baseStyles = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none";
  
  const sizeStyles = {
    default: "h-10 px-4 py-2",
    sm: "h-9 rounded-md px-3",
  };

  const variantStyles = {
    default: "bg-indigo-600 text-white hover:bg-indigo-700",
    outline: "border border-gray-300 bg-transparent hover:bg-gray-100",
    ghost: "hover:bg-gray-100 hover:text-gray-900",
  };
  
  return <button className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]}`} {...props}>{children}</button>;
};