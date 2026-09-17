import React, { useState } from 'react';
import { Building2, UserCheck, Phone, Mail, MapPin, ExternalLink, ShieldCheck, Stethoscope, Search } from 'lucide-react';

export default function HealthcareNetwork() {
  const [selectedCity, setSelectedCity] = useState("ALL");
  const [searchFilter, setSearchFilter] = useState("");

  const directory = [
    // Islamabad
    {
      city: "Islamabad",
      hospital: "Shifa International Hospital",
      specialty: "Orthopedic Surgery & Trauma Centre",
      doctor: "Dr. Tariq Mahmood, FRCS",
      phone: "+92 51 8463000",
      email: "referrals@shifa.com.pk",
      address: "Pitras Bukhari Rd, H-8/4, Islamabad",
      modality: "Bone",
      rating: "4.9 ★"
    },
    {
      city: "Islamabad",
      hospital: "Maroof International Hospital",
      specialty: "Pulmonology & Critical Respiratory Care",
      doctor: "Dr. Asim Yusuf, MRCP",
      phone: "+92 51 2222920",
      email: "info@maroof.com.pk",
      address: "10th Ave, F-10 Markaz, Islamabad",
      modality: "Chest",
      rating: "4.8 ★"
    },
    {
      city: "Islamabad",
      hospital: "Kulsum International Hospital",
      specialty: "Cardiothoracic & Chest Diseases",
      doctor: "Dr. Aamer Ikram, FCPS",
      phone: "+92 51 8446666",
      email: "contact@kulsumhospital.com",
      address: "Blue Area, G 6/2, Islamabad",
      modality: "Chest",
      rating: "4.7 ★"
    },
    // Rawalpindi
    {
      city: "Rawalpindi",
      hospital: "Holy Family Hospital",
      specialty: "Department of Orthopedic Surgery & Trauma",
      doctor: "Prof. Dr. Asad Noor, FCPS",
      phone: "+92 51 9290321",
      email: "referrals@hfh.gov.pk",
      address: "Murree Rd, Satellite Town, Rawalpindi",
      modality: "Bone",
      rating: "4.9 ★"
    },
    {
      city: "Rawalpindi",
      hospital: "Rawalpindi Institute of Cardiology & Chest Diseases (RIC)",
      specialty: "Pulmonology & Acute Chest Care",
      doctor: "Prof. Dr. Shazli Manzoor, FCPS",
      phone: "+92 51 9281200",
      email: "chest@ric.punjab.gov.pk",
      address: "Rawal Rd, Rawalpindi",
      modality: "Chest",
      rating: "4.9 ★"
    },
    {
      city: "Rawalpindi",
      hospital: "Combined Military Hospital (CMH) Rawalpindi",
      specialty: "Institute of Orthopedics & Polytrauma",
      doctor: "Brig. Dr. Sohail Amin, FRCS",
      phone: "+92 51 5565111",
      email: "trauma@cmh.org.pk",
      address: "Abid Majeed Rd, Cantt, Rawalpindi",
      modality: "Bone",
      rating: "4.9 ★"
    },
    // Lahore
    {
      city: "Lahore",
      hospital: "Ghurki Trust Teaching Hospital",
      specialty: "Spine & Orthopedic Trauma Center",
      doctor: "Prof. Dr. Amer Aziz, FRCS",
      phone: "+92 42 36581401",
      email: "ortho@ghurkitrust.org.pk",
      address: "Jallo Mor, Lahore",
      modality: "Bone",
      rating: "4.9 ★"
    },
    {
      city: "Lahore",
      hospital: "Gulab Devi Chest Hospital",
      specialty: "Institute of Pulmonary & Respiratory Medicine",
      doctor: "Prof. Dr. Kamran Chatha, FCPS",
      phone: "+92 42 35841081",
      email: "referrals@gulabdevi.org",
      address: "Ferozepur Rd, Lahore",
      modality: "Chest",
      rating: "4.9 ★"
    },
    // Karachi
    {
      city: "Karachi",
      hospital: "Aga Khan University Hospital (AKUH)",
      specialty: "Orthopedic Trauma & Musculoskeletal Care",
      doctor: "Prof. Dr. Masood Umer, FCPS",
      phone: "+92 21 111 911 911",
      email: "referrals@aku.edu",
      address: "Stadium Rd, Karachi",
      modality: "Bone",
      rating: "5.0 ★"
    },
    {
      city: "Karachi",
      hospital: "Ojha Institute of Chest Diseases (Dow University)",
      specialty: "Pulmonary Medicine & Critical Care",
      doctor: "Prof. Dr. Javaid Khan, FRCP",
      phone: "+92 21 99232660",
      email: "chest@duhs.edu.pk",
      address: "SUPARCO Rd, Gulzar-e-Hijri, Karachi",
      modality: "Chest",
      rating: "4.9 ★"
    }
  ];

  const cities = ["ALL", "Rawalpindi", "Islamabad", "Lahore", "Karachi"];

  const filtered = directory.filter(d => {
    const matchesCity = selectedCity === "ALL" || d.city.toLowerCase() === selectedCity.toLowerCase();
    const term = searchFilter.toLowerCase();
    const matchesSearch = !term || (
      d.hospital.toLowerCase().includes(term) ||
      d.doctor.toLowerCase().includes(term) ||
      d.specialty.toLowerCase().includes(term)
    );
    return matchesCity && matchesSearch;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-slate-50 text-slate-900 font-sans p-6 md:p-8 space-y-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-xs font-semibold mb-2">
            <Building2 className="w-3.5 h-3.5 text-blue-600" />
            <span>Google Maps GPS Anchored Directory</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
            Hospital & Specialist Network
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Geographic healthcare facility registry for rapid clinical referrals and emergency doctor escalation.
          </p>
        </div>

        {/* City Filter Pills */}
        <div className="flex items-center space-x-2 bg-white p-1 rounded-xl border border-slate-300 shadow-sm self-start md:self-auto">
          {cities.map((city) => (
            <button
              key={city}
              onClick={() => setSelectedCity(city)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold tracking-wider transition-all cursor-pointer ${
                selectedCity === city
                  ? "bg-[#0B1727] text-white shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              {city}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Search Bar */}
        <div className="relative w-full max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search facility name, doctor, or specialty..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded-xl pl-9 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
        </div>

        {/* Directory Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((item, idx) => (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 space-y-4 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-md ${
                    item.modality === 'Bone' ? 'bg-teal-100 text-teal-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {item.modality === 'Bone' ? 'Orthopedic & Trauma' : 'Pulmonary & Respiratory'}
                  </span>
                  <span className="text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded-md">
                    {item.rating}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-base tracking-tight leading-snug">
                  {item.hospital}
                </h3>
                <p className="text-xs text-blue-600 font-medium mt-0.5">
                  {item.specialty}
                </p>

                <div className="pt-3 border-t border-slate-100 mt-3 space-y-2 text-xs text-slate-600">
                  <div className="flex items-center space-x-2 font-semibold text-slate-800">
                    <UserCheck className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{item.doctor}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
                    <span className="truncate">{item.address}</span>
                  </div>
                  <div className="flex items-center space-x-2 font-mono">
                    <Phone className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{item.phone}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Mail className="w-4 h-4 text-slate-400 shrink-0" />
                    <span className="truncate text-blue-600">{item.email}</span>
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-400">Verified Partner</span>
                <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md font-semibold text-[11px]">
                  Emergency Ingestion Active
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
