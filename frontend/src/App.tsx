import { Component, useEffect } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { BrandProvider, useBrandContext } from './context';
import { Dashboard } from './views';
import { logWebVitals, markPerformance } from './utils/performance';

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
  const { activeBrand, brands, loading } = useBrandContext();

  // Performance monitoring
  useEffect(() => {
    markPerformance('app-content-mounted');
    logWebVitals();
  }, []);

  // Debug logging to understand state changes
  useEffect(() => {
    console.log('🔍 App State:', {
      loading,
      brandsCount: brands.length,
      activeBrandId: activeBrand?.id,
      firstBrandId: brands[0]?.id,
    });
  }, [loading, brands.length, activeBrand?.id]);

  // Use active brand or first brand from list
  // Pass undefined if still loading - Dashboard will handle gracefully
  const brandId = activeBrand?.id || brands[0]?.id;

  // Always render Dashboard - it handles loading states internally
  // This allows the app shell to render immediately while brands load in background
  return (
    <Dashboard
      brandId={brandId}
      onSettingsClick={() => console.log('Settings clicked')}
      brandsLoading={loading}
      noBrands={!loading && brands.length === 0}
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
