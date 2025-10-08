import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Eye, EyeOff, Loader2, Check, X } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    full_name: '',
    terms_accepted: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState('weak');
  const [usernameAvailable, setUsernameAvailable] = useState(null);
  const [emailAvailable, setEmailAvailable] = useState(null);
  const [checkingUsername, setCheckingUsername] = useState(false);
  const [checkingEmail, setCheckingEmail] = useState(false);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Check username availability
  useEffect(() => {
    const checkUsername = async () => {
      if (formData.username.length >= 3) {
        setCheckingUsername(true);
        try {
          const response = await axios.get(
            `${BACKEND_URL}/api/auth/check-username/${formData.username}`
          );
          setUsernameAvailable(response.data.available);
        } catch (error) {
          setUsernameAvailable(null);
        } finally {
          setCheckingUsername(false);
        }
      } else {
        setUsernameAvailable(null);
      }
    };

    const timer = setTimeout(checkUsername, 500);
    return () => clearTimeout(timer);
  }, [formData.username]);

  // Check email availability
  useEffect(() => {
    const checkEmail = async () => {
      if (formData.email.includes('@')) {
        setCheckingEmail(true);
        try {
          const response = await axios.get(
            `${BACKEND_URL}/api/auth/check-email/${formData.email}`
          );
          setEmailAvailable(response.data.available);
        } catch (error) {
          setEmailAvailable(null);
        } finally {
          setCheckingEmail(false);
        }
      } else {
        setEmailAvailable(null);
      }
    };

    const timer = setTimeout(checkEmail, 500);
    return () => clearTimeout(timer);
  }, [formData.email]);

  // Check password strength
  useEffect(() => {
    const checkStrength = () => {
      const password = formData.password;
      let score = 0;

      if (password.length >= 8) score++;
      if (password.length >= 12) score++;
      if (/[a-z]/.test(password)) score++;
      if (/[A-Z]/.test(password)) score++;
      if (/\d/.test(password)) score++;
      if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;

      if (score <= 2) setPasswordStrength('weak');
      else if (score <= 4) setPasswordStrength('medium');
      else setPasswordStrength('strong');
    };

    if (formData.password) {
      checkStrength();
    }
  }, [formData.password]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (formData.password !== formData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }

    if (!formData.terms_accepted) {
      toast.error('Please accept the terms and conditions');
      return;
    }

    if (usernameAvailable === false) {
      toast.error('Username is already taken');
      return;
    }

    if (emailAvailable === false) {
      toast.error('Email is already registered');
      return;
    }

    setLoading(true);

    try {
      const result = await register(formData);
      toast.success(result.message || 'Account created successfully!');
      navigate('/auth/login');
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'Registration failed';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const getStrengthColor = () => {
    if (passwordStrength === 'weak') return 'bg-[#D9534F]';
    if (passwordStrength === 'medium') return 'bg-[#F5C518]';
    return 'bg-[#5CB85C]';
  };

  const getStrengthWidth = () => {
    if (passwordStrength === 'weak') return 'w-1/3';
    if (passwordStrength === 'medium') return 'w-2/3';
    return 'w-full';
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-4xl font-bold text-[#F5C518]">PodDB Pro</h1>
          </Link>
          <p className="text-gray-400 mt-2">Create your account</p>
        </div>

        {/* Register Form */}
        <div className="bg-[#1F1F1F] rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Username *
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  minLength={3}
                  maxLength={20}
                  pattern="[a-zA-Z0-9_]+"
                  className="w-full px-4 py-3 bg-black border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5799EF] focus:border-transparent"
                  placeholder="Choose a username"
                />
                {formData.username.length >= 3 && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {checkingUsername ? (
                      <Loader2 className="animate-spin text-gray-400" size={20} />
                    ) : usernameAvailable === true ? (
                      <Check className="text-[#5CB85C]" size={20} />
                    ) : usernameAvailable === false ? (
                      <X className="text-[#D9534F]" size={20} />
                    ) : null}
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                3-20 characters, letters, numbers, and underscores only
              </p>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email *
              </label>
              <div className="relative">
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-black border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5799EF] focus:border-transparent"
                  placeholder="your@email.com"
                />
                {formData.email.includes('@') && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {checkingEmail ? (
                      <Loader2 className="animate-spin text-gray-400" size={20} />
                    ) : emailAvailable === true ? (
                      <Check className="text-[#5CB85C]" size={20} />
                    ) : emailAvailable === false ? (
                      <X className="text-[#D9534F]" size={20} />
                    ) : null}
                  </div>
                )}
              </div>
            </div>

            {/* Full Name */}
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-300 mb-2">
                Full Name (Optional)
              </label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                maxLength={100}
                className="w-full px-4 py-3 bg-black border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5799EF] focus:border-transparent"
                placeholder="Your full name"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password *
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  minLength={8}
                  className="w-full px-4 py-3 bg-black border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5799EF] focus:border-transparent pr-12"
                  placeholder="Create a strong password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {/* Password Strength Indicator */}
              {formData.password && (
                <div className="mt-2">
                  <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
                    <div className={`h-full ${getStrengthColor()} ${getStrengthWidth()} transition-all duration-300`} />
                  </div>
                  <p className="text-xs text-gray-500 mt-1 capitalize">
                    Strength: {passwordStrength}
                  </p>
                </div>
              )}
              <p className="text-xs text-gray-500 mt-1">
                Min 8 characters, include uppercase, lowercase, number, and special character
              </p>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password *
              </label>
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  id="confirm_password"
                  name="confirm_password"
                  value={formData.confirm_password}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 bg-black border border-gray-700 rounded-md text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#5799EF] focus:border-transparent pr-12"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {formData.confirm_password && formData.password !== formData.confirm_password && (
                <p className="text-xs text-[#D9534F] mt-1">Passwords do not match</p>
              )}
            </div>

            {/* Terms and Conditions */}
            <div>
              <label className="flex items-start">
                <input
                  type="checkbox"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  required
                  className="w-4 h-4 mt-1 rounded border-gray-700 bg-black text-[#5799EF] focus:ring-[#5799EF]"
                />
                <span className="ml-2 text-sm text-gray-400">
                  I agree to the{' '}
                  <Link to="/terms" className="text-[#5799EF] hover:text-[#4080d0]">
                    Terms and Conditions
                  </Link>
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || usernameAvailable === false || emailAvailable === false}
              className="w-full py-3 px-4 bg-[#5799EF] hover:bg-[#4080d0] text-white font-semibold rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin mr-2" size={20} />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/auth/login" className="text-[#5799EF] hover:text-[#4080d0] font-semibold">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;