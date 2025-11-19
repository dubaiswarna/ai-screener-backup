'use client';

import { useState } from 'react';
import { apiClient, Signal } from '@/lib/api';

interface CreateSignalFormProps {
  onSuccess: () => void;
}

export default function CreateSignalForm({ onSuccess }: CreateSignalFormProps) {
  const [formData, setFormData] = useState<Partial<Signal>>({
    symbol: '',
    signal_type: 'BUY',
    confidence: 75,
    entry_price: 0,
    target_price: 0,
    stop_loss: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiClient.createSignal(formData as Signal);
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create signal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Create New Signal
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Symbol
            </label>
            <input
              type="text"
              required
              value={formData.symbol}
              onChange={(e) =>
                setFormData({ ...formData, symbol: e.target.value })
              }
              placeholder="NSE_RELIANCE"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Signal Type
            </label>
            <select
              value={formData.signal_type}
              onChange={(e) =>
                setFormData({ ...formData, signal_type: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confidence (%)
            </label>
            <input
              type="number"
              required
              min="0"
              max="100"
              value={formData.confidence}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  confidence: Number(e.target.value),
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Entry Price (₹)
            </label>
            <input
              type="number"
              required
              step="0.01"
              value={formData.entry_price || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  entry_price: Number(e.target.value),
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Price (₹)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.target_price || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  target_price: Number(e.target.value) || undefined,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stop Loss (₹)
            </label>
            <input
              type="number"
              step="0.01"
              value={formData.stop_loss || ''}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  stop_loss: Number(e.target.value) || undefined,
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onSuccess}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Creating...' : 'Create Signal'}
          </button>
        </div>
      </form>
    </div>
  );
}

