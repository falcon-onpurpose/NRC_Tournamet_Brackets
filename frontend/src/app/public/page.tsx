'use client';

import { useState, useEffect } from 'react';
import { 
  TrophyIcon, 
  ClockIcon, 
  UserGroupIcon,
  PlayIcon,
  PauseIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface Tournament {
  id: string;
  name: string;
  status: string;
  start_date: string;
  end_date: string;
}

interface Match {
  id: string;
  tournament_id: string;
  team1_name: string;
  team2_name: string;
  status: string;
  scheduled_time: string;
  arena: string;
  match_type: string;
}

export default function PublicDisplayPage() {
  const [activeTournaments, setActiveTournaments] = useState<Tournament[]>([]);
  const [currentMatch, setCurrentMatch] = useState<Match | null>(null);
  const [upcomingMatches, setUpcomingMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // For now, show placeholder data since public endpoints don't exist yet
    setLoading(false);
    setActiveTournaments([]);
    setCurrentMatch(null);
    setUpcomingMatches([]);
  }, []);

  const getMatchStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getMatchStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return <ClockIcon className="h-5 w-5" />;
      case 'in_progress':
        return <PlayIcon className="h-5 w-5" />;
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5" />;
      case 'cancelled':
        return <XCircleIcon className="h-5 w-5" />;
      default:
        return <ClockIcon className="h-5 w-5" />;
    }
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-black shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-4xl font-bold text-white">
                NRC Tournament
              </h1>
              <p className="mt-1 text-lg text-gray-300">
                Live Tournament Status
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-mono">
                {new Date().toLocaleTimeString('en-US', {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </div>
              <div className="text-sm text-gray-400">
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Info Message */}
        <div className="mb-6 bg-blue-900 border border-blue-700 rounded-lg p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-200">
                Public Display API Coming Soon
              </h3>
              <div className="mt-2 text-sm text-blue-300">
                The public display API is being developed. This page will show live tournament data when available.
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Current Match */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <PlayIcon className="h-6 w-6 mr-2 text-green-400" />
              Current Match
            </h2>
            
            {currentMatch ? (
              <div className="space-y-4">
                <div className="bg-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">Arena {currentMatch.arena}</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMatchStatusColor(currentMatch.status)}`}>
                      {getMatchStatusIcon(currentMatch.status)}
                      <span className="ml-1">{currentMatch.status.replace('_', ' ')}</span>
                    </span>
                  </div>
                  
                  <div className="text-center">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gray-600 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-white">{currentMatch.team1_name}</h3>
                        <p className="text-sm text-gray-400">Team 1</p>
                      </div>
                      <div className="bg-gray-600 rounded-lg p-4">
                        <h3 className="text-lg font-semibold text-white">{currentMatch.team2_name}</h3>
                        <p className="text-sm text-gray-400">Team 2</p>
                      </div>
                    </div>
                    
                    <div className="mt-4 text-center">
                      <span className="text-3xl font-bold text-yellow-400">VS</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 text-center text-sm text-gray-400">
                    {currentMatch.match_type} • {formatTime(currentMatch.scheduled_time)}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <PauseIcon className="mx-auto h-12 w-12 text-gray-600" />
                <h3 className="mt-2 text-lg font-medium text-gray-400">No active match</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Check upcoming matches below
                </p>
              </div>
            )}
          </div>

          {/* Active Tournaments */}
          <div className="bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <TrophyIcon className="h-6 w-6 mr-2 text-yellow-400" />
              Active Tournaments
            </h2>
            
            {activeTournaments.length > 0 ? (
              <div className="space-y-3">
                {activeTournaments.map((tournament) => (
                  <div key={tournament.id} className="bg-gray-700 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white">{tournament.name}</h3>
                    <div className="mt-2 flex items-center justify-between text-sm text-gray-400">
                      <span>{formatDate(tournament.start_date)} - {formatDate(tournament.end_date)}</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800`}>
                        {tournament.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <TrophyIcon className="mx-auto h-12 w-12 text-gray-600" />
                <h3 className="mt-2 text-lg font-medium text-gray-400">No active tournaments</h3>
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Matches */}
        <div className="mt-8 bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center">
            <ClockIcon className="h-6 w-6 mr-2 text-blue-400" />
            Upcoming Matches
          </h2>
          
          {upcomingMatches.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {upcomingMatches.slice(0, 6).map((match) => (
                <div key={match.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-sm text-gray-400">Arena {match.arena}</span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getMatchStatusColor(match.status)}`}>
                      {getMatchStatusIcon(match.status)}
                      <span className="ml-1">{match.status.replace('_', ' ')}</span>
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-gray-400">Team 1:</span>
                      <span className="ml-2 text-white">{match.team1_name}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-gray-400">Team 2:</span>
                      <span className="ml-2 text-white">{match.team2_name}</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-gray-600">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-400">{match.match_type}</span>
                      <span className="text-white font-mono">{formatTime(match.scheduled_time)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <ClockIcon className="mx-auto h-12 w-12 text-gray-600" />
              <h3 className="mt-2 text-lg font-medium text-gray-400">No upcoming matches</h3>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
