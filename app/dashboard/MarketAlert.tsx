import { Activity } from "lucide-react";
// import { BrainData } from "@/types/zelta";

interface MarketAlertProps {
  crowd_yes?: number;
  bayse_market?: string;
  loading?: boolean;
  error?: string | null;
}

export default function MarketAlert({
  crowd_yes,
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
      <p className="font-medium">{` ${bayse_market} : ${Math.floor(crowd_yes ?? 0) * 100}% fear`}</p>
    </div>
  );
}