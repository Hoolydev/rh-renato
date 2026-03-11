import React, { useState, useMemo } from "react";
import {
  Briefcase,
  Users,
  Settings,
  Download,
  Bell,
  Plus,
  Search,
  Phone,
  Mail,
  MapPin,
  Clock,
  Calendar,
  Check,
  X,
  Star,
  Zap,
  ChevronRight,
  UserCircle,
} from "lucide-react";

const MOCK_CANDIDATES = [
  {
    id: 1,
    nome: "Maria Silva",
    origem: "WhatsApp",
    telefone: "(11) 99999-0001",
    email: "mariasilva@email.com",
    completude: 95,
    vaga: "Auxiliar Administrativo",
    urgente: true,
    distancia: "3.2 km",
    tempo: "12 min",
    score_final: 94,
    score_tec: 90,
    score_geo: 100,
    score_comp: 92,
    disponibilidade: "Imediato",
    pretensao: "R$ 1.800",
    faixa_vaga: "R$ 1.500 - R$ 2.000",
    fit_salarial: true,
    etapa: "Entrevista",
    engajamento: "Rápida",
  },
  {
    id: 2,
    nome: "João Souza",
    origem: "WhatsApp",
    telefone: "(11) 99999-0002",
    email: "joaosouza@email.com",
    completude: 80,
    vaga: "Vigilante Patrimonial",
    urgente: false,
    distancia: "7.8 km",
    tempo: "28 min",
    score_final: 87,
    score_tec: 85,
    score_geo: 90,
    score_comp: 88,
    disponibilidade: "15 dias",
    pretensao: "R$ 2.200",
    faixa_vaga: "R$ 2.000 - R$ 2.500",
    fit_salarial: true,
    etapa: "Triagem",
    engajamento: "Rápida",
  },
  {
    id: 3,
    nome: "Ana Ferreira",
    origem: "Email",
    telefone: "(11) 99999-0003",
    email: "anaferreira@email.com",
    completude: 60,
    vaga: "Recepcionista",
    urgente: false,
    distancia: "11.2 km",
    tempo: "35 min",
    score_final: 55,
    score_tec: 70,
    score_geo: 40,
    score_comp: 80,
    disponibilidade: "30 dias",
    pretensao: "R$ 3.500",
    faixa_vaga: "R$ 2.000 - R$ 2.500",
    fit_salarial: false,
    etapa: "Triagem",
    engajamento: "Lenta",
  },
  {
    id: 4,
    nome: "Carlos Lima",
    origem: "Upload",
    telefone: "(11) 99999-0004",
    email: "carloslima@email.com",
    completude: 100,
    vaga: "Assistente Financeiro",
    urgente: false,
    distancia: "5.1 km",
    tempo: "18 min",
    score_final: 78,
    score_tec: 82,
    score_geo: 75,
    score_comp: 70,
    disponibilidade: "15 dias",
    pretensao: "R$ 2.800",
    faixa_vaga: "R$ 2.500 - R$ 3.000",
    fit_salarial: true,
    etapa: "Proposta",
    engajamento: "Rápida",
  },
];

// Reusable Components
const Badge = ({ children, colorClass, className = "" }) => (
  <span
    className={`px-2 py-0.5 rounded-full text-xs font-medium ${colorClass} ${className}`}
  >
    {children}
  </span>
);

