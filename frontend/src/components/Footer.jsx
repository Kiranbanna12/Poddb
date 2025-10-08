import React from 'react';
import { Link } from 'react-router-dom';
import { Youtube, Twitter, Instagram, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-black border-t border-gray-800 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="text-2xl font-bold">
                <span className="text-[#F5C518]">Pod</span>
                <span className="text-white">DB</span>
                <span className="text-[#F5C518] ml-1 text-sm">Pro</span>
              </div>
            </div>
            <p className="text-[#AAAAAA] text-sm mb-4 max-w-md">
              India's most comprehensive podcast database. Discover, rate, and explore thousands of podcasts across all categories.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors">
                <Youtube size={20} />
              </a>
              <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors">
                <Twitter size={20} />
              </a>
              <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors">
                <Instagram size={20} />
              </a>
              <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors">
                <Mail size={20} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/rankings" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Rankings
                </Link>
              </li>
              <li>
                <Link to="/contribute" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Contribute
                </Link>
              </li>
              <li>
                <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Browse Categories
                </a>
              </li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h3 className="text-white font-semibold mb-4 text-sm">About</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  About Us
                </a>
              </li>
              <li>
                <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-[#AAAAAA] hover:text-[#5799EF] transition-colors text-sm">
                  Terms of Service
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-[#2A2A2A] mt-8 pt-8">
          <p className="text-center text-[#AAAAAA] text-sm">
            © 2025 PodDB Pro. All rights reserved. Data sourced from YouTube and community contributions.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;