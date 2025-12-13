# Dashboard State Management Hooks

This directory contains custom React hooks for managing the Luminous Dashboard state, including real-time job updates, session history, and WebSocket fallback mechanisms.

## Overview

The state management system is built around three core hooks that work together to provide a seamless real-time experience:

1. **useSupabaseRealtime** - Low-level hook for Supabase Realtime subscriptions
2. **useJobStatus** - High-level hook for tracking job status with automatic fallback
3. **useSessionHistory** - Hook for managing multi-turn generation session history

These hooks are consumed by the **DashboardContext** which provides a unified state management layer for the entire dashboard.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  DashboardContext                       │
│  (Unified state + actions for entire dashboard)        │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
        ┌─────────▼─────────┐  ┌─────▼──────────────┐
        │   useJobStatus    │  │ useSessionHistory  │
        │ (Job tracking +   │  │ (Version history)  │
        │  polling fallback)│  │                    │
        └─────────┬─────────┘  └────────────────────┘
                  │
        ┌─────────▼──────────┐
        │ useSupabaseRealtime│
        │ (WebSocket updates)│
        └────────────────────┘
```

## Hooks

### useSupabaseRealtime

**Purpose**: Subscribe to real-time database updates via Supabase Realtime (PostgreSQL subscriptions).

**Usage**:
```tsx
import { useSupabaseRealtime } from './hooks/useSupabaseRealtime';

function MyComponent() {
  useSupabaseRealtime({
    jobId: 'job-123',
    onUpdate: (update) => {
      console.log('Job updated:', update);
    },
    onError: (error) => {
      console.error('Realtime error:', error);
    }
  });
}
```

**Features**:
- Automatic subscription management (subscribe on mount, unsubscribe on unmount)
- Filters updates to specific job_id
- Error handling with optional callback
- Stable callback refs to prevent unnecessary re-subscriptions

**Requirements**: 9.1, 9.9

---

### useJobStatus

**Purpose**: Track job status with real-time updates and automatic polling fallback.

**Usage**:
```tsx
import { useJobStatus } from './hooks/useJobStatus';

function MyComponent() {
  const { status, error, isPolling, refetch } = useJobStatus('job-123');

  if (error) return <div>Error: {error.message}</div>;
  if (!status) return <div>Loading...</div>;

  return (
    <div>
      <p>Status: {status.status}</p>
      <p>Progress: {status.progress}%</p>
      {isPolling && <span>⚠️ Using polling mode</span>}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
}
```

**Features**:
- Uses `useSupabaseRealtime` for real-time updates
- Automatically falls back to polling if Realtime fails
- Detects stale connections (no updates for 10 seconds)
- Stops polling when job reaches terminal state (completed/failed/cancelled)
- Provides manual refetch function

**Requirements**: 9.1-9.10

---

### useSessionHistory

**Purpose**: Manage multi-turn generation session history and version navigation.

**Usage**:
```tsx
import { useSessionHistory } from './hooks/useSessionHistory';

function MyComponent() {
  const {
    versions,
    currentIndex,
    currentVersion,
    loadVersion,
    addVersion,
    isLoading,
    error
  } = useSessionHistory('session-123');

  return (
    <div>
      <h3>Version {currentIndex + 1} of {versions.length}</h3>
      <img src={currentVersion?.image_url} alt="Current version" />
      
      <div>
        {versions.map((version, index) => (
          <button
            key={version.attempt_id}
            onClick={() => loadVersion(index)}
            disabled={index === currentIndex}
          >
            Version {index + 1} ({version.score}%)
          </button>
        ))}
      </div>
    </div>
  );
}
```

**Features**:
- Fetches session history from backend on mount
- Automatically navigates to latest version
- Provides version navigation (loadVersion)
- Supports adding new versions (addVersion)
- Auto-scrolls to new versions when added

**Requirements**: 10.1-10.7

---

## DashboardContext

**Purpose**: Unified state management for the entire Luminous Dashboard.

**Usage**:
```tsx
import { DashboardProvider, useDashboard } from './context/DashboardContext';

// Wrap your app
function App() {
  return (
    <DashboardProvider brandId="brand-123">
      <Dashboard />
    </DashboardProvider>
  );
}

// Use in components
function Dashboard() {
  const {
    // State
    jobId,
    sessionId,
    status,
    currentImageUrl,
    complianceScore,
    violations,
    twinData,
    versions,
    currentVersion,
    messages,
    connectionStatus,
    isPolling,
    error,
    
    // Actions
    submitPrompt,
    loadVersion,
    acceptCorrection,
    retryGeneration,
    clearError,
  } = useDashboard();

  return (
    <div>
      <ConnectionIndicator status={connectionStatus} />
      <ChatInterface messages={messages} onSubmit={submitPrompt} />
      <Canvas imageUrl={currentImageUrl} violations={violations} />
      <ComplianceGauge score={complianceScore} violations={violations} />
      <VersionScrubber versions={versions} onSelect={loadVersion} />
    </div>
  );
}
```

**Features**:
- Combines all hooks into unified state
- Manages chat history
- Handles optimistic updates
- Provides high-level actions (submitPrompt, acceptCorrection, etc.)
- Automatically adds completed jobs to version history
- Derives connection status from polling state

**Requirements**: 9.1-9.10, 10.1-10.7

---

## Real-Time Update Flow

```
1. User submits prompt
   ↓
2. API returns job_id
   ↓
3. useSupabaseRealtime subscribes to job updates
   ↓
4. Backend updates job status in database
   ↓
5. Supabase Realtime pushes update to client
   ↓
6. useJobStatus receives update and updates state
   ↓
7. DashboardContext propagates to all components
   ↓
8. UI updates reactively
```

## Fallback Mechanism

If Supabase Realtime fails or times out:

```
1. useJobStatus detects no updates for 10 seconds
   ↓
2. Sets isPolling = true
   ↓
3. Starts polling API every 5 seconds
   ↓
4. Updates state from polling responses
   ↓
5. Continues until job reaches terminal state
```

## Environment Variables

Required environment variables (add to `.env`):

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## Testing

All hooks have comprehensive unit tests:

```bash
# Run all hook tests
npm test -- src/hooks/__tests__/

# Run specific hook test
npm test -- src/hooks/__tests__/useJobStatus.test.ts
```

## Error Handling

All hooks implement robust error handling:

- **Network errors**: Caught and exposed via `error` state
- **Subscription errors**: Trigger fallback to polling
- **Invalid data**: Logged to console, doesn't crash app
- **Timeout errors**: Automatically retry with exponential backoff

## Performance Considerations

- **Stable refs**: Callbacks use refs to prevent unnecessary re-subscriptions
- **Cleanup**: All subscriptions and intervals are properly cleaned up
- **Memoization**: DashboardContext uses useMemo for derived state
- **Polling optimization**: Stops polling when job is complete

## Future Enhancements

- [ ] Add retry logic with exponential backoff for failed API calls
- [ ] Implement connection quality monitoring
- [ ] Add offline support with request queuing
- [ ] Support multiple concurrent jobs
- [ ] Add WebSocket heartbeat monitoring
