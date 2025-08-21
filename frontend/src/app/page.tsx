import Link from 'next/link';
import { 
  TrophyIcon, 
  UserGroupIcon, 
  CalendarIcon, 
  CogIcon,
  ChartBarIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

export default function Dashboard() {
  const menuItems = [
    {
      title: 'Tournaments',
      description: 'Create and manage tournaments',
      icon: TrophyIcon,
      href: '/tournaments',
      color: 'bg-blue-500',
    },
    {
      title: 'Teams',
      description: 'Register and manage teams',
      icon: UserGroupIcon,
      href: '/teams',
      color: 'bg-green-500',
    },
    {
      title: 'Matches',
      description: 'Schedule and track matches',
      icon: CalendarIcon,
      href: '/matches',
      color: 'bg-purple-500',
    },
    {
      title: 'Public Display',
      description: 'View current tournament status',
      icon: EyeIcon,
      href: '/public',
      color: 'bg-orange-500',
    },
    {
      title: 'Analytics',
      description: 'Tournament statistics and reports',
      icon: ChartBarIcon,
      href: '/analytics',
      color: 'bg-indigo-500',
    },
    {
      title: 'Settings',
      description: 'System configuration',
      icon: CogIcon,
      href: '/settings',
      color: 'bg-gray-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                NRC Tournament Program
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Comprehensive tournament management system
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                System Online
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                Welcome to NRC Tournament Management
              </h2>
              <p className="text-gray-600 mb-6">
                Manage your robotics tournaments with ease. Create tournaments, register teams, 
                schedule matches, and track results in real-time.
              </p>
              
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">0</div>
                  <div className="text-sm text-blue-500">Active Tournaments</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">0</div>
                  <div className="text-sm text-green-500">Registered Teams</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">0</div>
                  <div className="text-sm text-purple-500">Scheduled Matches</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">0</div>
                  <div className="text-sm text-orange-500">Completed Matches</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Grid */}
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {menuItems.map((item) => (
              <Link
                key={item.title}
                href={item.href}
                className="group relative bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg shadow hover:shadow-md transition-shadow"
              >
                <div>
                  <span className={`inline-flex p-3 ${item.color} text-white rounded-lg`}>
                    <item.icon className="h-6 w-6" aria-hidden="true" />
                  </span>
                </div>
                <div className="mt-4">
                  <h3 className="text-lg font-medium text-gray-900 group-hover:text-indigo-600">
                    {item.title}
                  </h3>
                  <p className="mt-2 text-sm text-gray-500">
                    {item.description}
                  </p>
                </div>
                <span
                  className="absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                  aria-hidden="true"
                >
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4h1a1 1 0 00-1-1v1zm-1 12a1 1 0 102 0h-2zM8 3a1 1 0 000 2V3zM3.293 19.293a1 1 0 101.414 1.414l-1.414-1.414zM19 4v12h2V4h-2zm1-1H8v2h12V3zm-.707.293l-16 16 1.414 1.414 16-16-1.414-1.414z" />
                  </svg>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
