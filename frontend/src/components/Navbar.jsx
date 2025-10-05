import { Link } from 'react-router-dom';
import { FiHome, FiBarChart2, FiUpload } from 'react-icons/fi';

function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">E</span>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
              ExoHunt
            </span>
          </Link>

          <div className="flex space-x-6">
            <Link
              to="/"
              className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors duration-200"
            >
              <FiHome className="text-xl" />
              <span className="font-medium">Home</span>
            </Link>
            <Link
              to="/dashboard"
              className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors duration-200"
            >
              <FiBarChart2 className="text-xl" />
              <span className="font-medium">Dashboard</span>
            </Link>
            <Link
              to="/analyze"
              className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors duration-200"
            >
              <FiUpload className="text-xl" />
              <span className="font-medium">Analyze</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
