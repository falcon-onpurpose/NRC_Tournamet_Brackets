'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  PlusIcon, 
  UserGroupIcon, 
  CogIcon,
  UserIcon,
  CalendarIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '@/lib/api';

interface Team {
  id: string;
  name: string;
  tournament_id: string;
  tournament_name: string;
  experience_level: string;
  created_at: string;
  robots_count: number;
  players_count: number;
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTeams();
  }, []);

  const loadTeams = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getTeams();
      setTeams(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const getExperienceColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'novice':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading teams...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Teams</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage tournament teams and registrations
              </p>
            </div>
            <Link
              href="/teams/create"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Register Team
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Error loading teams
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    {error}
                  </div>
                </div>
              </div>
            </div>
          )}

          {teams.length === 0 && !loading ? (
            <div className="text-center py-12">
              <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No teams registered</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by registering a new team.
              </p>
              <div className="mt-6">
                <Link
                  href="/teams/create"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Register Team
                </Link>
              </div>
            </div>
          ) : (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {teams.map((team) => (
                  <li key={team.id}>
                    <div className="px-4 py-4 sm:px-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="flex-shrink-0">
                            <UserGroupIcon className="h-8 w-8 text-indigo-600" />
                          </div>
                          <div className="ml-4">
                            <div className="flex items-center">
                              <p className="text-sm font-medium text-indigo-600 truncate">
                                {team.name}
                              </p>
                              <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getExperienceColor(team.experience_level)}`}>
                                {team.experience_level}
                              </span>
                            </div>
                            <p className="text-sm text-gray-500">
                              Tournament: {team.tournament_name}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-sm text-gray-500">
                            <div className="flex items-center">
                              <CogIcon className="h-4 w-4 mr-1" />
                              {team.robots_count} robots
                            </div>
                            <div className="flex items-center mt-1">
                              <UserIcon className="h-4 w-4 mr-1" />
                              {team.players_count} players
                            </div>
                            <div className="flex items-center mt-1">
                              <CalendarIcon className="h-4 w-4 mr-1" />
                              {formatDate(team.created_at)}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Link
                              href={`/teams/${team.id}`}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              <EyeIcon className="h-4 w-4" />
                            </Link>
                            <Link
                              href={`/teams/${team.id}/edit`}
                              className="text-gray-400 hover:text-gray-600"
                            >
                              <PencilIcon className="h-4 w-4" />
                            </Link>
                            <button
                              className="text-gray-400 hover:text-red-600"
                              onClick={() => {
                                // TODO: Implement delete functionality
                                console.log('Delete team:', team.id);
                              }}
                            >
                              <TrashIcon className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
