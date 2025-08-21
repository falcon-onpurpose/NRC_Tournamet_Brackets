# Frontend Architecture - Clean Separation of Concerns

## Overview

The NRC Tournament Program frontend is designed with a clean separation between business logic and user interface components. This architecture allows anyone to create custom interfaces without modifying the core logic.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    UI Components Layer                      │
│  (Pages, Components, Forms - Pure Presentation Logic)      │
├─────────────────────────────────────────────────────────────┤
│                    Custom Hooks Layer                       │
│  (State Management, Business Logic Orchestration)          │
├─────────────────────────────────────────────────────────────┤
│                    Services Layer                           │
│  (Business Logic, Data Validation, API Communication)      │
├─────────────────────────────────────────────────────────────┤
│                    API Layer                                │
│  (HTTP Client, Request/Response Handling)                  │
├─────────────────────────────────────────────────────────────┤
│                    Types Layer                              │
│  (TypeScript Interfaces, Data Models)                      │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/
├── lib/                          # Core business logic
│   ├── types.ts                  # TypeScript interfaces
│   ├── api.ts                    # API client configuration
│   ├── services/                 # Business logic services
│   │   ├── tournamentService.ts
│   │   ├── teamService.ts
│   │   ├── matchService.ts
│   │   └── ...
│   └── hooks/                    # Custom React hooks
│       ├── useTournaments.ts
│       ├── useTeams.ts
│       └── ...
├── components/                   # Reusable UI components
│   ├── ui/                       # Pure UI components
│   │   ├── TournamentCard.tsx
│   │   ├── TournamentForm.tsx
│   │   └── ...
│   └── Navigation.tsx
└── app/                          # Next.js App Router pages
    ├── tournaments/
    ├── teams/
    └── ...
```

## Layer Responsibilities

### 1. Types Layer (`lib/types.ts`)

**Purpose**: Define all data structures and interfaces used throughout the application.

**Responsibilities**:
- Define TypeScript interfaces for all data models
- Ensure type safety across the application
- Provide consistent data structures

**Example**:
```typescript
export interface Tournament {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: TournamentStatus;
  // ... other properties
}
```

**Benefits**:
- Type safety across the entire application
- Clear contract for data structures
- Easy to modify data models in one place

### 2. API Layer (`lib/api.ts`)

**Purpose**: Handle all HTTP communication with the backend.

**Responsibilities**:
- Configure HTTP client (Axios)
- Define API endpoints
- Handle request/response interceptors
- Provide typed API methods

**Example**:
```typescript
export const apiClient = {
  getTournaments: () => api.get(endpoints.tournaments),
  createTournament: (data: TournamentCreate) => api.post(endpoints.tournaments, data),
  // ... other methods
};
```

**Benefits**:
- Centralized API configuration
- Consistent error handling
- Easy to modify API endpoints
- Type-safe API calls

### 3. Services Layer (`lib/services/`)

**Purpose**: Contain all business logic, data validation, and data transformation.

**Responsibilities**:
- Implement business rules and validation
- Transform data between API and UI formats
- Handle complex business operations
- Provide utility functions for data formatting

**Example**:
```typescript
export class TournamentService {
  static async getTournaments(): Promise<Tournament[]> {
    // Business logic for fetching tournaments
  }
  
  static validateTournament(data: TournamentCreate): { valid: boolean; errors: string[] } {
    // Business validation logic
  }
  
  static getStatusDisplay(status: string): { label: string; color: string } {
    // Data transformation logic
  }
}
```

**Benefits**:
- Reusable business logic
- Centralized validation rules
- Easy to test business logic independently
- Clear separation of concerns

### 4. Custom Hooks Layer (`lib/hooks/`)

**Purpose**: Manage React state and orchestrate business logic.

**Responsibilities**:
- Manage component state
- Coordinate between services and UI
- Handle loading and error states
- Provide clean interfaces for components

**Example**:
```typescript
export function useTournaments() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTournaments = useCallback(async () => {
    // Orchestrate business logic
  }, []);

  return {
    tournaments,
    loading,
    error,
    loadTournaments,
    // ... other methods
  };
}
```

**Benefits**:
- Reusable state management
- Clean component interfaces
- Centralized error handling
- Easy to test state logic

### 5. UI Components Layer (`components/ui/`)

**Purpose**: Pure presentation components with no business logic.

**Responsibilities**:
- Render UI elements
- Handle user interactions
- Apply styling and layout
- Receive data and callbacks as props

**Example**:
```typescript
interface TournamentCardProps {
  tournament: Tournament;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  showActions?: boolean;
}

