'use client';

import { useEffect, useState } from 'react';
import { apiClient, Trade } from '@/lib/api';
import { format } from 'date-fns';

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    fetchTrades();
  }, [days]);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getTrades(undefined, days);
      setTrades(data);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toUpperCase()) {
      case 'OPEN':
        return 'bg-blue-100 text-blue-800';
      case 'CLOSED':
        return 'bg-gray-100 text-gray-800';
      case 'STOPPED':
        return 'bg-red-100 text-red-800';
      case 'TARGET_HIT':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trade History</h1>
          <p className="text-gray-600 mt-1">View all your trading activity</p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-600">Period:</label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {trades.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No trades found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Date
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Symbol
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Type
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Quantity
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Entry Price
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Exit Price
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    P&L
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr
                    key={trade.id}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4 text-sm">
                      {format(new Date(trade.entry_date), 'MMM dd, yyyy')}
                    </td>
                    <td className="py-3 px-4 font-medium">
                      {trade.symbol.replace('NSE_', '')}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          trade.trade_type.toUpperCase() === 'BUY'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {trade.trade_type}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">{trade.quantity}</td>
                    <td className="text-right py-3 px-4">
                      ₹{trade.entry_price.toFixed(2)}
                    </td>
                    <td className="text-right py-3 px-4">
                      {trade.exit_price
                        ? `₹${trade.exit_price.toFixed(2)}`
                        : '-'}
                    </td>
                    <td
                      className={`text-right py-3 px-4 font-medium ${
                        trade.profit_loss && trade.profit_loss >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {trade.profit_loss !== undefined
                        ? `₹${trade.profit_loss.toLocaleString('en-IN', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                          })}`
                        : '-'}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                          trade.status
                        )}`}
                      >
                        {trade.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

