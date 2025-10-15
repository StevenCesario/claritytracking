import { useState } from 'react';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';

// This new component is a "local conductor". Its only job is to manage
// which authentication form is visible, keeping the main App component clean.
function AuthScreen({ onLoginSuccess }) {
  const [view, setView] = useState('login'); // Can be 'login' or 'register'

  // When registration is successful, this function passed from the parent
  // will be called, which will then flip the view back to 'login'.
  const handleRegisterSuccess = () => {
    setView('login');
    // We could add a "Registration successful!" message here later.
  };

  return (
    <div className="w-full max-w-md">
      {view === 'login' ? (
        <LoginForm onLoginSuccess={onLoginSuccess} />
      ) : (
        <RegistrationForm onRegisterSuccess={handleRegisterSuccess} />
      )}
      <div className="mt-4 text-center">
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

  const handleLoginSuccess = (newToken) => {
    // When the login is successful, this function is called by the LoginForm.
    // It updates the state, which will cause the App to re-render.
    setToken(newToken);
  };

  const handleLogout = () => {
    // To log out, we simply remove the token from state and localStorage.
    localStorage.removeItem('authToken');
    setToken(null);
  };

  return (
    <div className="bg-gray-900 min-h-screen flex items-center justify-center text-white p-4">
      {token ? (
        // If a token exists, we render the "logged-in" view (our future dashboard).
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400">You are logged in!</p>
          <button 
            onClick={handleLogout} 
            className="mt-4 px-4 py-2 bg-red-600 rounded-md hover:bg-red-700 font-medium"
          >
            Log Out
          </button>
        </div>
      ) : (
        // If no token exists, we render the AuthScreen, passing it the function
        // that will update the token upon a successful login.
        <AuthScreen onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;

