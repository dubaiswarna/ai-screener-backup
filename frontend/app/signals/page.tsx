'use client';

import { useEffect, useState } from 'react';
import { apiClient, Signal } from '@/lib/api';
import SignalCard from '@/components/SignalCard';
import CreateSignalForm from '@/components/CreateSignalForm';

export default function SignalsPage() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [minConfidence, setMinConfidence] = useState(50);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    fetchSignals();
  }, [minConfidence]);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getSignals(minConfidence, 100);
      setSignals(data);
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignalCreated = () => {
    fetchSignals();
    setShowCreateForm(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Trading Signals</h1>
          <p className="text-gray-600 mt-1">
            View and manage AI-generated trading signals
          </p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
        >
          {showCreateForm ? 'Cancel' : '+ Create Signal'}
        </button>
      </div>

      {showCreateForm && (
        <CreateSignalForm onSuccess={handleSignalCreated} />
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Active Signals</h2>
          <div className="flex items-center space-x-4">
            <label className="text-sm text-gray-600">
              Min Confidence:
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-32"
            />
            <span className="text-sm font-medium w-12">
              {minConfidence}%
            </span>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded animate-pulse"></div>
            ))}
          </div>
        ) : signals.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p>No signals found with {minConfidence}%+ confidence.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {signals.map((signal, index) => (
              <SignalCard key={index} signal={signal} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

