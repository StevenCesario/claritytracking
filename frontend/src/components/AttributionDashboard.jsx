import { useState, useEffect } from 'react';
// We'll add API calls and chart imports later

// Placeholder data for now
const mockAttributionData = {
  totalConversionsRecovered: 137,
  trueROAS: 3.4,
  campaignPerformance: [
    { id: 'C1', name: 'Campaign A', roas: 4.1 },
    { id: 'C2', name: 'Campaign B', roas: 2.8 },
    { id: 'C3', name: 'Campaign C', roas: 3.9 },
  ],
};

function AttributionDashboard({ websiteId }) {
  const [data, setData] = useState(mockAttributionData); // Using mock data for now
  const [isLoading, setIsLoading] = useState(false); // Set to false since we have mock data
  const [error, setError] = useState(null);

  // We'll add a useEffect for fetching real data later
  // useEffect(() => {
  //   const fetchData = async () => { ... };
  //   fetchData();
  // }, [websiteId]);

  if (isLoading) {
    return <p className="text-gray-400 mt-4">Loading attribution data...</p>;
  }

  if (error) {
    return <p className="text-red-400 mt-4">Error loading attribution data: {error}</p>;
  }

  return (
    <div className="mt-8 pt-6 border-t border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-4">Attribution Overview</h3>
      
      {/* Placeholder sections for the key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-3xl font-bold text-white">{data.totalConversionsRecovered}</p>
          <p className="text-sm text-gray-400">Total Conversions Recovered</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-3xl font-bold text-white">{data.trueROAS.toFixed(2)}x</p>
          <p className="text-sm text-gray-400">True ROAS (Overall)</p>
        </div>
      </div>

      <h4 className="text-md font-semibold text-white mb-3">Campaign Performance (ROAS)</h4>
      <div className="bg-gray-700 p-4 rounded-lg">
        {/* We'll replace this with a chart later */}
        <ul className="space-y-2">
          {data.campaignPerformance.map(campaign => (
            <li key={campaign.id} className="text-gray-300 flex justify-between">
              <span>{campaign.name}</span>
              <span>{campaign.roas.toFixed(2)}x</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default AttributionDashboard;