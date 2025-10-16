import { useState, useEffect } from 'react';
import { getWebsites, createWebsite } from '../services/api';

// A simple form for creating the first website.
function CreateWebsiteForm({ onWebsiteCreated }) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const newWebsite = await createWebsite({ name, url });
      onWebsiteCreated(newWebsite); // Pass the new website up to the Dashboard
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-lg text-center">
      <h2 className="text-2xl font-bold text-white mb-2">Welcome to ClarityPixel</h2>
      <p className="text-gray-400 mb-6">Let's get your first website set up for tracking.</p>
      <form onSubmit={handleSubmit} className="space-y-4 text-left">
        <div>
          <label className="block text-sm font-medium text-gray-300">Website Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., My Shopify Store"
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-300">Website URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.yourstore.com"
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
          />
        </div>
        {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        <button type="submit" className="w-full py-2 px-4 bg-teal-600 rounded-md hover:bg-teal-700 font-medium">
          Add Website
        </button>
      </form>
    </div>
  );
}


// The main Dashboard component.
function Dashboard({ onLogout }) {
  const [websites, setWebsites] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch websites when the component mounts
  useEffect(() => {
    const fetchWebsites = async () => {
      try {
        const data = await getWebsites();
        setWebsites(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchWebsites();
  }, []);

  // Callback to add a newly created website to our state
  const handleWebsiteCreated = (newWebsite) => {
    setWebsites([...websites, newWebsite]);
  };

  if (isLoading) {
    return <p className="text-gray-400">Loading your dashboard...</p>;
  }

  if (error) {
    return <p className="text-red-400">Error: {error}</p>;
  }

  return (
    <div className="w-full">
      {websites.length === 0 ? (
        <CreateWebsiteForm onWebsiteCreated={handleWebsiteCreated} />
      ) : (
        <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center w-full max-w-md">
           <h1 className="text-3xl font-bold text-white">Your Websites</h1>
           <ul className="mt-4 text-left">
            {websites.map(site => (
              <li key={site.id} className="text-gray-300 p-2 border-b border-gray-700">{site.name} ({site.url})</li>
            ))}
           </ul>
           <button
            onClick={onLogout}
            className="mt-6 px-4 py-2 bg-red-600 rounded-md hover:bg-red-700 font-medium"
          >
            Log Out
          </button>
        </div>
      )}
    </div>
  );
}

export default Dashboard;