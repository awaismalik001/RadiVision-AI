import React, { useState } from 'react';
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
  ArrowRight 
} from 'lucide-react';
import axios from 'axios';

export default function AuthModal({ isOpen, onClose, onLoginSuccess, isStandalone = false }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('User');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

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
        if (!isPasswordValid) {
          setErrorMessage('Password must satisfy all security complexity requirements.');
          setIsLoading(false);
          return;
        }

        const res = await axios.post('/api/auth/signup', {
          full_name: fullName,
          username: username,
          email: email,
          phone: phone,
          password: password,
          role: role
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

  const containerWidth = isSignUp ? "max-w-xl" : "max-w-md";

  return (
    <div className={isStandalone ? `relative z-10 w-full ${containerWidth} mx-auto transition-all duration-200` : `fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1727]/80 backdrop-blur-md`}>
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className={`w-full ${containerWidth} bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden max-h-[92vh] flex flex-col transition-all duration-200`}
      >
        {/* Top Branding Banner (Compact) */}
        <div className="bg-[#1982bf] py-3.5 px-6 text-white text-center relative shrink-0">
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

                  {/* Account Role */}
                  <div>
                    <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                      Account Role
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setRole('User')}
                        className={`py-1.5 px-3 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                          role === 'User' 
                            ? 'border-[#1982bf] bg-blue-50 text-[#1982bf]' 
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        User
                      </button>
                      <button
                        type="button"
                        onClick={() => setRole('Admin')}
                        className={`py-1.5 px-3 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                          role === 'Admin' 
                            ? 'border-[#1982bf] bg-blue-50 text-[#1982bf]' 
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        Admin
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
                  onClick={() => { setIsSignUp(false); setErrorMessage(''); }}
                  className="font-semibold text-[#1982bf] hover:underline cursor-pointer"
                >
                  Sign In
                </button>
              </span>
            ) : (
              <span>
                Don't have an account?{' '}
                <button
                  onClick={() => { setIsSignUp(true); setErrorMessage(''); }}
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
