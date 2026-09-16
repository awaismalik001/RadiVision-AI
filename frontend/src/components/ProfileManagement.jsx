import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Lock, 
  ShieldAlert, 
  ShieldCheck, 
  KeyRound, 
  Save, 
  CheckCircle2, 
  AlertCircle,
  Users,
  Eye,
  EyeOff
} from 'lucide-react';
import axios from 'axios';

export default function ProfileManagement({ currentUser }) {
  const isAdmin = currentUser?.role === 'Admin';
  
  // Form State
  const [usersList, setUsersList] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(currentUser?.user_id || 1);
  const [fullName, setFullName] = useState(currentUser?.full_name || '');
  const [username, setUsername] = useState(currentUser?.username || '');
  const [email, setEmail] = useState(currentUser?.email || '');
  const [newPassword, setNewPassword] = useState('');
  const [targetRole, setTargetRole] = useState(currentUser?.role || 'User');
  const [isActive, setIsActive] = useState(true);

  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  // Fetch all users if Admin
  useEffect(() => {
    if (isAdmin) {
      axios.get('/api/admin/users')
        .then((res) => {
          if (res.data && res.data.users) {
            setUsersList(res.data.users);
          }
        })
        .catch((err) => console.error('[Profile] Fetch users error:', err));
    }
  }, [isAdmin]);

  // When admin selects a different user from dropdown
  const handleSelectUser = (id) => {
    const user = usersList.find((u) => u.user_id === Number(id));
    if (user) {
      setSelectedUserId(user.user_id);
      setFullName(user.full_name || '');
      setUsername(user.username || '');
      setEmail(user.email || '');
      setTargetRole(user.role || 'User');
      setIsActive(user.is_active === 1);
      setNewPassword('');
      setMessage(null);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!isAdmin) {
      setMessage({ type: 'error', text: 'Unauthorized: Only Administrators can update account credentials.' });
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    try {
      const payload = {
        current_user: currentUser,
        full_name: fullName,
        username: username,
        email: email,
        password: newPassword ? newPassword : null,
        role: targetRole,
        is_active: isActive
      };

      const res = await axios.put(`/api/admin/users/${selectedUserId}`, payload);
      if (res.data && res.data.success) {
        setMessage({ type: 'success', text: res.data.message });
        setNewPassword('');
        // Refresh user list
        axios.get('/api/admin/users').then((r) => setUsersList(r.data.users || []));
      } else {
        setMessage({ type: 'error', text: res.data.message || 'Update failed.' });
      }
    } catch (err) {
      const errText = err.response?.data?.detail || err.message || 'Failed to update user.';
      setMessage({ type: 'error', text: errText });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-6 md:p-8">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="flex items-center space-x-2">
          <span className="px-2.5 py-0.5 rounded-md bg-blue-100 text-blue-800 text-xs font-semibold uppercase tracking-wider">
            Hospital Security Settings
          </span>
          <span className={`px-2.5 py-0.5 rounded-md text-xs font-semibold flex items-center space-x-1 ${
            isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-slate-200 text-slate-700'
          }`}>
            {isAdmin ? <ShieldCheck className="w-3 h-3 inline" /> : <Lock className="w-3 h-3 inline" />}
            <span>{isAdmin ? "Full Admin Access" : "Read-Only Access"}</span>
          </span>
        </div>
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900 mt-1 tracking-tight">
          Staff Profile & Credential Management
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Role-based access control complying with medical information security policies.
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Security Alert Banner for Non-Admin */}
        {!isAdmin && (
          <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-3 shadow-sm">
            <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-sm">Credential Modifications Restricted to Administrators</div>
              <p className="text-xs text-amber-800 mt-0.5 leading-relaxed">
                In compliance with hospital IT compliance and security protocols, regular users cannot
                alter usernames or passwords. If you require credential renewal or role adjustments, please contact your
                System Administrator.
              </p>
            </div>
          </div>
        )}

        {/* Admin User Selector Dropdown */}
        {isAdmin && usersList.length > 0 && (
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <div className="font-semibold text-sm text-slate-900">Manage Staff Credentials</div>
                <div className="text-xs text-slate-500">Select any staff account in the database to edit</div>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <label className="text-xs font-medium text-slate-600 whitespace-nowrap">Target Account:</label>
              <select
                value={selectedUserId}
                onChange={(e) => handleSelectUser(e.target.value)}
                className="px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-300 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
              >
                {usersList.map((u) => (
                  <option key={u.user_id} value={u.user_id}>
                    {u.full_name} ({u.username}) • {u.role}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Profile Card & Edit Form */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8">
          {/* Clinician Identity Card */}
          <div className="flex items-center space-x-4 pb-5 border-b border-slate-100 mb-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#1982BF] to-cyan-500 text-white font-bold text-xl flex items-center justify-center shadow-md">
              {fullName ? fullName.split(' ').filter(Boolean).map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'AW'}
            </div>
            <div>
              <div className="text-base font-bold text-slate-900">{fullName || 'User'}</div>
              <div className="text-xs text-slate-500 font-mono">Department of Radiology & Thoracic Imaging</div>
              <div className="mt-1 inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Active User Session (AES-256 Vault Verified)</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleUpdate} className="space-y-6">
            {/* Status Message */}
            {message && (
              <div className={`p-4 rounded-xl text-sm flex items-center space-x-2.5 ${
                message.type === 'success' 
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' 
                  : 'bg-rose-50 text-rose-800 border border-rose-200'
              }`}>
                {message.type === 'success' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                )}
                <span>{message.text}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Full Name */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-2 focus:ring-[#1982bf] focus:border-[#1982bf] text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="e.g. Dr. Alexander Wright, MD"
                  required
                />
              </div>

              {/* Username */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Username</span>
                  {!isAdmin && <Lock className="w-3 h-3 text-slate-400" />}
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="Username"
                  required
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-4 py-2.5 rounded-xl border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="physician@radivision.ai"
                  required
                />
              </div>

              {/* Role */}
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                  Assigned PACS Role
                </label>
                {isAdmin ? (
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 focus:ring-2 focus:ring-[#1982bf]"
                  >
                    <option value="User">User</option>
                    <option value="Admin">Admin</option>
                  </select>
                ) : (
                  <input
                    type="text"
                    value={targetRole === 'Admin' ? 'Admin' : 'User'}
                    disabled
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-sm text-slate-500 cursor-not-allowed font-medium"
                  />
                )}
              </div>
            </div>

            {/* Password Section */}
            <div className="pt-4 border-t border-slate-100">
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                <span>{isAdmin ? "Update Password" : "Password Credentials"}</span>
                {!isAdmin && <Lock className="w-3 h-3 text-slate-400" />}
              </label>

              {isAdmin ? (
                <div className="space-y-2">
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password (leave blank to keep unchanged)"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm text-slate-900 focus:ring-2 focus:ring-blue-500 pr-10"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-xs text-slate-500">
                    Must be ≥ 8 chars, including uppercase, lowercase, number, and special character (!@#$%^&*).
                  </p>
                </div>
              ) : (
                <div className="relative">
                  <input
                    type="password"
                    value="••••••••••••"
                    disabled
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-100 text-sm text-slate-400 cursor-not-allowed tracking-widest"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 font-medium flex items-center space-x-1">
                    <Lock className="w-3 h-3 inline" />
                    <span>Admin Managed</span>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-4 flex items-center justify-between">
              <div className="text-xs text-slate-400">
                Security Hash: Salted bcrypt (Cost factor: 12)
              </div>

              {isAdmin ? (
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2.5 rounded-xl bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center space-x-2 shadow-md transition-all cursor-pointer"
                >
                  <Save className="w-4 h-4" />
                  <span>{isSubmitting ? "Saving Updates..." : "Save Credentials"}</span>
                </button>
              ) : (
                <div className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-slate-100 text-slate-400 text-xs font-medium cursor-not-allowed border border-slate-200">
                  <Lock className="w-3.5 h-3.5" />
                  <span>Modification Restricted to Admins</span>
                </div>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