const ProgressBar = ({ label, value, colorClass }) => (
  <div className="flex items-center gap-2 mb-1">
    <span className="text-[10px] text-gray-500 w-8">{label}</span>
    <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full ${colorClass}`}
        style={{ width: `${value}%` }}
      />
    </div>
    <span className="text-[10px] font-medium w-5 text-right">{value}</span>
  </div>
);

const FunnelProgress = ({ etapa }) => {
  const steps = { Triagem: 1, Entrevista: 2, Proposta: 3, Contratado: 4 };
  const currentStep = steps[etapa] || 0;

  return (
    <div className="flex gap-1 mt-1">
      {[1, 2, 3, 4].map((step) => (
        <div
          key={step}
          className={`w-2 h-2 rounded-full ${step <= currentStep ? "bg-current opacity-80" : "bg-gray-200"}`}
        />
      ))}
    </div>
  );
};

export default function ReclutamentoDashboard() {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterScore, setFilterScore] = useState("Todos");
  const [filterEtapa, setFilterEtapa] = useState("Todos");
  const [filterFonte, setFilterFonte] = useState("Todos");
  const [filterDisp, setFilterDisp] = useState("Todos");

  const [favorites, setFavorites] = useState(new Set());
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const toggleFavorite = (id) => {
    setFavorites((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) newSet.delete(id);
      else newSet.add(id);
      return newSet;
    });
  };

  const filteredCandidates = useMemo(() => {
    return MOCK_CANDIDATES.filter((c) => {
      const matchSearch =
        c.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.vaga.toLowerCase().includes(searchTerm.toLowerCase());

      let matchScore = true;
      if (filterScore === "Alto") matchScore = c.score_final >= 80;
      else if (filterScore === "Médio")
        matchScore = c.score_final >= 60 && c.score_final <= 79;
      else if (filterScore === "Baixo") matchScore = c.score_final < 60;

      const matchEtapa = filterEtapa === "Todos" || c.etapa === filterEtapa;
      const matchFonte =
        filterFonte === "Todos" ||
        (filterFonte === "Upload"
          ? c.origem === "Upload"
          : c.origem === filterFonte);
      const matchDisp =
        filterDisp === "Todos" || c.disponibilidade === filterDisp;

      return matchSearch && matchScore && matchEtapa && matchFonte && matchDisp;
    });
  }, [searchTerm, filterScore, filterEtapa, filterFonte, filterDisp]);

  return (
    <div className="min-h-screen bg-[#F4F4F5] font-['Inter'] text-[#0A0A0A] flex overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 bg-white border-r border-gray-200 flex flex-col items-center py-6 gap-8 z-10 shrink-0">
        <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center text-white font-bold text-xl mb-4">
          RH
        </div>
        <button
          className="p-3 text-gray-400 hover:text-black hover:bg-gray-50 rounded-xl transition-colors"
          title="Vagas"
        >
          <Briefcase size={22} />
        </button>
        <button
          className="p-3 text-black bg-gray-50 rounded-xl shadow-sm"
          title="Candidatos"
        >
          <Users size={22} />
        </button>
        <div className="flex-1" />
        <button
          className="p-3 text-gray-400 hover:text-black hover:bg-gray-50 rounded-xl transition-colors"
          title="Configurações"
        >
          <Settings size={22} />
        </button>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <header className="bg-white border-b border-gray-200 px-8 h-20 flex items-center justify-between shrink-0">
          <nav className="flex gap-8">
            <button className="text-gray-500 hover:text-black font-medium text-sm transition-colors">
              Vagas Abertas
            </button>
            <button className="text-black font-semibold text-sm border-b-2 border-black pb-1">
              Meus Candidatos
            </button>
            <button className="text-gray-500 hover:text-black font-medium text-sm transition-colors">
              Configurações
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <button className="p-2 text-gray-400 hover:text-black transition-colors rounded-full hover:bg-gray-50">
              <Download size={20} />
            </button>
            <button className="p-2 text-gray-400 hover:text-black transition-colors rounded-full hover:bg-gray-50 relative">
              <Bell size={20} />
              <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white" />
            </button>
            <div className="w-9 h-9 rounded-full bg-gray-200 overflow-hidden cursor-pointer border border-gray-300">
              <img
                src="https://i.pravatar.cc/150?img=33"
                alt="Admin"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </header>

        {/* Page Content Scrollable Area */}
        <div className="flex-1 overflow-auto p-8">
          {/* Dashboard Header */}
          <div className="flex justify-between items-end mb-8">
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-2">
                Bem-vindo de volta, Recrutador
              </h1>
              <p className="text-gray-500 text-sm font-medium">
                12 novos candidatos processados &bull; Média Lead Score: 87/100
              </p>
            </div>
            <button className="bg-black hover:bg-gray-800 text-white px-5 py-2.5 rounded-xl font-medium flex items-center gap-2 shadow-sm transition-all hover:-translate-y-0.5">
              <Plus size={18} />
              Postar Nova Vaga
            </button>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col min-h-[500px]">
            {/* Filters */}
            <div className="p-5 border-b border-gray-100 flex flex-wrap items-center gap-4">
              <div className="relative flex-1 min-w-[200px] max-w-sm">
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                  size={18}
                />
                <input
                  type="text"
                  placeholder="Buscar por nome ou vaga..."
                  className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-black/5"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <select
                className="bg-gray-50 border border-gray-200 text-sm rounded-xl py-2 px-3 focus:outline-none focus:border-gray-300 cursor-pointer text-gray-700"
                value={filterScore}
                onChange={(e) => setFilterScore(e.target.value)}
              >
                <option value="Todos">Score: Todos</option>
                <option value="Alto">Alto (≥80)</option>
                <option value="Médio">Médio (60-79)</option>
                <option value="Baixo">Baixo (&lt;60)</option>
              </select>

              <select
                className="bg-gray-50 border border-gray-200 text-sm rounded-xl py-2 px-3 focus:outline-none focus:border-gray-300 cursor-pointer text-gray-700"
                value={filterEtapa}
                onChange={(e) => setFilterEtapa(e.target.value)}
              >
                <option value="Todos">Etapa: Todas</option>
                <option value="Triagem">Triagem</option>
                <option value="Entrevista">Entrevista</option>
                <option value="Proposta">Proposta</option>
                <option value="Contratado">Contratado</option>
              </select>

              <select
                className="bg-gray-50 border border-gray-200 text-sm rounded-xl py-2 px-3 focus:outline-none focus:border-gray-300 cursor-pointer text-gray-700"
                value={filterFonte}
                onChange={(e) => setFilterFonte(e.target.value)}
              >
                <option value="Todos">Fonte: Todas</option>
                <option value="WhatsApp">WhatsApp</option>
                <option value="Email">Email</option>
                <option value="Upload">Upload</option>
              </select>

              <select
                className="bg-gray-50 border border-gray-200 text-sm rounded-xl py-2 px-3 focus:outline-none focus:border-gray-300 cursor-pointer text-gray-700"
                value={filterDisp}
                onChange={(e) => setFilterDisp(e.target.value)}
              >
                <option value="Todos">Disp: Todas</option>
                <option value="Imediato">Imediato</option>
                <option value="15 dias">15 dias</option>
                <option value="30 dias">30 dias</option>
              </select>
            </div>

            {/* Table */}
            <div className="flex-1 overflow-x-auto">
              <table className="w-full text-left whitespace-nowrap">
                <thead>
                  <tr className="text-[11px] font-semibold text-gray-500 tracking-wider uppercase border-b border-gray-100 bg-gray-50/50">
                    <th className="px-5 py-4 font-semibold">
                      Candidato e Contato
                    </th>
                    <th className="px-5 py-4 font-semibold">Vaga Aplicada</th>
                    <th className="px-5 py-4 font-semibold">Distância</th>
                    <th className="px-5 py-4 font-semibold">Score Final</th>
                    <th className="px-5 py-4 font-semibold">
                      Scores Detalhados
                    </th>
                    <th className="px-5 py-4 font-semibold">Disponibilidade</th>
                    <th className="px-5 py-4 font-semibold">
                      Pretensão Salarial
                    </th>
                    <th className="px-5 py-4 font-semibold">Etapa do Funil</th>
                    <th className="px-5 py-4 font-semibold">Engajamento</th>
                    <th className="px-5 py-4 font-semibold text-right">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {filteredCandidates.map((c) => {
                    const isHigh = c.score_final >= 80;
                    const isMed = c.score_final >= 60 && c.score_final < 80;

                    return (
                      <tr
                        key={c.id}
                        className="border-b border-gray-50 hover:bg-gray-50/80 transition-colors animate-in fade-in duration-300 group"
                      >
                        {/* 1. Candidato e Contato */}
                        <td className="px-5 py-4">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-bold text-gray-900">
                              {c.nome}
                            </span>
                            <Badge
                              colorClass={
                                c.origem === "WhatsApp"
                                  ? "bg-emerald-100 text-emerald-700"
                                  : c.origem === "Email"
                                    ? "bg-blue-100 text-blue-700"
                                    : "bg-purple-100 text-purple-700"
                              }
                            >
                              {c.origem}
                            </Badge>
                          </div>
                          <div className="flex flex-col gap-0.5 text-xs text-gray-500">
                            <span className="flex items-center gap-1.5">
                              <Phone size={12} /> {c.telefone}
                            </span>
                            <span className="flex items-center gap-1.5">
                              <Mail size={12} /> {c.email}
                            </span>
                            <span className="mt-1 text-[10px] text-gray-400">
                              Perfil {c.completude}% completo
                            </span>
                          </div>
                        </td>

                        {/* 2. Vaga Aplicada */}
                        <td className="px-5 py-4 align-top">
                          <div className="font-bold text-gray-800 mb-1">
                            {c.vaga}
                          </div>
                          {c.urgente && (
                            <Badge colorClass="bg-red-100 text-red-600 animate-pulse inline-flex items-center gap-1">
                              <Zap size={10} className="fill-current" /> Urgente
                            </Badge>
                          )}
                        </td>

                        {/* 3. Distância */}
                        <td className="px-5 py-4 align-top">
                          <div className="flex flex-col gap-1.5 text-gray-600 text-xs font-medium">
                            <span className="flex items-center gap-1.5">
                              <MapPin size={14} className="text-gray-400" />{" "}
                              {c.distancia}
                            </span>
                            <span className="flex items-center gap-1.5">
                              <Clock size={14} className="text-gray-400" />{" "}
                              {c.tempo}
                            </span>
                          </div>
                        </td>

                        {/* 4. Score Final */}
                        <td className="px-5 py-4 align-top">
                          <div
                            className={`
                            inline-flex items-center justify-center w-12 h-12 rounded-xl font-bold text-lg
                            ${isHigh ? "bg-emerald-100 text-emerald-700" : isMed ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"}
                          `}
                          >
                            {c.score_final}%
                          </div>
                        </td>

                        {/* 5. Scores Detalhados */}
                        <td className="px-5 py-4 align-top w-32">
                          <div className="flex flex-col justify-center h-full">
                            <ProgressBar
                              label="Téc"
                              value={c.score_tec}
                              colorClass="bg-blue-500"
                            />
                            <ProgressBar
                              label="Geo"
                              value={c.score_geo}
                              colorClass="bg-purple-500"
                            />
                            <ProgressBar
                              label="Cmp"
                              value={c.score_comp}
                              colorClass="bg-orange-500"
                            />
                          </div>
                        </td>

                        {/* 6. Disponibilidade */}
                        <td className="px-5 py-4 align-top">
                          <Badge
                            colorClass={`
                            flex items-center gap-1 w-fit
                            ${
                              c.disponibilidade === "Imediato"
                                ? "bg-emerald-100 text-emerald-700"
                                : c.disponibilidade === "15 dias"
                                  ? "bg-amber-100 text-amber-700"
                                  : "bg-gray-100 text-gray-700"
                            }
                          `}
                          >
                            <Calendar size={10} /> {c.disponibilidade}
                          </Badge>
                        </td>

                        {/* 7. Pretensão Salarial */}
                        <td className="px-5 py-4 align-top">
                          <div className="group/tooltip relative inline-flex items-center gap-1.5 font-medium text-gray-800 cursor-help">
                            {c.pretensao}
                            {c.fit_salarial ? (
                              <Check
                                size={14}
                                className="text-emerald-500 stroke-[3]"
                              />
                            ) : (
                              <X
                                size={14}
                                className="text-red-500 stroke-[3]"
                              />
                            )}
                            {/* Tooltip */}
                            <div className="absolute opacity-0 group-hover/tooltip:opacity-100 bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-[10px] rounded pointer-events-none transition-opacity whitespace-nowrap z-10">
                              Faixa: {c.faixa_vaga}
                            </div>
                          </div>
                        </td>

                        {/* 8. Etapa do Funil */}
                        <td className="px-5 py-4 align-top">
                          <div className="flex flex-col gap-1 items-start">
                            <Badge
                              colorClass={`
                              ${
                                c.etapa === "Triagem"
                                  ? "bg-gray-100 text-gray-600"
                                  : c.etapa === "Entrevista"
                                    ? "bg-blue-100 text-blue-700"
                                    : c.etapa === "Proposta"
                                      ? "bg-purple-100 text-purple-700"
                                      : "bg-emerald-100 text-emerald-700"
                              }
                            `}
                            >
                              {c.etapa}
                            </Badge>
                            <div
                              className={`text-${c.etapa === "Triagem" ? "gray-400" : c.etapa === "Entrevista" ? "blue-500" : c.etapa === "Proposta" ? "purple-500" : "emerald-500"}`}
                            >
                              <FunnelProgress etapa={c.etapa} />
                            </div>
                          </div>
                        </td>

                        {/* 9. Engajamento */}
                        <td className="px-5 py-4 align-top">
                          <div
                            className={`flex items-center gap-1.5 text-xs font-semibold ${c.engajamento === "Rápida" ? "text-emerald-600" : "text-red-500"}`}
                          >
                            <Zap
                              size={14}
                              className={
                                c.engajamento === "Rápida" ? "fill-current" : ""
                              }
                            />
                            {c.engajamento === "Rápida"
                              ? "Resposta rápida"
                              : "Resposta lenta"}
                          </div>
                        </td>

                        {/* 10. Ações */}
                        <td className="px-5 py-4 align-top text-right">
                          <div className="flex items-center justify-end gap-2 text-gray-400">
                            <button
                              onClick={() => toggleFavorite(c.id)}
                              className={`p-1.5 rounded-lg hover:bg-gray-100 transition-colors ${favorites.has(c.id) ? "text-yellow-400" : "hover:text-yellow-400"}`}
                            >
                              <Star
                                size={18}
                                className={
                                  favorites.has(c.id) ? "fill-current" : ""
                                }
                              />
                            </button>
                            {/* Simulate WhatsApp Icon */}
                            <button
                              className="p-1.5 rounded-lg hover:bg-emerald-50 hover:text-emerald-600 transition-colors"
                              title="Contatar no WhatsApp"
                            >
                              <svg
                                width="18"
                                height="18"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                              </svg>
                            </button>
                            <button
                              onClick={() => setSelectedCandidate(c)}
                              className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 text-xs font-semibold rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm ml-1"
                            >
                              Ver Perfil
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {filteredCandidates.length === 0 && (
                    <tr>
                      <td
                        colSpan="10"
                        className="px-5 py-12 text-center text-gray-500"
                      >
                        Nenhum candidato encontrado com estes filtros.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      {/* --- Drawer Overlay & Panel --- */}
      {selectedCandidate && (
        <>
          <div
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 transition-opacity animate-in fade-in"
            onClick={() => setSelectedCandidate(null)}
          />
          <div className="fixed inset-y-0 right-0 w-[450px] bg-white shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-300">
            <div className="h-16 border-b border-gray-100 flex items-center justify-between px-6 shrink-0">
              <h2 className="font-semibold text-lg flex items-center gap-2">
                Perfil do Candidato
              </h2>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="p-1.5 text-gray-400 hover:text-black rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-8">
              {/* Header Drawer */}
              <div className="flex gap-4 items-center mb-8">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center text-gray-400 shrink-0">
                  <UserCircle size={40} className="stroke-1" />
                </div>
                <div>
                  <h3 className="text-xl font-bold">
                    {selectedCandidate.nome}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge colorClass="bg-gray-100 text-gray-600">
                      {selectedCandidate.origem}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      Aplicou para {selectedCandidate.vaga}
                    </span>
                  </div>
                </div>
              </div>

              {/* Big Score */}
              <div className="flex justify-between items-center bg-gray-50 border border-gray-100 rounded-2xl p-5 mb-8">
                <div>
                  <div className="text-sm font-semibold text-gray-600">
                    Lead Score Geral
                  </div>
                  <div className="text-xs text-gray-400 mt-0.5">
                    Recomendação Alta da IA
                  </div>
                </div>
                <div className="text-4xl font-black text-emerald-600">
                  {selectedCandidate.score_final}%
                </div>
              </div>

              {/* Pseudo Radar/Bars Details */}
              <div className="mb-8">
                <h4 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
                  Análise Detalhada (IA)
                </h4>
                <div className="flex flex-col gap-3">
                  <ProgressBar
                    label="Técnico"
                    value={selectedCandidate.score_tec}
                    colorClass="bg-blue-500"
                  />
                  <ProgressBar
                    label="Geográfico"
                    value={selectedCandidate.score_geo}
                    colorClass="bg-purple-500"
                  />
                  <ProgressBar
                    label="Comportamento"
                    value={selectedCandidate.score_comp}
                    colorClass="bg-orange-500"
                  />
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] text-gray-500 w-20">
                      Engajamento
                    </span>
                    <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${selectedCandidate.engajamento === "Rápida" ? "bg-emerald-500 w-[95%]" : "bg-red-500 w-[40%]"}`}
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] text-gray-500 w-20">
                      Fit Salarial
                    </span>
                    <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${selectedCandidate.fit_salarial ? "bg-emerald-500 w-[100%]" : "bg-red-500 w-[30%]"}`}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="h-px bg-gray-100 w-full mb-6" />

              {/* Info Blocks */}
              <div className="flex flex-col gap-6">
                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
                    Contato
                  </h4>
                  <div className="text-sm border border-gray-100 rounded-xl p-3 bg-white shadow-sm flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-gray-700">
                      <Phone size={14} className="text-gray-400" />{" "}
                      {selectedCandidate.telefone}
                    </div>
                    <div className="flex items-center gap-2 text-gray-700">
                      <Mail size={14} className="text-gray-400" />{" "}
                      {selectedCandidate.email}
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
                    Estabilidade Profissional
                  </h4>
                  <p className="text-sm text-gray-600 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />{" "}
                    Tempo médio em empregos: <strong>2.5 anos</strong>
                  </p>
                </div>

                <div>
                  <h4 className="text-sm font-bold uppercase tracking-wider text-gray-400 mb-2">
                    Pretensão Salarial
                  </h4>
                  <div className="text-sm flex items-center justify-between bg-gray-50 p-3 rounded-xl border border-gray-100">
                    <div>
                      <span className="block text-xs text-gray-500 mb-0.5">
                        Pretensão
                      </span>
                      <strong
                        className={
                          selectedCandidate.fit_salarial
                            ? "text-emerald-700"
                            : "text-red-600"
                        }
                      >
                        {selectedCandidate.pretensao}
                      </strong>
                    </div>
                    <div className="text-gray-300">/</div>
                    <div className="text-right">
                      <span className="block text-xs text-gray-500 mb-0.5">
                        Faixa da Vaga
                      </span>
                      <strong className="text-gray-700">
                        {selectedCandidate.faixa_vaga}
                      </strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer Actions */}
            <div className="p-6 bg-gray-50 border-t border-gray-100 shrink-0 flex flex-col gap-3">
              <button className="w-full bg-black text-white py-3 rounded-xl font-semibold shadow-sm hover:bg-gray-800 transition-colors flex justify-center items-center gap-2">
                Avançar no Funil <ChevronRight size={16} />
              </button>
              <div className="flex gap-3">
                <button className="flex-1 bg-white border border-gray-200 text-gray-700 py-2.5 rounded-xl font-medium hover:bg-emerald-50 hover:text-emerald-600 hover:border-emerald-200 transition-colors flex justify-center items-center gap-2 text-sm">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                  </svg>
                  WhatsApp
                </button>
                <button className="flex-1 bg-white border border-gray-200 text-red-600 py-2.5 rounded-xl font-medium hover:bg-red-50 hover:border-red-200 transition-colors text-sm">
                  Reprovar
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
