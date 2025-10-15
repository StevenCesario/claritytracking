import { useState } from 'react';
import { registerUser } from '../services/api';

function RegistrationForm({ onRegisterSuccess }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    try {
      await registerUser({ name, email, password });
      setSuccess(true);
      // On success, we call the function from AuthScreen to switch the view back to login.
      setTimeout(onRegisterSuccess, 1500); // Wait a moment so the user can see the success message
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full">
      <h2 className="text-2xl font-bold text-center text-white mb-6">Create Your Account</h2>
      {success ? (
        <p className="text-green-400 text-center">Registration successful! Redirecting to login...</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength="8"
              className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md py-2 px-3 text-white"
            />
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
          <button type="submit" className="w-full py-2 px-4 bg-teal-600 rounded-md hover:bg-teal-700 font-medium">
            Register
          </button>
        </form>
      )}
    </div>
  );
}

export default RegistrationForm;
