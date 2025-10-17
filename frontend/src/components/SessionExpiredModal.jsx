function SessionExpiredModal({ onClose }) {
  return (
    // This is the semi-transparent backdrop
    <div 
      className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50"
      onClick={onClose} // Allow closing by clicking the backdrop
    >
      {/* This is the modal content itself */}
      <div 
        className="bg-gray-800 p-8 rounded-lg shadow-lg text-center w-full max-w-sm"
        onClick={(e) => e.stopPropagation()} // Prevent clicks inside the modal from closing it
      >
        <h2 className="text-2xl font-bold text-white">Session Expired</h2>
        <p className="text-gray-400 mt-4">Your session has timed out. Please log in again to continue.</p>
        <button
          onClick={onClose}
          className="mt-6 w-full py-2 px-4 bg-teal-600 rounded-md hover:bg-teal-700 font-medium"
        >
          OK
        </button>
      </div>
    </div>
  );
}

export default SessionExpiredModal;