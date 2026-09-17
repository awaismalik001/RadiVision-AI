import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Lock, 
  User, 
  Mail, 
  Phone, 
  ShieldCheck, 
  AlertCircle, 
  CheckCircle2, 
  Stethoscope, 
  Eye, 
  EyeOff, 
  ArrowRight,
  X,
  Globe,
  MapPin,
  Search,
  ChevronDown,
  Check,
  RefreshCw
} from 'lucide-react';
import axios from 'axios';

export default function AuthModal({ isOpen, onClose, onLoginSuccess, isStandalone = false }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const country = 'Pakistan';
  const [city, setCity] = useState('');
  const [citySearch, setCitySearch] = useState('');
  const [citySuggestions, setCitySuggestions] = useState([]);
  const [isCityDropdownOpen, setIsCityDropdownOpen] = useState(false);
  const [isLoadingPlaces, setIsLoadingPlaces] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const cityDropdownRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (cityDropdownRef.current && !cityDropdownRef.current.contains(event.target)) {
        setIsCityDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Search cities via Google Maps Places Autocomplete endpoint (restricted to Pakistan)
  useEffect(() => {
    const q = citySearch.trim();
    setIsLoadingPlaces(true);
    const timer = setTimeout(() => {
      axios.get(`/api/maps/places-autocomplete?query=${encodeURIComponent(q)}&country=Pakistan`)
        .then(res => {
          if (res.data?.predictions) setCitySuggestions(res.data.predictions);
        })
        .catch(() => {})
        .finally(() => setIsLoadingPlaces(false));
    }, 180);

    return () => clearTimeout(timer);
  }, [citySearch]);

  const handleToggleSignUp = (signUpMode) => {
    setIsSignUp(signUpMode);
    setErrorMessage('');
    if (isStandalone && window.electronAPI) {
      if (signUpMode) {
        window.electronAPI.authSignUp?.();
      } else {
        window.electronAPI.authSignIn?.();
      }
    }
  };

  if (!isOpen) return null;

  // Password validation rules for sign up
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  const isPasswordValid = hasMinLength && hasUppercase && hasLowercase && hasNumber && hasSpecial;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      if (isSignUp) {
        if (!city.trim()) {
          setErrorMessage('Mandatory: Please select your City (Pakistan).');
          setIsLoading(false);
          return;
        }

        if (!isPasswordValid) {
          setErrorMessage('Password must satisfy all security complexity requirements.');
          setIsLoading(false);
          return;
        }

        const res = await axios.post('/api/auth/signup', {
          full_name: fullName.trim(),
          username: username.trim(),
          email: email.trim(),
          phone: phone.trim(),
          country: country.trim(),
          city: city.trim(),
          password: password,
          role: 'User'
        });

        if (res.data && res.data.success) {
          onLoginSuccess(res.data.user);
          onClose();
        }
      } else {
        const res = await axios.post('/api/auth/login', {
          username: username,
          password: password
        });

        if (res.data && res.data.success) {
          onLoginSuccess(res.data.user);
          onClose();
        }
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Authentication error.';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const containerWidth = isStandalone 
    ? (isSignUp ? "max-w-[430px]" : "max-w-[360px]") 
    : (isSignUp ? "max-w-xl" : "max-w-md");

  return (
    <div className={isStandalone ? `relative z-10 w-full ${containerWidth} mx-auto transition-all duration-200` : `fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1727]/80 backdrop-blur-md`}>
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className={`w-full ${containerWidth} bg-white rounded-3xl ${isStandalone ? 'shadow-[0_25px_60px_-15px_rgba(0,0,0,0.65)] border border-slate-200/90' : 'shadow-2xl border border-slate-200'} overflow-hidden max-h-[96vh] flex flex-col transition-all duration-200`}
      >
        {/* Top Branding Banner (Compact & Draggable) */}
        <div 
          style={{ WebkitAppRegion: 'drag' }}
          className="bg-[#1982bf] py-3.5 px-6 text-white text-center relative shrink-0 select-none cursor-default"
        >
          {isStandalone && (
            <button
              type="button"
              onClick={() => {
                if (window.electronAPI?.close) {
                  window.electronAPI.close();
                }
              }}
              style={{ WebkitAppRegion: 'no-drag' }}
              className="absolute top-2.5 right-2.5 text-white/70 hover:text-white hover:bg-white/20 p-1.5 rounded-lg transition-colors cursor-pointer"
              title="Close Application"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <div className="inline-flex w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-blue-600 items-center justify-center shadow-md ring-1 ring-cyan-400/40 mb-1">
            <Stethoscope className="w-4 h-4 text-white" />
          </div>
          <h2 className="text-lg font-bold tracking-wider">
            RADIVISION <span className="text-cyan-400">AI</span>
          </h2>
          <p className="text-[11px] text-white/80">
            {isSignUp ? "Create your workstation account" : "Sign in to your workstation"}
          </p>
        </div>

        {/* Form Body (Compact & Vertically Optimized) */}
        <div className="p-5 overflow-y-auto">
          {errorMessage && (
            <div className="mb-3 p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3">
            {isSignUp ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                  {/* Full Name */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        placeholder="e.g. Awais Malik"
                        required
                        className="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Username */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Username
                    </label>
                    <div className="relative">
                      <User className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="e.g. awais_malik"
                        required
                        className="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Personal Email */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Personal Email
                    </label>
                    <div className="relative">
                      <Mail className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="name@gmail.com"
                        required
                        className="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Phone Number */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Phone Number
                    </label>
                    <div className="relative">
                      <Phone className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="0300-1234567"
                        required
                        className="w-full pl-8 pr-3 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Mandatory City Selection (Powered by Google Maps Platform) */}
                  <div className="relative md:col-span-2" ref={cityDropdownRef}>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                      <span>City (Pakistan) <span className="text-rose-500">*</span></span>
                      <span className="text-[9px] text-blue-600 font-semibold flex items-center gap-0.5">
                        <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                        Google Maps Platform
                      </span>
                    </label>
                    <div className="relative">
                      <MapPin className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={citySearch}
                        onChange={(e) => {
                          setCitySearch(e.target.value);
                          setCity(e.target.value);
                          setIsCityDropdownOpen(true);
                        }}
                        onFocus={() => {
                          setIsCityDropdownOpen(true);
                        }}
                        placeholder="e.g. Rawalpindi, Islamabad, Lahore, Karachi, Peshawar..."
                        required
                        className="w-full pl-8 pr-7 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      />
                      <div className="absolute right-2.5 top-1/2 -translate-y-1/2 flex items-center pointer-events-none">
                        {isLoadingPlaces ? (
                          <RefreshCw className="w-3 h-3 text-blue-500 animate-spin" />
                        ) : (
                          <Search className="w-3 h-3 text-slate-400" />
                        )}
                      </div>

                      {/* Dropdown Suggestions */}
                      {isCityDropdownOpen && (
                        <div className="absolute left-0 right-0 z-40 mt-1 bg-white rounded-xl shadow-xl border border-slate-200 py-1 max-h-48 overflow-y-auto">
                          <div className="px-2.5 py-1 text-[10px] uppercase font-semibold tracking-wider text-slate-400 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                            <span>Cities in Pakistan</span>
                            <span className="text-[9px] text-cyan-600 font-normal">Places API</span>
                          </div>
                          {citySuggestions.length > 0 ? (
                            citySuggestions.map((item, idx) => (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => {
                                  setCity(item.city);
                                  setCitySearch(item.city);
                                  setIsCityDropdownOpen(false);
                                }}
                                className="w-full px-3 py-1.5 text-left text-xs hover:bg-blue-50 flex items-center justify-between transition-colors group cursor-pointer"
                              >
                                <div className="truncate">
                                  <span className="font-medium text-slate-800 group-hover:text-blue-600">{item.city}</span>
                                  <span className="text-[10px] text-slate-400 ml-1.5 truncate">
                                    {item.description !== item.city ? item.description : "Pakistan"}
                                  </span>
                                </div>
                                {city.toLowerCase() === item.city.toLowerCase() && (
                                  <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                                )}
                              </button>
                            ))
                          ) : (
                            <div className="px-3 py-2 text-[11px] text-slate-400 text-center">
                              {isLoadingPlaces ? "Searching cities in Pakistan..." : "Type city name (e.g. Rawalpindi)"}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Password */}
                  <div className="md:col-span-2">
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Password
                    </label>
                    <div className="relative">
                      <Lock className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input
                        type={showPassword ? "text" : "password"}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••••••"
                        required
                        className="w-full pl-8 pr-8 py-2 rounded-xl border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                      >
                        {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Password Requirements Badges (Compact 1-row) */}
                <div className="p-2 rounded-xl bg-slate-50 border border-slate-200 text-[11px] flex flex-wrap items-center justify-between gap-1 text-slate-500">
                  <span className="font-semibold text-slate-600 text-[10px]">Requirements:</span>
                  <div className="flex flex-wrap gap-1 text-[10px]">
                    <span className={`px-1.5 py-0.5 rounded font-medium ${hasMinLength ? "bg-emerald-100 text-emerald-800" : "bg-slate-200/80 text-slate-500"}`}>8+ chars</span>
                    <span className={`px-1.5 py-0.5 rounded font-medium ${hasUppercase ? "bg-emerald-100 text-emerald-800" : "bg-slate-200/80 text-slate-500"}`}>Uppercase</span>
                    <span className={`px-1.5 py-0.5 rounded font-medium ${hasLowercase ? "bg-emerald-100 text-emerald-800" : "bg-slate-200/80 text-slate-500"}`}>Lowercase</span>
                    <span className={`px-1.5 py-0.5 rounded font-medium ${hasNumber ? "bg-emerald-100 text-emerald-800" : "bg-slate-200/80 text-slate-500"}`}>Number</span>
                    <span className={`px-1.5 py-0.5 rounded font-medium ${hasSpecial ? "bg-emerald-100 text-emerald-800" : "bg-slate-200/80 text-slate-500"}`}>Special (!@#)</span>
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Username */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Username
                  </label>
                  <div className="relative">
                    <User className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Username"
                      required
                      className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      required
                      className="w-full pl-9 pr-10 py-2.5 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none font-mono"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Remember Me on Login */}
                <div className="flex items-center justify-between text-xs text-slate-600 pt-0.5">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input 
                      type="checkbox" 
                      defaultChecked 
                      className="w-4 h-4 rounded border-slate-300 text-[#1982bf] focus:ring-[#1982bf] cursor-pointer" 
                    />
                    <span>Remember workstation session</span>
                  </label>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-2.5 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-md transition-all cursor-pointer"
            >
              <span>{isLoading ? "Authenticating..." : isSignUp ? "Create Account" : "Sign In"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </form>

          {/* Toggle between Login and Signup */}
          <div className="mt-3 text-center text-xs text-slate-500">
            {isSignUp ? (
              <span>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => handleToggleSignUp(false)}
                  className="font-semibold text-[#1982bf] hover:underline cursor-pointer"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => handleToggleSignUp(true)}
                  className="font-semibold text-[#1982bf] hover:underline cursor-pointer"
                >
                  Register Account
                </button>
              </span>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
