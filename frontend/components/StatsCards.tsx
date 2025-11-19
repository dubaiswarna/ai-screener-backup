'use client';

import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  DollarSign,
  Briefcase
} from 'lucide-react';

interface Stats {
  signals: {
    active: number;
    total_today: number;
  };
  portfolio: {
    total_capital: number;
    current_value: number;
    total_pnl: number;
    total_pnl_pct: number;
  };
  trades: {
    open: number;
    closed_30d: number;
  };
}

export default function StatsCards() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiClient.getStatsOverview();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="bg-white rounded-lg shadow p-6 animate-pulse"
          >
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return <div>Failed to load statistics</div>;
  }

  const cards = [
    {
      title: 'Active Signals',
      value: stats.signals.active,
      icon: Activity,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Portfolio Value',
      value: `₹${(stats.portfolio.current_value || 0).toLocaleString('en-IN')}`,
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Total P&L',
      value: `₹${(stats.portfolio.total_pnl || 0).toLocaleString('en-IN')}`,
      icon: stats.portfolio.total_pnl >= 0 ? TrendingUp : TrendingDown,
      color: stats.portfolio.total_pnl >= 0 ? 'text-green-600' : 'text-red-600',
      bgColor: stats.portfolio.total_pnl >= 0 ? 'bg-green-100' : 'bg-red-100',
      subtitle: `${(stats.portfolio.total_pnl_pct || 0).toFixed(2)}%`,
    },
    {
      title: 'Open Trades',
      value: stats.trades.open,
      icon: Briefcase,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <div
            key={index}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">
                  {card.title}
                </p>
                <p className={`text-2xl font-bold mt-2 ${card.color}`}>
                  {card.value}
                </p>
                {card.subtitle && (
                  <p className="text-sm text-gray-500 mt-1">{card.subtitle}</p>
                )}
              </div>
              <div className={`${card.bgColor} p-3 rounded-lg`}>
                <Icon className={`w-6 h-6 ${card.color}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

