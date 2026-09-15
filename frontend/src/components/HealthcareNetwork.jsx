import React, { useState } from 'react';
import { Building2, UserCheck, Phone, Mail, MapPin, ExternalLink, ShieldCheck, Stethoscope } from 'lucide-react';

export default function HealthcareNetwork() {
  const [selectedCity, setSelectedCity] = useState("ALL");

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
      modality: "Bone"
    },
    {
      city: "Islamabad",
      hospital: "Maroof International Hospital",
      specialty: "Pulmonology & Critical Respiratory Care",
      doctor: "Dr. Asim Yusuf, MRCP",
      phone: "+92 51 2222920",
      email: "info@maroof.com.pk",
      address: "10th Ave, F-10 Markaz, Islamabad",
      modality: "Chest"
    },
    {
      city: "Islamabad",
      hospital: "Kulsum International Hospital",
      specialty: "Cardiothoracic & Chest Diseases",
      doctor: "Dr. Aamer Ikram, FCPS",
      phone: "+92 51 8446666",
      email: "contact@kulsumhospital.com",
      address: "Blue Area, G 6/2, Islamabad",
      modality: "Chest"
    },
    // New York
    {
      city: "New York",
      hospital: "Hospital for Special Surgery (HSS)",
      specialty: "Orthopedic Trauma Service",
      doctor: "Dr. David L. Helfet, MD",
      phone: "+1 212-606-1000",
      email: "orthotrauma@hss.edu",
      address: "535 E 70th St, New York, NY 10021",
      modality: "Bone"
    },
    {
      city: "New York",
      hospital: "Lenox Hill Hospital (Northwell Health)",
      specialty: "Pulmonary & Critical Care Medicine",
      doctor: "Dr. Michael Schwartz, MD",
      phone: "+1 212-434-2000",
      email: "referrals@northwell.edu",
      address: "100 E 77th St, New York, NY 10075",
      modality: "Chest"
    },
    {
      city: "New York",
      hospital: "NYU Langone Orthopedic Center",
      specialty: "Department of Orthopedic Surgery",
      doctor: "Dr. Kenneth Egol, MD",
      phone: "+1 212-598-6000",
      email: "inquiries@nyulangone.org",
      address: "333 E 38th St, New York, NY 10016",
      modality: "Bone"
    },
    // Karachi
    {
      city: "Karachi",
      hospital: "Aga Khan University Hospital (AKUH)",
      specialty: "Orthopedic Trauma & Reconstructive Surgery",
      doctor: "Dr. Pervaiz Hashmi, FCPS",
      phone: "+92 21 111 911 911",
      email: "referrals@aku.edu",
      address: "National Stadium Rd, Karachi",
      modality: "Bone"
    },
    {
      city: "Karachi",
      hospital: "National Institute of Cardiovascular Diseases (NICVD)",
      specialty: "Thoracic & Chest Critical Care",
      doctor: "Dr. Javaid Khan, FRCP",
      phone: "+92 21 99201271",
      email: "chest@nicvd.org",
      address: "Rafiqui Shaheed Rd, Karachi",
      modality: "Chest"
    },
    // Lahore
    {
      city: "Lahore",
      hospital: "Doctors Hospital & Medical Center",
      specialty: "Orthopedic Surgery & Joint Replacement",
      doctor: "Dr. Muhammad Hanif, FRCS",
      phone: "+92 42 111 223 377",
      email: "appointments@doctorshospital.com.pk",
      address: "Canal Bank Rd, Johar Town, Lahore",
      modality: "Bone"
    }
  ];

  const cities = ["ALL", "Islamabad", "New York", "Karachi", "Lahore"];

  const filtered = directory.filter(d => 
    selectedCity === "ALL" || d.city.toLowerCase() === selectedCity.toLowerCase()
  );

  return (
    <div className="flex-1 overflow-y-auto bg-[#070b14] text-slate-100 p-6 md:p-8 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-cyan-300 text-xs font-mono mb-2">
            <Building2 className="w-3.5 h-3.5" />
            <span>GPS Healthcare & Specialist Referral Registry</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-white tracking-tight">
            Hospital & Specialist Network
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Curated hospital directory and specialist physicians automatically populated into patient RSNA clinical reports.
          </p>
        </div>

        {/* City Filter Pills */}
        <div className="flex items-center space-x-2 self-start md:self-auto overflow-x-auto pb-1">
          {cities.map((city) => (
            <button
              key={city}
              onClick={() => setSelectedCity(city)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-colors cursor-pointer ${
                selectedCity === city
                  ? "bg-cyan-600 text-white shadow-md shadow-cyan-600/30"
                  : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {city}
            </button>
          ))}
        </div>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((item, idx) => (
          <div
            key={idx}
            className="p-5 rounded-2xl bg-[#0e1626]/80 border border-slate-800/80 hover:border-cyan-500/40 backdrop-blur-md shadow-xl transition-all flex flex-col justify-between space-y-4"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-950/70 border border-cyan-500/40 text-cyan-300">
                  {item.city}
                </span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                  item.modality === 'Bone' ? 'bg-amber-950/60 text-amber-300 border border-amber-500/30' : 'bg-blue-950/60 text-blue-300 border border-blue-500/30'
                }`}>
                  {item.modality === 'Bone' ? 'Orthopedics / Trauma' : 'Pulmonology / Chest'}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
                  <Building2 className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span className="truncate">{item.hospital}</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{item.specialty}</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 space-y-1.5 text-xs">
                <div className="flex items-center space-x-2 text-emerald-300 font-medium">
                  <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{item.doctor}</span>
                </div>
                <div className="flex items-center space-x-2 text-slate-400 font-mono text-[11px]">
                  <Phone className="w-3.5 h-3.5 text-cyan-400" />
                  <a href={`tel:${item.phone}`} className="hover:text-cyan-300">{item.phone}</a>
                </div>
                <div className="flex items-center space-x-2 text-slate-400 font-mono text-[11px] truncate">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  <a href={`mailto:${item.email}`} className="hover:text-cyan-300 truncate">{item.email}</a>
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-500">
              <span className="flex items-center space-x-1 truncate max-w-[200px]">
                <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                <span className="truncate">{item.address}</span>
              </span>
              <span className="text-cyan-400 flex items-center space-x-0.5 font-medium">
                <span>Direct Referral</span>
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
