import React from "react";
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from "lucide-react";
import type { SimulationResponse } from "@/types/zelta";

interface SimulationResultsProps {
  result: SimulationResponse;
}

export default function SimulationResults({ result }: SimulationResultsProps) {
  const { data, simulation_type } = result;

  if (simulation_type === "side_hustle") {
    return (
      <div className="mt-6 bg-white border-2 border-gray-100 rounded-2xl p-4 lg:p-6">
        <div className="flex gap-3 items-start mb-4">
          <div className="bg-emerald-100 rounded-full w-10 h-10 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-gray-800 font-bold text-lg">Simulation Results</h2>
            <p className="text-gray-500 text-sm">Bayesian Monte Carlo projection</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-4">
            <h3 className="text-gray-500 font-bold text-sm">Kelly Allocation</h3>
            <p className="text-emerald-600 font-bold text-2xl">
              ₦{data.kelly_allocation?.toLocaleString() || "0"}
            </p>
            <p className="text-gray-500 text-xs mt-1">Safe investment amount</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
            <h3 className="text-gray-500 font-bold text-sm">Expected Return</h3>
            <p className="text-blue-600 font-bold text-2xl">
              ₦{data.expected_return?.toLocaleString() || "0"}
            </p>
            <p className="text-gray-500 text-xs mt-1">Average projection</p>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-4">
            <h3 className="text-gray-500 font-bold text-sm">Confidence Score</h3>
            <p className="text-orange-600 font-bold text-2xl">
              {data.confidence_score || 0}%
            </p>
            <p className="text-gray-500 text-xs mt-1">Decision quality</p>
          </div>
        </div>

        {/* Probability Bands */}
        {data.probability_bands && (
          <div className="mb-6">
            <h3 className="text-gray-800 font-bold text-md mb-3">Probability Bands</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center bg-red-50 border border-red-200 rounded-2xl p-3">
                <span className="text-gray-700 font-medium">Low Risk (25%)</span>
                <span className="text-red-600 font-bold">₦{data.probability_bands.low.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center bg-yellow-50 border border-yellow-200 rounded-2xl p-3">
                <span className="text-gray-700 font-medium">Medium Risk (50%)</span>
                <span className="text-yellow-600 font-bold">₦{data.probability_bands.medium.toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center bg-green-50 border border-green-200 rounded-2xl p-3">
                <span className="text-gray-700 font-medium">High Risk (25%)</span>
                <span className="text-green-600 font-bold">₦{data.probability_bands.high.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}

        {/* Recommendation */}
        {data.recommendation && (
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
            <div className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-gray-800 font-bold text-sm">ZELTA Recommendation</h3>
                <p className="text-gray-700 text-sm mt-1">{data.recommendation}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  if (simulation_type === "savings") {
    return (
      <div className="mt-6 bg-white border-2 border-gray-100 rounded-2xl p-4 lg:p-6">
        <div className="flex gap-3 items-start mb-4">
          <div className="bg-blue-100 rounded-full w-10 h-10 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h2 className="text-gray-800 font-bold text-lg">Savings Projection</h2>
            <p className="text-gray-500 text-sm">Week-by-week trajectory</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
            <h3 className="text-gray-500 font-bold text-sm">Weeks to Target</h3>
            <p className="text-blue-600 font-bold text-2xl">
              {data.weeks_to_target || 0} weeks
            </p>
            <p className="text-gray-500 text-xs mt-1">Estimated timeline</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
            <h3 className="text-gray-500 font-bold text-sm">Risk Level</h3>
            <p className="text-green-600 font-bold text-2xl capitalize">
              {data.risk_level || "Low"}
            </p>
            <p className="text-gray-500 text-xs mt-1">Based on obligations</p>
          </div>
        </div>

        {/* Weekly Trajectory */}
        {data.weekly_trajectory && data.weekly_trajectory.length > 0 && (
          <div className="mb-6">
            <h3 className="text-gray-800 font-bold text-md mb-3">Weekly Progress</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {data.weekly_trajectory.slice(0, 8).map((week) => (
                <div key={week.week} className="flex justify-between items-center p-3 rounded-2xl border border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      week.risk_status === 'green' ? 'bg-green-400' :
                      week.risk_status === 'amber' ? 'bg-yellow-400' : 'bg-red-400'
                    }`} />
                    <span className="text-gray-700 font-medium">Week {week.week}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-gray-800 font-bold">₦{week.saved_amount.toLocaleString()}</span>
                    {week.notes && (
                      <p className="text-gray-500 text-xs mt-1">{week.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendation */}
        {data.recommendation && (
          <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
            <div className="flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-gray-800 font-bold text-sm">Savings Strategy</h3>
                <p className="text-gray-700 text-sm mt-1">{data.recommendation}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
}