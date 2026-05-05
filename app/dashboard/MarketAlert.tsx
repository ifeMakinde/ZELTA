import { Activity } from "lucide-react";

interface MarketAlertProps {
  crowd_yes?: number;     // 0-1 decimal from IntelligenceData
  bayse_market?: string;
  bayse_primary?: number; // 0-1 decimal fallback
  loading?: boolean;
  error?: string | null;
}

export default function MarketAlert({
  crowd_yes,
  bayse_market,
  bayse_primary,
  loading,
}: MarketAlertProps) {
  if (loading) {
    return <div className="h-10 bg-gray-100 rounded-xl animate-pulse" />;
  }

  // Both are 0-1 decimals — multiply by 100 for display
  const rawFear = crowd_yes ?? bayse_primary ?? 0;
  const fearPct = Math.round((Number.isFinite(rawFear) ? rawFear : 0) * 100);
  const market = bayse_market || "Bayse Market";

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-orange-50 text-sm">
      <Activity color="orange" size={20} className="shrink-0" />
      <p className="font-medium">{market} : {fearPct}% fear</p>
    </div>
  );
}