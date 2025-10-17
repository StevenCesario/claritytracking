import { useState, useEffect } from 'react';
import { getWebsiteHealth } from '../services/api';

const statusStyles = {
  healthy: 'bg-green-500',
  warning: 'bg-yellow-500',
  error: 'bg-red-500',
};

function EventHealthMonitor({ websiteId }) {
  const [healthData, setHealthData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      if (!websiteId) return;
      try {
        setIsLoading(true);
        const data = await getWebsiteHealth(websiteId);
        setHealthData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchHealth();
  }, [websiteId]);

  if (isLoading) {
    return <p className="text-gray-400 mt-4">Loading event health...</p>;
  }

  if (error) {
    return <p className="text-red-400 mt-4">Error loading health data: {error}</p>;
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-white">Event Health Monitor</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
        {healthData.map((event) => (
          <div key={event.event_name} className="bg-gray-700 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">{event.event_name}</span>
              <span className={`h-3 w-3 rounded-full ${statusStyles[event.status]}`}></span>
            </div>
            <p className="text-2xl font-bold text-white mt-2">{event.emq_score.toFixed(1)}</p>
            <p className="text-xs text-gray-400">Event Match Quality</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default EventHealthMonitor;
