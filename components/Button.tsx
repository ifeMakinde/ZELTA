import React from "react";

function Button({
  children,
  onClick,
  className,
  disabled = false,
  type = "submit",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  className: string;
  disabled?: boolean;
  type?: "submit" | "button" | "reset";
}) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {children}
    </button>
  );
}

export default Button;