export function TournamentCard({ tournament, onEdit, onDelete, showActions }: TournamentCardProps) {
  // Pure UI rendering logic
}
```

**Benefits**:
- Reusable UI components
- Easy to customize appearance
- No business logic dependencies
- Easy to test UI behavior

### 6. Pages Layer (`app/`)

**Purpose**: Compose UI components and connect to business logic.

**Responsibilities**:
- Compose UI components
- Connect to custom hooks
- Handle routing and navigation
- Manage page-level state

**Example**:
```typescript
export default function TournamentsPage() {
  const { tournaments, loading, error, deleteTournament } = useTournaments();
  
  return (
    <div>
      {tournaments.map(tournament => (
        <TournamentCard
          key={tournament.id}
          tournament={tournament}
          onDelete={deleteTournament}
        />
      ))}
    </div>
  );
}
```

**Benefits**:
- Clean page composition
- Minimal business logic
- Easy to modify page layouts
- Clear data flow

## Benefits of This Architecture

### 1. **Custom Interface Creation**
Anyone can create a custom interface by:
- Using the existing services and hooks
- Creating new UI components
- Composing pages differently
- **No need to modify business logic**

### 2. **Easy Testing**
- **Services**: Test business logic independently
- **Hooks**: Test state management separately
- **Components**: Test UI behavior in isolation
- **Pages**: Test component composition

### 3. **Maintainability**
- **Single Responsibility**: Each layer has one clear purpose
- **Loose Coupling**: Changes in one layer don't affect others
- **High Cohesion**: Related functionality is grouped together

### 4. **Reusability**
- **Services**: Reusable across different UI implementations
- **Hooks**: Reusable across different components
- **Components**: Reusable across different pages

### 5. **Type Safety**
- **End-to-end type safety** from API to UI
- **Compile-time error detection**
- **Better developer experience**

## Creating Custom Interfaces

### Example: Custom Tournament Dashboard

```typescript
// 1. Use existing business logic
import { useTournaments } from '@/lib/hooks/useTournaments';
import { TournamentService } from '@/lib/services/tournamentService';

// 2. Create custom UI components
function CustomTournamentCard({ tournament }) {
  // Custom styling and layout
}

// 3. Compose custom page
export default function CustomDashboard() {
  const { tournaments, loading } = useTournaments();
  
  return (
    <div className="custom-layout">
      {tournaments.map(tournament => (
        <CustomTournamentCard key={tournament.id} tournament={tournament} />
      ))}
    </div>
  );
}
```

### Example: Mobile Interface

```typescript
// 1. Same business logic
import { useTournaments } from '@/lib/hooks/useTournaments';

// 2. Mobile-specific UI components
function MobileTournamentCard({ tournament }) {
  // Mobile-optimized layout
}

// 3. Mobile page composition
export default function MobileTournamentsPage() {
  const { tournaments } = useTournaments();
  
  return (
    <div className="mobile-layout">
      {tournaments.map(tournament => (
        <MobileTournamentCard key={tournament.id} tournament={tournament} />
      ))}
    </div>
  );
}
```

## Migration Guide

### From Current Architecture to Clean Architecture

1. **Extract Types** (`lib/types.ts`)
   - Move all interfaces to types file
   - Ensure consistent naming

2. **Create Services** (`lib/services/`)
   - Extract business logic from components
   - Create service classes for each domain

3. **Create Hooks** (`lib/hooks/`)
   - Extract state management logic
   - Create custom hooks for each domain

4. **Refactor Components** (`components/ui/`)
   - Remove business logic from components
   - Make components pure and reusable

5. **Update Pages** (`app/`)
   - Use custom hooks for state management
   - Compose UI components
   - Remove direct API calls

## Best Practices

### 1. **Never Mix Layers**
- UI components should never call API directly
- Services should never contain UI logic
- Hooks should only manage state, not render UI

### 2. **Use TypeScript Strictly**
- Define interfaces for all data structures
- Use strict typing throughout the application
- Avoid `any` types

### 3. **Keep Components Pure**
- Components should be pure functions
- All data should come from props
- All actions should be passed as callbacks

### 4. **Centralize Business Logic**
- All business rules should be in services
- Validation should be in services
- Data transformation should be in services

### 5. **Handle Errors Consistently**
- Use consistent error handling patterns
- Centralize error messages
- Provide meaningful error feedback

## Conclusion

This architecture provides a solid foundation for building maintainable, testable, and extensible frontend applications. The clean separation of concerns makes it easy to create custom interfaces without modifying the core business logic, while the type safety ensures reliability and developer productivity.
