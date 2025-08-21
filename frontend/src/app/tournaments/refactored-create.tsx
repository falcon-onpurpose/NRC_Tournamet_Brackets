'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { useTournaments } from '@/lib/hooks/useTournaments';
import { TournamentForm } from '@/components/ui/TournamentForm';
import { TournamentCreate } from '@/lib/types';

export default function RefactoredCreateTournamentPage() {
  const router = useRouter();
  const { createTournament } = useTournaments();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: TournamentCreate) => {
    try {
      setLoading(true);
      setError(null);
      
      await createTournament(data);
      router.push('/tournaments');
    } catch (err: any) {
      setError(err.message || 'Failed to create tournament');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    router.push('/tournaments');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center py-6">
            <Link
              href="/tournaments"
              className="mr-4 text-gray-400 hover:text-gray-600"
            >
              <ArrowLeftIcon className="h-6 w-6" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Create Tournament</h1>
              <p className="mt-1 text-sm text-gray-500">
                Set up a new robotics tournament
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg">
            <div className="p-6">
              {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
                  <div className="flex">
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Error creating tournament
                      </h3>
                      <div className="mt-2 text-sm text-red-700">
                        {error}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <TournamentForm
                onSubmit={handleSubmit}
                onCancel={handleCancel}
                loading={loading}
                submitLabel="Create Tournament"
                cancelLabel="Cancel"
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
