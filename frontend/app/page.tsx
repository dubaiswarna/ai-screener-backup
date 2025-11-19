import { Suspense } from 'react';
import Dashboard from '@/components/Dashboard';
import StatsCards from '@/components/StatsCards';

export default function Home() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          🎯 AI Stock Screener
        </h1>
        <p className="text-lg text-gray-600">
          AI-Powered Trading Signals with 86.9% Proven Win Rate
        </p>
      </div>

      <Suspense fallback={<div>Loading stats...</div>}>
        <StatsCards />
      </Suspense>

      <Suspense fallback={<div>Loading dashboard...</div>}>
        <Dashboard />
      </Suspense>
    </div>
  );
}

