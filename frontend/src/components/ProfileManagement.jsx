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
  EyeOff,
  Trash2,
  AlertTriangle,
  X,
  RefreshCw
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

  // Deletion Modal State
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

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

  const handleDeleteSelectedUser = async () => {
    const targetId = deleteTargetId || selectedUserId;
    if (!targetId) return;

    const targetUserObj = usersList.find((u) => u.user_id === Number(targetId)) || selectedUser;
    const targetUname = (targetUserObj?.username || '').toLowerCase();

    if (targetUname === 'awaismalik001') {
      setDeleteError("Security Violation: Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.");
      return;
    }
    if (currentUser && (Number(currentUser.user_id) === Number(targetId) || (currentUser.username || '').toLowerCase() === targetUname)) {
      setDeleteError("Action Disallowed: You cannot delete your own active administrative session.");
      return;
    }

    setIsDeleting(true);
    setDeleteError(null);
    try {
      const res = await axios.delete(`/api/admin/users/${targetId}`, {
        data: { current_user: currentUser }
      });
      if (res.data && res.data.success) {
        setShowDeleteModal(false);
        setMessage({ type: 'success', text: res.data.message });
        // Refresh users list
        const updatedRes = await axios.get('/api/admin/users');
        const updatedList = updatedRes.data.users || [];
        setUsersList(updatedList);
        // Switch to logged in user or first available user
        const fallback = updatedList.find(u => u.user_id === currentUser?.user_id) || updatedList[0];
        if (fallback) {
          handleSelectUser(fallback.user_id);
        }
      }
    } catch (err) {
      const errText = err.response?.data?.detail || err.message || 'Failed to delete user.';
      setDeleteError(errText);
    } finally {
      setIsDeleting(false);
    }
  };

  const selectedUser = usersList.find((u) => u.user_id === Number(selectedUserId)) || currentUser;
  const targetToDelete = usersList.find((u) => u.user_id === Number(deleteTargetId || selectedUserId)) || selectedUser;
  const isSelectedMasterAdmin = (selectedUser?.username || username || '').toLowerCase() === 'awaismalik001';
  const isSelectedSelf = currentUser && (
    Number(currentUser.user_id) === Number(selectedUserId) ||
    (currentUser.username || '').toLowerCase() === (selectedUser?.username || username || '').toLowerCase()
  );
  const isTargetToDeleteMasterAdmin = (targetToDelete?.username || '').toLowerCase() === 'awaismalik001';
  const isTargetToDeleteSelf = currentUser && (
    Number(currentUser.user_id) === Number(targetToDelete?.user_id) ||
    (currentUser.username || '').toLowerCase() === (targetToDelete?.username || '').toLowerCase()
  );

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-4 md:p-5 space-y-4">
      {/* Top Header */}
      <div className="max-w-4xl mx-auto border-b border-slate-200 pb-3">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded bg-blue-100 text-[#1982bf] text-[11px] font-bold uppercase tracking-wider">
            Account Management
          </span>
          <span className={`px-2 py-0.5 rounded text-[11px] font-semibold flex items-center space-x-1 ${
            isAdmin ? 'bg-purple-100 text-purple-800' : 'bg-slate-200 text-slate-700'
          }`}>
            {isAdmin ? <ShieldCheck className="w-3 h-3 inline" /> : <Lock className="w-3 h-3 inline" />}
            <span>{isAdmin ? "Full Admin Access" : "Read-Only Access"}</span>
          </span>
        </div>
        <h1 className="text-lg md:text-xl font-bold text-slate-900 mt-1 tracking-tight">
          Staff Profile & Credential Management
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Role-based access control complying with medical information security policies.
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-4">
        {/* Security Alert Banner for Non-Admin */}
        {!isAdmin && (
          <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 flex items-start space-x-2.5 shadow-sm">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-xs">Credential Modifications Restricted to Administrators</div>
              <p className="text-[11px] text-amber-800 mt-0.5 leading-relaxed">
                In compliance with hospital IT compliance and security protocols, regular users cannot
                alter usernames or passwords. If you require credential renewal or role adjustments, please contact your
                System Administrator.
              </p>
            </div>
          </div>
        )}

        {/* Admin User Selector Dropdown */}
        {isAdmin && usersList.length > 0 && (
          <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-3">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
                <Users className="w-4 h-4" />
              </div>
              <div>
                <div className="font-semibold text-xs text-slate-900">Manage Staff Credentials</div>
                <div className="text-[11px] text-slate-500">Select any staff account in the database to edit</div>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <label className="text-xs font-medium text-slate-600 whitespace-nowrap">Target Account:</label>
              <select
                value={selectedUserId}
                onChange={(e) => handleSelectUser(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-sm font-semibold text-slate-900 focus:outline-none focus:ring-1 focus:ring-blue-500 cursor-pointer"
              >
                {usersList.map((u) => (
                  <option key={u.user_id} value={u.user_id}>
                    {u.full_name} ({u.username}) • {u.role}
                  </option>
                ))}
              </select>

              {isSelectedMasterAdmin ? (
                <span className="px-2.5 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-300 text-xs font-semibold flex items-center space-x-1.5 shadow-xs" title="Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.">
                  <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                  <span>Protected Root Admin</span>
                </span>
              ) : isSelectedSelf ? (
                <span className="px-2.5 py-1.5 rounded-lg bg-slate-100 text-slate-600 border border-slate-200 text-xs font-semibold flex items-center space-x-1.5 shadow-xs" title="You cannot delete your own active administrative session.">
                  <Lock className="w-3.5 h-3.5 text-slate-500" />
                  <span>Active Session (Self)</span>
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => {
                    setDeleteTargetId(selectedUserId);
                    setDeleteError(null);
                    setShowDeleteModal(true);
                  }}
                  className="px-2.5 py-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 hover:border-rose-300 text-xs font-semibold flex items-center space-x-1 shadow-xs transition-colors cursor-pointer"
                  title={`Delete ${selectedUser?.role || 'user'} account`}
                >
                  <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                  <span>Delete {selectedUser?.role === 'Admin' ? 'Admin' : 'User'}</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Profile Card & Edit Form */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 md:p-5">
          {/* User Identity Card */}
          <div className="flex items-center space-x-3 pb-3.5 border-b border-slate-100 mb-4">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-[#1982BF] to-cyan-500 text-white font-bold text-sm flex items-center justify-center shadow-sm">
              {fullName ? fullName.split(' ').filter(Boolean).map(n => n[0]).join('').substring(0, 2).toUpperCase() : 'AM'}
            </div>
            <div>
              <div className="text-sm font-bold text-slate-900">{fullName || 'User'}</div>
              <div className="text-xs text-slate-500 font-mono">Department of Radiology & Thoracic Imaging</div>
              <div className="mt-0.5 inline-flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span>Active User Session (AES-256 Vault Verified)</span>
              </div>
            </div>
          </div>

          <form onSubmit={handleUpdate} className="space-y-4">
            {/* Status Message */}
            {message && (
              <div className={`p-3 rounded-lg text-xs flex items-center space-x-2 ${
                message.type === 'success' 
                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' 
                  : 'bg-rose-50 text-rose-800 border border-rose-200'
              }`}>
                {message.type === 'success' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                ) : (
                  <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
                )}
                <span>{message.text}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Full Name */}
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-1 focus:ring-[#1982bf] focus:border-[#1982bf] text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="e.g. Dr. Alexander Wright, MD"
                  required
                />
              </div>

              {/* Username */}
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                  <span>Username</span>
                  {!isAdmin && <Lock className="w-3 h-3 text-slate-400" />}
                </label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="Username"
                  required
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={!isAdmin}
                  className={`w-full px-3 py-1.5 rounded-lg border text-sm transition-colors ${
                    isAdmin 
                      ? 'bg-white border-slate-300 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-slate-900' 
                      : 'bg-slate-100 border-slate-200 text-slate-500 cursor-not-allowed'
                  }`}
                  placeholder="physician@radivision.ai"
                  required
                />
              </div>

              {/* Role */}
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Assigned PACS Role
                </label>
                {isAdmin ? (
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-300 bg-white text-sm text-slate-900 focus:ring-1 focus:ring-[#1982bf]"
                  >
                    <option value="User">User</option>
                    <option value="Admin">Admin</option>
                  </select>
                ) : (
                  <input
                    type="text"
                    value={targetRole === 'Admin' ? 'Admin' : 'User'}
                    disabled
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-100 text-sm text-slate-500 cursor-not-allowed font-medium"
                  />
                )}
              </div>
            </div>

            {/* Password Section */}
            <div className="pt-3 border-t border-slate-100">
              <label className="block text-[11px] font-semibold text-slate-700 uppercase tracking-wider mb-1 flex items-center justify-between">
                <span>{isAdmin ? "Update Password" : "Password Credentials"}</span>
                {!isAdmin && <Lock className="w-3 h-3 text-slate-400" />}
              </label>

              {isAdmin ? (
                <div className="space-y-1.5">
                  <div className="relative">
                    <input
                      type={showPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Enter new password (leave blank to keep unchanged)"
                      className="w-full px-3 py-1.5 rounded-lg border border-slate-300 bg-white text-sm text-slate-900 focus:ring-1 focus:ring-blue-500 pr-9"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 cursor-pointer"
                    >
                      {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Must be ≥ 8 chars, including uppercase, lowercase, number, and special character (!@#$%^&*).
                  </p>
                </div>
              ) : (
                <div className="relative">
                  <input
                    type="password"
                    value="••••••••••••"
                    disabled
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 bg-slate-100 text-sm text-slate-400 cursor-not-allowed tracking-widest"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] text-slate-400 font-medium flex items-center space-x-1">
                    <Lock className="w-3 h-3 inline" />
                    <span>Admin Managed</span>
                  </div>
                </div>
              )}
            </div>

            {/* Bottom Actions */}
            <div className="pt-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-t border-slate-100">
              {isAdmin ? (
                <>
                  <div className="flex items-center space-x-2">
                    {isSelectedMasterAdmin ? (
                      <span className="px-3 py-1.5 rounded-lg bg-amber-50 text-amber-800 border border-amber-300 font-semibold text-xs flex items-center space-x-1.5 shadow-xs" title="Master Administrator 'awaismalik001' is permanently protected and cannot be deleted.">
                        <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                        <span>Protected Root Administrator (Deletion Blocked)</span>
                      </span>
                    ) : isSelectedSelf ? (
                      <span className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-600 border border-slate-200 font-semibold text-xs flex items-center space-x-1.5 shadow-xs" title="You cannot delete your own active administrative session.">
                        <Lock className="w-3.5 h-3.5 text-slate-500" />
                        <span>Active Session Account (Self-Deletion Blocked)</span>
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => {
                          setDeleteTargetId(selectedUserId);
                          setDeleteError(null);
                          setShowDeleteModal(true);
                        }}
                        className="px-3.5 py-2 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 hover:border-rose-300 font-semibold text-xs flex items-center space-x-1.5 shadow-xs transition-colors cursor-pointer"
                        title={`Permanently delete ${targetRole === 'Admin' ? 'Administrator' : 'User'} account`}
                      >
                        <Trash2 className="w-3.5 h-3.5 text-rose-500" />
                        <span>Delete {targetRole === 'Admin' ? 'Admin' : 'User'} Account</span>
                      </button>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 self-end sm:self-auto">
                    <div className="text-[11px] text-slate-400 hidden sm:block">
                      Salted bcrypt (Cost factor: 12)
                    </div>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="px-4 py-2 rounded-lg bg-[#1982bf] hover:bg-[#156ea3] text-white font-semibold text-sm flex items-center space-x-1.5 shadow-sm transition-all cursor-pointer"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>{isSubmitting ? "Saving Updates..." : "Save Credentials"}</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="text-[11px] text-slate-400">
                    Security Hash: Salted bcrypt (Cost factor: 12)
                  </div>
                  <div className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-400 text-[11px] font-medium cursor-not-allowed border border-slate-200">
                    <Lock className="w-3 h-3" />
                    <span>Modification Restricted to Admins</span>
                  </div>
                </>
              )}
            </div>
          </form>
        </div>
      </div>

      {/* Delete User Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl max-w-md w-full p-5 shadow-2xl border border-slate-200 space-y-4"
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-rose-100 text-rose-600 flex items-center justify-center">
                  <Trash2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Delete Staff Account
                  </h3>
                  <p className="text-xs text-slate-500">
                    PACS Security & Access Control
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <p className="text-xs text-slate-600 leading-relaxed">
                Are you sure you want to permanently delete this account? This will immediately revoke credentials and access from the RadiVision AI PACS suite.
              </p>

              {/* Account Selector inside Modal */}
              <div className="space-y-1">
                <label className="text-[11px] font-semibold text-slate-600">Select Account to Delete:</label>
                <select
                  value={deleteTargetId || selectedUserId}
                  onChange={(e) => {
                    setDeleteTargetId(Number(e.target.value));
                    setDeleteError(null);
                  }}
                  className="w-full px-2.5 py-1.5 rounded-lg bg-slate-50 border border-slate-300 text-xs font-semibold text-slate-900 focus:outline-none focus:ring-1 focus:ring-rose-500 cursor-pointer"
                >
                  {usersList.map((u) => {
                    const isUnameMaster = (u.username || '').toLowerCase() === 'awaismalik001';
                    const isUSelf = currentUser && (
                      Number(currentUser.user_id) === Number(u.user_id) || 
                      (currentUser.username || '').toLowerCase() === (u.username || '').toLowerCase()
                    );
                    return (
                      <option key={u.user_id} value={u.user_id}>
                        {u.full_name} (@{u.username}) • {u.role} {isUnameMaster ? '[Protected Root Admin]' : isUSelf ? '[Your Account]' : ''}
                      </option>
                    );
                  })}
                </select>
              </div>

              <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs space-y-2 font-sans">
                <div className="flex justify-between">
                  <span className="text-slate-500">Account Name:</span>
                  <span className="font-bold text-slate-900">{targetToDelete?.full_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Username:</span>
                  <span className="font-mono font-semibold text-slate-800">@{targetToDelete?.username}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Assigned Role:</span>
                  <span className={`font-semibold px-2 py-0.5 rounded text-[11px] ${targetToDelete?.role === 'Admin' ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'}`}>
                    {targetToDelete?.role === 'Admin' ? 'System Administrator' : 'Clinician'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Email:</span>
                  <span className="text-slate-700 font-mono text-[11px]">{targetToDelete?.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Location:</span>
                  <span className="text-slate-700">{targetToDelete?.city || 'Rawalpindi'}, {targetToDelete?.country || 'Pakistan'}</span>
                </div>
              </div>

              {isTargetToDeleteMasterAdmin && (
                <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-300 text-amber-800 text-xs flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-amber-600 shrink-0" />
                  <span>Security Policy: Root Administrator 'awaismalik001' is permanently locked and protected against deletion.</span>
                </div>
              )}

              {isTargetToDeleteSelf && !isTargetToDeleteMasterAdmin && (
                <div className="p-2.5 rounded-lg bg-slate-100 border border-slate-300 text-slate-700 text-xs flex items-center space-x-2">
                  <Lock className="w-4 h-4 text-slate-500 shrink-0" />
                  <span>Self-Deletion Disallowed: You cannot delete your own active administrative account.</span>
                </div>
              )}

              {deleteError && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{deleteError}</span>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                disabled={isDeleting}
                className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteSelectedUser}
                disabled={isDeleting || isTargetToDeleteMasterAdmin || isTargetToDeleteSelf}
                className="px-4 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold shadow-sm transition-all flex items-center space-x-1.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeleting && <RefreshCw className="w-3 h-3 animate-spin" />}
                <span>{isDeleting ? "Deleting..." : "Permanently Delete"}</span>
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
