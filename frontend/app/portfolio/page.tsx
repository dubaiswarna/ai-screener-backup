'use client';

import { useEffect, useState } from 'react';
import { apiClient, PortfolioPosition, PortfolioSummary } from '@/lib/api';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function PortfolioPage() {
  const [positions, setPositions] = useState<PortfolioPosition[]>([]);
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getPortfolio();
      setPositions(data.positions || []);
      setSummary(data.summary || null);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
        <p className="text-gray-600 mt-1">Your current positions and P&L</p>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Total Capital</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              ₹{summary.total_capital.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Invested Amount</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              ₹{summary.invested_amount.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Current Value</p>
            <p className="text-2xl font-bold text-gray-900 mt-2">
              ₹{summary.current_value.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm text-gray-600">Total P&L</p>
            <div className="flex items-center space-x-2 mt-2">
              {summary.total_pnl >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-600" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-600" />
              )}
              <p
                className={`text-2xl font-bold ${
                  summary.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                ₹{summary.total_pnl.toLocaleString('en-IN')}
              </p>
            </div>
            <p
              className={`text-sm mt-1 ${
                summary.total_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {summary.total_pnl_pct >= 0 ? '+' : ''}
              {summary.total_pnl_pct.toFixed(2)}%
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Positions
        </h2>
        {positions.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No open positions.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">
                    Symbol
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Quantity
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Entry Price
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    Current Price
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    P&L
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">
                    P&L %
                  </th>
                </tr>
              </thead>
              <tbody>
                {positions.map((position, index) => (
                  <tr
                    key={index}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4 font-medium">
                      {position.symbol.replace('NSE_', '')}
                    </td>
                    <td className="text-right py-3 px-4">
                      {position.quantity}
                    </td>
                    <td className="text-right py-3 px-4">
                      ₹{position.entry_price.toFixed(2)}
                    </td>
                    <td className="text-right py-3 px-4">
                      ₹{position.current_price.toFixed(2)}
                    </td>
                    <td
                      className={`text-right py-3 px-4 font-medium ${
                        position.profit_loss >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      ₹{position.profit_loss.toLocaleString('en-IN', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td
                      className={`text-right py-3 px-4 font-medium ${
                        position.profit_loss_pct >= 0
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {position.profit_loss_pct >= 0 ? '+' : ''}
                      {position.profit_loss_pct.toFixed(2)}%
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

