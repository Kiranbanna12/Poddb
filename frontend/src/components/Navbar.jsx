import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Menu, X, User, LogOut } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      console.log('Search query:', searchQuery);
      // Navigate to search results page (to be implemented)
    }
  };

  return (
    <nav className="bg-black border-b border-gray-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold">
              <span className="text-[#F5C518]">Pod</span>
              <span className="text-white">DB</span>
              <span className="text-[#F5C518] ml-1 text-sm">Pro</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-white hover:text-[#5799EF] transition-colors text-sm font-medium">
              Home
            </Link>
            <Link to="/rankings" className="text-white hover:text-[#5799EF] transition-colors text-sm font-medium">
              Rankings
            </Link>
            <Link to="/contribute" className="text-white hover:text-[#5799EF] transition-colors text-sm font-medium">
              Contribute
            </Link>
          </div>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="hidden md:flex items-center flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <input
                type="text"
                placeholder="Search podcasts, episodes, people..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-[#2A2A2A] text-white text-sm px-4 py-2 pl-10 rounded-md focus:outline-none focus:ring-2 focus:ring-[#5799EF] transition-all"
              />
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            </div>
          </form>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/profile">
                  <Button variant="ghost" size="sm" className="text-white hover:text-[#5799EF] hover:bg-[#1F1F1F]">
                    <User size={18} className="mr-2" />
                    {user?.username || 'Profile'}
                  </Button>
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-white hover:text-[#D9534F] hover:bg-[#1F1F1F]"
                >
                  <LogOut size={18} className="mr-2" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link to="/auth/login">
                  <Button variant="ghost" size="sm" className="text-white hover:text-[#5799EF] hover:bg-[#1F1F1F]">
                    <User size={18} className="mr-2" />
                    Sign In
                  </Button>
                </Link>
                <Link to="/auth/register">
                  <Button size="sm" className="bg-[#5799EF] hover:bg-[#4080d0] text-white">
                    Sign Up
                  </Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden text-white hover:text-[#F5C518] transition-colors"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-[#0F0F0F] border-t border-gray-800">
          <div className="px-4 py-4 space-y-4">
            <form onSubmit={handleSearch} className="mb-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-[#2A2A2A] text-white text-sm px-4 py-2 pl-10 rounded-md focus:outline-none focus:ring-2 focus:ring-[#5799EF]"
                />
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              </div>
            </form>
            
            <Link 
              to="/" 
              className="block text-white hover:text-[#5799EF] transition-colors py-2"
              onClick={() => setIsMenuOpen(false)}
            >
              Home
            </Link>
            <Link 
              to="/rankings" 
              className="block text-white hover:text-[#5799EF] transition-colors py-2"
              onClick={() => setIsMenuOpen(false)}
            >
              Rankings
            </Link>
            <Link 
              to="/contribute" 
              className="block text-white hover:text-[#5799EF] transition-colors py-2"
              onClick={() => setIsMenuOpen(false)}
            >
              Contribute
            </Link>
            <Button className="w-full bg-[#5799EF] hover:bg-[#4A7BC8] text-white">
              <User size={18} className="mr-2" />
              Sign In
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;