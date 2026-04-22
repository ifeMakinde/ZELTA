import React, { ReactNode } from "react";

function Widget({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`border border-gray-100 shadow-sm ${className}`}>
      {children}
    </div>
  );
}

export default Widget;
