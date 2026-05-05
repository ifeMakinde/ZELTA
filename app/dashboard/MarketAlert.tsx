import { Activity } from "lucide-react";
// import { BrainData } from "@/types/zelta";

interface MarketAlertProps {
  fear?: number;
  bayse_market?: string;
  loading?: boolean;
  error?: string | null;
}

export default function MarketAlert({
  fear,
  bayse_market,
  loading,
  error,
}: MarketAlertProps) {
  if (loading) {
    return <div className="h-8 bg-gray-200 rounded-md animate-pulse"></div>;
  }

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-orange-50 text-sm">
      <Activity color="orange" size={20} />
      <p className="font-medium">{` ${bayse_market} : ${Math.round(fear ?? 0)}% fear`}</p>
    </div>
  );
}