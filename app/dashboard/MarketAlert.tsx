import { Activity } from "lucide-react";

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
    return <div className="h-10 bg-gray-200 rounded-xl animate-pulse" />;
  }

  if (error) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-xl bg-red-50 text-sm">
        <Activity color="red" size={20} />
        <p className="font-medium text-red-600">Market signal unavailable</p>
      </div>
    );
  }

  if (!bayse_market) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 text-sm">
        <Activity color="gray" size={20} />
        <p className="font-medium text-gray-400">Awaiting market signal...</p>
      </div>
    );
  }

  // crowd_yes is a decimal fraction (0–1) from the API — convert to percentage for display
  const fearPct = Math.round((crowd_yes ?? 0) * 100);

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-orange-50 text-sm">
      <Activity color="orange" size={20} />
      <p className="font-medium">
        {bayse_market}: <span className="text-orange-600 font-bold">{fearPct}%</span> crowd fear
      </p>
    </div>
  );
}