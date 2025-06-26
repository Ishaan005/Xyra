import React from "react";

/**
 * ActivityCostPreview component
 * Renders a cost preview for activity-based pricing models.
 *
 * Props:
 * - pricePerUnit: string
 * - baseAgentFee: string
 * - minimumCharge: string
 * - unitType: string
 * - volumePricingEnabled: boolean
 * - volumeTier1Threshold: string
 * - volumeTier1Price: string
 * - volumeTier2Threshold: string
 * - volumeTier2Price: string
 * - volumeTier3Threshold: string
 * - volumeTier3Price: string
 */

interface ActivityCostPreviewProps {
  pricePerUnit: string;
  baseAgentFee: string;
  minimumCharge: string;
  unitType: string;
  volumePricingEnabled: boolean;
  volumeTier1Threshold: string;
  volumeTier1Price: string;
  volumeTier2Threshold: string;
  volumeTier2Price: string;
  volumeTier3Threshold: string;
  volumeTier3Price: string;
}

export default function ActivityCostPreview({
  pricePerUnit,
  baseAgentFee,
  minimumCharge,
  unitType,
  volumePricingEnabled,
  volumeTier1Threshold,
  volumeTier1Price,
  volumeTier2Threshold,
  volumeTier2Price,
  volumeTier3Threshold,
  volumeTier3Price,
}: ActivityCostPreviewProps) {
  return (
    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h4 className="font-medium text-sm mb-3 text-blue-800">💡 Cost Preview</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="text-xs text-blue-700">Example usage:</label>
          <input
            type="number"
            placeholder="10000"
            className="w-full mt-1 px-2 py-1 text-sm border rounded"
            onChange={(e) => {
              const units = parseInt(e.target.value) || 0;
              const agents = 1;
              const basePrice = parseFloat(pricePerUnit) || 0;
              const baseFee = parseFloat(baseAgentFee) || 0;
              const minCharge = parseFloat(minimumCharge) || 0;
              let cost = baseFee * agents;
              if (volumePricingEnabled) {
                const tier1Threshold = parseInt(volumeTier1Threshold) || 0;
                const tier1Price = parseFloat(volumeTier1Price) || basePrice;
                if (units <= tier1Threshold) {
                  cost += units * tier1Price;
                } else {
                  cost += tier1Threshold * tier1Price;
                  const remainingUnits = units - tier1Threshold;
                  const tier2Threshold = parseInt(volumeTier2Threshold) || 0;
                  const tier2Price = parseFloat(volumeTier2Price) || basePrice;
                  if (remainingUnits <= (tier2Threshold - tier1Threshold)) {
                    cost += remainingUnits * tier2Price;
                  } else {
                    cost += (tier2Threshold - tier1Threshold) * tier2Price;
                    const finalUnits = remainingUnits - (tier2Threshold - tier1Threshold);
                    const tier3Price = parseFloat(volumeTier3Price) || basePrice;
                    cost += finalUnits * tier3Price;
                  }
                }
              } else {
                cost += units * basePrice;
              }
              cost = Math.max(cost, minCharge);
              const preview = document.getElementById('cost-preview');
              if (preview) {
                preview.textContent = `$${cost.toFixed(2)}`;
              }
            }}
          />
          <span className="text-xs text-blue-600">{unitType}s</span>
        </div>
        <div>
          <label className="text-xs text-blue-700">Estimated cost:</label>
          <div id="cost-preview" className="mt-1 px-2 py-1 bg-white border rounded text-sm font-mono">
            $0.00
          </div>
        </div>
      </div>
      <p className="text-xs text-blue-600 mt-2">
        * Preview includes base agent fee{volumePricingEnabled ? " and volume discounts" : ""}
      </p>
    </div>
  );
}
