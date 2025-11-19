'use client';

import { Signal } from '@/lib/api';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { clsx } from 'clsx';

interface SignalCardProps {
  signal: Signal;
}

export default function SignalCard({ signal }: SignalCardProps) {
  const isBuy = signal.signal_type.toUpperCase() === 'BUY';
  const confidenceColor = 
    signal.confidence >= 80 ? 'text-green-600' :
    signal.confidence >= 60 ? 'text-yellow-600' :
    'text-orange-600';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {signal.symbol.replace('NSE_', '')}
          </h3>
          <div className="flex items-center space-x-2 mt-1">
            {isBuy ? (
              <TrendingUp className="w-4 h-4 text-green-600" />
            ) : (
              <TrendingDown className="w-4 h-4 text-red-600" />
            )}
            <span
              className={clsx(
                'text-sm font-medium',
                isBuy ? 'text-green-600' : 'text-red-600'
              )}
            >
              {signal.signal_type}
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className={clsx('text-lg font-bold', confidenceColor)}>
            {signal.confidence.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Confidence</div>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Entry Price:</span>
          <span className="font-medium">₹{signal.entry_price.toFixed(2)}</span>
        </div>
        {signal.target_price && (
          <div className="flex justify-between">
            <span className="text-gray-600">Target:</span>
            <span className="font-medium text-green-600">
              ₹{signal.target_price.toFixed(2)}
            </span>
          </div>
        )}
        {signal.stop_loss && (
          <div className="flex justify-between">
            <span className="text-gray-600">Stop Loss:</span>
            <span className="font-medium text-red-600">
              ₹{signal.stop_loss.toFixed(2)}
            </span>
          </div>
        )}
        {signal.risk_reward_ratio && (
          <div className="flex justify-between pt-2 border-t border-gray-100">
            <span className="text-gray-600">Risk/Reward:</span>
            <span className="font-medium">
              {signal.risk_reward_ratio.toFixed(2)}:1
            </span>
          </div>
        )}
      </div>

      {signal.model_name && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="text-xs text-gray-500">
            Model: {signal.model_name}
          </div>
        </div>
      )}
    </div>
  );
}

