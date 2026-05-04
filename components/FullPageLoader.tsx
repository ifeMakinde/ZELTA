"use client";

interface FullPageLoaderProps {
  show: boolean;
  message?: string;
}

export default function FullPageLoader({
  show,
  message = "Loading...",
}: FullPageLoaderProps) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm">
      <div className="text-center space-y-4">
        {/* Spinner */}
        <div className="flex justify-center">
          <div className="relative w-12 h-12">
            <div
              className="absolute inset-0 rounded-full border-4 border-gray-200"
              style={{
                animation: "spin 3s linear infinite",
              }}
            >
              <div
                className="absolute inset-0 rounded-full border-4 border-transparent border-t-green-500 border-r-green-500"
                style={{
                  animation: "spin 1s linear infinite reverse",
                }}
              />
            </div>
          </div>
        </div>

        {/* Message */}
        <p className="text-sm font-medium text-gray-700">{message}</p>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
