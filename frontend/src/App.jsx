import { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';

// This new component is a "local conductor". Its only job is to manage
// which authentication form is visible, keeping the main App component clean.
function AuthScreen({ onLoginSuccess }) {
  const [view, setView] = useState('login'); // Can be 'login' or 'register'
  const [showSuccess, setShowSuccess] = useState(false);

  // When registration is successful, this function passed from the parent
  // will be called, which will then flip the view back to 'login'.
  const handleRegisterSuccess = () => {
    setView('login');
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <div className="w-full max-w-md bg-gray-800 p-8 rounded-lg shadow-lg">
      {showSuccess && (
        <div className="mb-4 p-3 bg-green-900 text-green-300 border border-green-700 rounded-md text-center">
          Registration successful! Please log in.
        </div>
      )}
      {view === 'login' ? (
        <LoginForm onLoginSuccess={onLoginSuccess} />
      ) : (
        <RegistrationForm onRegisterSuccess={handleRegisterSuccess} />
      )}
      <div className="mt-6 text-center">
        {view === 'login' ? (
          <p className="text-gray-400">
            No account yet?{' '}
            <button onClick={() => setView('register')} className="font-medium text-teal-400 hover:underline">
              Register
            </button>
          </p>
        ) : (
          <p className="text-gray-400">
            Already have an account?{' '}
            <button onClick={() => setView('login')} className="font-medium text-teal-400 hover:underline">
              Log In
            </button>
          </p>
        )}
      </div>
    </div>
  );
}


// This is the "Master Conductor" of our entire application.
function App() {
  // It holds the most important piece of state: the authentication token.
  // It initializes its state by checking localStorage, which allows us to
  // keep the user logged in even after a page refresh.
  const [token, setToken] = useState(localStorage.getItem('authToken'));

  // A single declarative rule for localStorage management of the authToken
  useEffect(() => {
    if (token) {
      localStorage.setItem('authToken', token);
    } else {
      localStorage.removeItem('authToken');
    }
  }, [token]);

  // This function is now passed to AuthScreen
  const handleLoginSuccess = (newToken) => {
    setToken(newToken);
  };

  // This function is now passed to the Logout button
  const handleLogout = () => {
    setToken(null);
  };

  return (
    <div className="bg-gray-900 min-h-screen flex items-center justify-center text-white p-4">
      {token ? (
        <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center w-full max-w-md">
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 mt-2">You are logged in!</p>
          <button 
            onClick={handleLogout} // We now use the named handler
            className="mt-6 px-4 py-2 bg-red-600 rounded-md hover:bg-red-700 font-medium"
          >
            Log Out
          </button>
        </div>
      ) : (
        <AuthScreen onLoginSuccess={handleLoginSuccess} /> // We now use the named handler
      )}
    </div>
  );
}

export default App;

