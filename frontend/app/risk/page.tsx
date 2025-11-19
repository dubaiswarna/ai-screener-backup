'use client';

import { useEffect, useState } from 'react';
import { apiClient, RiskReport } from '@/lib/api';
import { AlertTriangle, Shield, TrendingDown } from 'lucide-react';

export default function RiskPage() {
  const [report, setReport] = useState<RiskReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRiskReport();
  }, []);

  const fetchRiskReport = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getRiskReport();
      setReport(data);
    } catch (error) {
      console.error('Error fetching risk report:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'LOW':
        return 'bg-green-100 text-green-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
      case 'HIGH':
        return 'bg-orange-100 text-orange-800';
      case 'CRITICAL':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-500">Failed to load risk report.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Risk Report</h1>
        <p className="text-gray-600 mt-1">
          Comprehensive risk analysis and portfolio health
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">
            Risk Overview
          </h2>
          <span
            className={`px-4 py-2 rounded-lg font-medium ${getRiskLevelColor(
              report.risk_level
            )}`}
          >
            {report.risk_level} Risk
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Total Capital</p>
            <p className="text-2xl font-bold text-gray-900">
              ₹{report.total_capital.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Invested Amount</p>
            <p className="text-2xl font-bold text-gray-900">
              ₹{report.invested_amount.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Available Cash</p>
            <p className="text-2xl font-bold text-gray-900">
              ₹{report.available_cash.toLocaleString('en-IN')}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Portfolio Heat</p>
            <p className="text-2xl font-bold text-gray-900">
              {report.portfolio_heat.toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Risk Metrics
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <TrendingDown className="w-5 h-5 text-red-600" />
                <span className="text-gray-700">Max Drawdown</span>
              </div>
              <span className="text-lg font-semibold text-red-600">
                {report.max_drawdown.toFixed(2)}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-blue-600" />
                <span className="text-gray-700">Sharpe Ratio</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {report.sharpe_ratio.toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-purple-600" />
                <span className="text-gray-700">Sortino Ratio</span>
              </div>
              <span className="text-lg font-semibold text-gray-900">
                {report.sortino_ratio.toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-orange-600" />
                <span className="text-gray-700">VaR (95%)</span>
              </div>
              <span className="text-lg font-semibold text-orange-600">
                ₹{report.var_95.toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Performance Summary
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Total P&L</span>
              <span
                className={`text-lg font-semibold ${
                  report.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                ₹{report.total_pnl.toLocaleString('en-IN')}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Total P&L %</span>
              <span
                className={`text-lg font-semibold ${
                  report.total_pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {report.total_pnl_pct >= 0 ? '+' : ''}
                {report.total_pnl_pct.toFixed(2)}%
              </span>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Risk Assessment</p>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm text-gray-700">
                  Your portfolio is currently at{' '}
                  <span className="font-semibold">
                    {report.portfolio_heat.toFixed(1)}% heat
                  </span>
                  , which indicates a{' '}
                  <span className="font-semibold">{report.risk_level}</span>{' '}
                  risk level. Consider diversifying if heat exceeds 80%.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

