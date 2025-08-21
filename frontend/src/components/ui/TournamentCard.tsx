import React from 'react';
import Link from 'next/link';
import { 
  TrophyIcon, 
  CalendarIcon, 
  UserGroupIcon,
  ClockIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { Tournament } from '@/lib/types';
import { TournamentService } from '@/lib/services/tournamentService';

interface TournamentCardProps {
  tournament: Tournament;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  showActions?: boolean;
  className?: string;
}

export function TournamentCard({ 
  tournament, 
  onEdit, 
  onDelete, 
  showActions = true,
  className = ''
}: TournamentCardProps) {
  const statusDisplay = TournamentService.getStatusDisplay(tournament.status);
  const stats = TournamentService.getTournamentStats(tournament);

  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <TrophyIcon className="h-8 w-8 text-indigo-600" />
          </div>
          <div className="ml-4">
            <div className="flex items-center">
              <h3 className="text-lg font-medium text-gray-900">
                {tournament.name}
              </h3>
              <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusDisplay.color}`}>
                {statusDisplay.label}
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              {tournament.description}
            </p>
          </div>
        </div>
        
        {showActions && (
          <div className="flex items-center space-x-2">
            <Link
              href={`/tournaments/${tournament.id}`}
              className="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
            >
              View
            </Link>
            {onEdit && (
              <button
                onClick={() => onEdit(tournament.id)}
                className="text-gray-400 hover:text-gray-600"
                title="Edit tournament"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(tournament.id)}
                className="text-gray-400 hover:text-red-600"
                title="Delete tournament"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        )}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="flex items-center text-sm text-gray-500">
          <CalendarIcon className="h-4 w-4 mr-1" />
          <span>
            {TournamentService.formatDate(tournament.start_date)} - {TournamentService.formatDate(tournament.end_date)}
          </span>
        </div>
        
        <div className="flex items-center text-sm text-gray-500">
          <UserGroupIcon className="h-4 w-4 mr-1" />
          <span>Max {tournament.max_teams} teams</span>
        </div>
        
        <div className="flex items-center text-sm text-gray-500">
          <ClockIcon className="h-4 w-4 mr-1" />
          <span>{tournament.swiss_rounds_count} Swiss rounds</span>
        </div>
      </div>

      {stats.daysUntilStart > 0 && (
        <div className="mt-3">
          <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
            Starts in {stats.daysUntilStart} days
          </span>
        </div>
      )}

      {stats.isActive && (
        <div className="mt-3">
          <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
            Tournament is active
          </span>
        </div>
      )}
    </div>
  );
}

export default TournamentCard;
