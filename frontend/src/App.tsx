import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { BrandProvider, useBrandContext } from './context';
import { Dashboard } from './views';

// Error Boundary to catch runtime errors
interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('App Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-red-900 text-white p-8">
          <h1 className="text-2xl font-bold mb-4">Something went wrong</h1>
          <pre className="bg-black/50 p-4 rounded overflow-auto">
            {this.state.error?.message}
            {'\n\n'}
            {this.state.error?.stack}
          </pre>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-white text-red-900 rounded"
          >
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

const AppContent: React.FC = () => {
  const { activeBrand } = useBrandContext();

  return (
    <Dashboard
      brandId={activeBrand?.id || 'demo-brand'}
      onSettingsClick={() => console.log('Settings clicked')}
    />
  );
};

function App() {
  return (
    <ErrorBoundary>
      <BrandProvider>
        <AppContent />
      </BrandProvider>
    </ErrorBoundary>
  );
}

export default App;
