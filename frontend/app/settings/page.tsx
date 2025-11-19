'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';

interface Config {
  total_capital?: number;
  max_risk_per_trade?: number;
  max_portfolio_risk?: number;
  min_confidence?: number;
}

export default function SettingsPage() {
  const [config, setConfig] = useState<Config>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getConfig();
      setConfig(data);
    } catch (error) {
      console.error('Error fetching config:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      await apiClient.updateConfig(config);
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to save settings',
      });
    } finally {
      setSaving(false);
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Configure your trading parameters</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Total Capital (₹)
              </label>
              <input
                type="number"
                value={config.total_capital || ''}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    total_capital: Number(e.target.value) || undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="1000000"
              />
              <p className="text-xs text-gray-500 mt-1">
                Your total trading capital
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Risk Per Trade (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={config.max_risk_per_trade || ''}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    max_risk_per_trade: Number(e.target.value) || undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="2.0"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum risk per trade (recommended: 1-2%)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Max Portfolio Risk (%)
              </label>
              <input
                type="number"
                step="0.1"
                value={config.max_portfolio_risk || ''}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    max_portfolio_risk: Number(e.target.value) || undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="10.0"
              />
              <p className="text-xs text-gray-500 mt-1">
                Maximum total portfolio risk (recommended: 5-10%)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Confidence (%)
              </label>
              <input
                type="number"
                step="1"
                value={config.min_confidence || ''}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    min_confidence: Number(e.target.value) || undefined,
                  })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="70"
              />
              <p className="text-xs text-gray-500 mt-1">
                Minimum AI confidence to consider signals (recommended: 70%+)
              </p>
            </div>
          </div>

          {message && (
            <div
              className={`px-4 py-3 rounded-lg ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {message.text}
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

