import { useState } from 'react';
import { registerUser } from '../services/api';

function RegistrationForm({ onRegisterSuccess }) {
  // const [name, setName] = useState(''); No longer used
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  // const [success, setSuccess] = useState(false); No longer used

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    try {
      // We now only send the essentials: email and password.
      await registerUser({ email, password });

      // We call the function passed from the parent to handle the success state
      // (e.g., show a message and switch back to the login view).
      onRegisterSuccess();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-center text-white mb-6">Create Your Account</h2>
      
      {/* The Name input field has been removed. */}

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
      {error && <p className="text-red-400 text-sm text-center">{error}</p>}
      <button type="submit" className="w-full py-2 px-4 bg-teal-600 rounded-md hover:bg-teal-700 font-medium">
        Register
      </button>
    </form>
  );
}

export default RegistrationForm;
