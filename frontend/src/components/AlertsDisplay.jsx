import { useState, useEffect } from 'react';
import { getWebsiteAlerts } from '../services/api';

// Simple map for styling alerts based on severity
const alertStyles = {
  error: {
    bg: 'bg-red-900 border-red-700',
    icon: 'text-red-400',
    title: 'text-red-300',
    message: 'text-red-400',
  },
  warning: {
    bg: 'bg-yellow-900 border-yellow-700',
    icon: 'text-yellow-400',
    title: 'text-yellow-300',
    message: 'text-yellow-400',
  },
};

// A simple icon component to make it look a bit better
function AlertIcon({ severity }) {
    const iconClass = alertStyles[severity]?.icon || 'text-gray-400';
    if (severity === 'error') {
        return (
            <svg className={`w-5 h-5 ${iconClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        ); 
    }
    return (
    <svg className={`w-5 h-5 ${iconClass}`} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  );
}

// Main AlertsDisplay component
function AlertsDisplay({ websiteId }) {
    const [alerts, setAlerts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAlerts = async () => {
            if (!websiteId) return;
            try {
                setIsLoading(true);
                const data = await getWebsiteAlerts(websiteId);
                setAlerts(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchAlerts();
    }, [websiteId]); // This effect re-runs whenever the websiteId prop changes

    if (isLoading) {
        return <p className="text-gray-400 mt-4 text-sm">Loading alerts...</p>;
    }

    if (error) {
        return <p className="text-red-400 mt-4 text-sm">Error loading alerts: {error}</p>;
    }

    if (alerts.length === 0) {
        return (
        <div className="mt-6 p-4 bg-gray-700 rounded-lg border border-gray-600">
            <h3 className="text-lg font-semibold text-white mb-2">Health Alerts</h3>
            <p className="text-green-400 text-sm">✓ No issues detected. All systems nominal.</p>
        </div>
        );
    }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-white mb-4">Health Alerts</h3>
      <div className="space-y-4">
        {alerts.map((alert) => {
          const styles = alertStyles[alert.severity] || alertStyles.warning;
          return (
            <div key={alert.id} className={`p-4 rounded-lg border ${styles.bg}`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  <AlertIcon severity={alert.severity} />
                </div>
                <div className="ml-3">
                  <h4 className={`text-sm font-medium ${styles.title}`}>{alert.title}</h4>
                  <p className={`text-sm mt-1 ${styles.message}`}>{alert.message}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default AlertsDisplay;