import { useState, useEffect } from 'react';
import { getWebsites, createWebsite } from '../services/api';

// --- Child Components ---

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

// NEW: A form for connecting a platform. The submit handler is a placeholder for now.
function ConnectionForm({ website }) {
  const [pixelId, setPixelId] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    // Logic to be added in the next commit!
    console.log(`Submitting for website ID ${website.id} with Pixel ID ${pixelId}`);
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-lg mt-8">
      <h3 className="text-xl font-bold text-white mb-4">Connect to Meta</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-300">Meta Pixel ID</label>
          <input
            type="text"
            value={pixelId}
            onChange={(e) => setPixelId(e.target.value)}
            placeholder="Enter your Pixel ID"
            required
            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
          />
        </div>
        {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        <button type="submit" className="w-full py-2 px-4 bg-teal-600 rounded-md hover:bg-teal-700 font-medium">
          Connect
        </button>
      </form>
    </div>
  );
}


// --- Main Dashboard Component ---

function Dashboard({ onLogout }) {
  const [websites, setWebsites] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWebsiteId, setSelectedWebsiteId] = useState(null); // NEW: State to track which form to show

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

  // Find the currently selected website object
  const selectedWebsite = websites.find(w => w.id === selectedWebsiteId);

  if (isLoading) {
    return <p className="text-gray-400">Loading your dashboard...</p>;
  }

  if (error) {
    return <p className="text-red-400">Error: {error}</p>;
  }

  if (websites.length === 0) {
    return <CreateWebsiteForm onWebsiteCreated={handleWebsiteCreated} />;
  }

  // Main view when the user HAS websites
  return (
    // Flexbox utilities added here to center the child components
    <div className="w-full flex flex-col items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center w-full max-w-2xl">
          <h1 className="text-3xl font-bold text-white">Your Websites</h1>
          <ul className="mt-4 text-left divide-y divide-gray-700">
          {websites.map(site => (
            <li key={site.id} className="py-4">
              <p className="font-semibold text-white">{site.name} <span className="text-gray-400 font-normal">({site.url})</span></p>
              {site.connections.length > 0 ? (
                <div className="mt-2 text-sm text-green-400">
                  ✓ Connected to: {site.connections.map(c => c.platform).join(', ')}
                </div>
              ) : (
                // NEW: Button to show the connection form
                <button
                  onClick={() => setSelectedWebsiteId(site.id)}
                  className="mt-2 text-sm text-teal-400 hover:underline"
                >
                  + Connect a platform
                </button>
              )}
            </li>
          ))}
          </ul>
          <button
            onClick={onLogout}
            className="mt-8 px-4 py-2 bg-red-600 rounded-md hover:bg-red-700 font-medium"
          >
            Log Out
          </button>
      </div>

      {/* NEW: Conditionally render the ConnectionForm */}
      {selectedWebsite && (
        <ConnectionForm website={selectedWebsite} />
      )}
    </div>
  );
}

export default Dashboard;