document.addEventListener('DOMContentLoaded', () => {

    // --- Tab Navigation Logic ---
    const navItems = document.querySelectorAll('.nav-item');
    const topNavBtns = document.querySelectorAll('.top-nav-btn');
    const viewSections = document.querySelectorAll('.view-section');

    function switchTab(targetId) {
        // Sections
        viewSections.forEach(section => {
            if (section.id === targetId) {
                section.classList.remove('hidden');
                section.classList.add('active');
            } else {
                section.classList.add('hidden');
                section.classList.remove('active');
            }
        });

        // Sidebar Nav Styling
        navItems.forEach(nav => {
            if (nav.getAttribute('data-target') === targetId) {
                nav.classList.add('text-black', 'bg-gray-50');
                nav.classList.remove('text-gray-400');
            } else {
                // Ignore non-sidebar navs
                if (nav.classList.contains('active-nav')) {
                    nav.classList.remove('text-black', 'bg-gray-50');
                    nav.classList.add('text-gray-400');
                }
            }
        });

        // Top Navigation Styling
        topNavBtns.forEach(btn => {
            if (btn.getAttribute('data-target') === targetId) {
                btn.classList.add('border-b-2', 'border-black', 'pb-1', 'text-black', 'font-semibold');
                btn.classList.remove('text-gray-500', 'hover:text-black', 'font-medium');
            } else {
                btn.classList.remove('border-b-2', 'border-black', 'pb-1', 'text-black', 'font-semibold');
                btn.classList.add('text-gray-500', 'hover:text-black', 'font-medium');
            }
        });
    }

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('data-target');
            if (targetId) switchTab(targetId);
        });
    });

    topNavBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = btn.getAttribute('data-target');
            if (targetId) switchTab(targetId);
        });
    });

    // Sub-buttons shortcuts
    const btnNovaVaga = document.getElementById('btnNovaVaga');
    if (btnNovaVaga) {
        btnNovaVaga.addEventListener('click', () => switchTab('section-nova-vaga'));
    }

    // Dropdown Profile
    const avatarProfile = document.getElementById('avatarProfile');
    const profileDropdown = document.getElementById('profileDropdown');

    if (avatarProfile && profileDropdown) {
        avatarProfile.addEventListener('click', (e) => {
            e.stopPropagation();
            profileDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!avatarProfile.contains(e.target)) {
                profileDropdown.classList.add('hidden');
            }
        });
    }


    // --- Data: Jobs from API ---
    async function fetchJobs() {
        try {
            const res = await fetch('/api/vagas');
            const result = await res.json();
            return result.data || [];
        } catch (error) {
            console.error('Error fetching jobs:', error);
            // Fallback mock jobs if API is down
            return [
                { id: 1, empresa: "Condomínio Residencial (Offline)", titulo: "Porteiro / Controlador", requisitos_obrigatorios: ["12x36", "CLT"], salario_min: 1800 }
            ];
        }
    }

    async function renderJobs() {
        const jobsGrid = document.getElementById('jobsGrid');
        if (!jobsGrid) return;

        const jobs = await fetchJobs();
        jobsGrid.innerHTML = '';

        jobs.forEach(job => {
            // Transform tags
            let tags = [];
            try {
                if (typeof job.requisitos_obrigatorios === 'string') {
                    tags = JSON.parse(job.requisitos_obrigatorios);
                } else if (Array.isArray(job.requisitos_obrigatorios)) {
                    tags = job.requisitos_obrigatorios;
                }
            } catch (e) {
                tags = [];
            }
            if (job.regime) tags.push(job.regime);

            const tagsHtml = tags.map(t => `<span class="bg-gray-100 text-gray-600 px-2 py-1 rounded-md text-[10px] font-semibold">${t}</span>`).join('');

            // Format currency
            const formatter = new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            });
            const salaryHtml = job.salario_min ? formatter.format(job.salario_min) : "A combinar";

            jobsGrid.innerHTML += `
                <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow relative">
                    <button class="absolute top-4 right-4 text-gray-400 hover:text-black"><i data-lucide="bookmark" class="w-5 h-5"></i></button>
                    <div class="w-12 h-12 bg-gray-50 rounded-xl border border-gray-100 flex items-center justify-center mb-4 p-2">
                        <img src="https://cdn-icons-png.flaticon.com/512/684/684809.png" alt="Logo" class="max-w-full max-h-full">
                    </div>
                    <div class="text-xs font-semibold text-gray-500 mb-1 flex items-center gap-1">${job.empresa || 'Empresa'} <i data-lucide="badge-check" class="w-4 h-4 text-emerald-500"></i></div>
                    <h3 class="font-bold text-lg mb-3">${job.titulo}</h3>
                    <div class="flex gap-2 mb-4 flex-wrap whitespace-normal">${tagsHtml}</div>
                    <div class="font-semibold text-gray-900 mb-6">${salaryHtml}</div>
                    
                    <div class="flex items-center justify-between border-t border-gray-100 pt-4">
                        <div class="flex items-center gap-2 text-sm text-gray-500 font-medium">
                            <i data-lucide="users" class="w-4 h-4"></i> ${Math.floor(Math.random() * 50) + 5}
                        </div>
                        <button class="text-xs font-bold bg-black text-white px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors">Detalhes</button>
                    </div>
                </div>
            `;
        });
        if (window.lucide) window.lucide.createIcons();
    }
    renderJobs();

    // Form Nova Vaga Logic - (Will only affect UI visually, not database for MVP)
    const formNovaVaga = document.getElementById('formNovaVaga');
    if (formNovaVaga) {
        formNovaVaga.addEventListener('submit', async (e) => {
            e.preventDefault();
            // In a real app we would POST to /api/vagas here. For MVP simplicity, just reload or alert.
            const data = {
                titulo: document.getElementById('nv_titulo').value,
                descricao: "Vaga criada pelo painel",
                requisitos: document.getElementById('nv_tags').value
            };

            try {
                await fetch('/api/vagas', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
            } catch (err) {
                console.error("Failed to POST new job:", err);
            }

            formNovaVaga.reset();
            switchTab('section-vagas');
            setTimeout(renderJobs, 500); // Wait for DB to update if successful
        });
    }

    // --- Mock Data: Candidates ---
    const initialMockCandidates = [
        {
            id: 1, nome: "Maria Silva", origem: "WhatsApp", telefone: "(11) 99999-0001", email: "mariasilva@email.com", completude: 95, vaga: "Auxiliar Administrativo", urgente: true, distancia: "3.2 km", tempo: "12 min", score_final: 94, score_tec: 90, score_geo: 100, score_comp: 92, disponibilidade: "Imediato", pretensao: "R$ 1.800", faixa_vaga: "R$ 1.500 - R$ 2.000", fit_salarial: true, etapa: "Entrevista", engajamento: "Rápida"
        },
        {
            id: 2, nome: "João Souza", origem: "WhatsApp", telefone: "(11) 99999-0002", email: "joaosouza@email.com", completude: 80, vaga: "Vigilante Patrimonial", urgente: false, distancia: "7.8 km", tempo: "28 min", score_final: 87, score_tec: 85, score_geo: 90, score_comp: 88, disponibilidade: "15 dias", pretensao: "R$ 2.200", faixa_vaga: "R$ 2.000 - R$ 2.500", fit_salarial: true, etapa: "Triagem", engajamento: "Rápida"
        },
        {
            id: 3, nome: "Ana Ferreira", origem: "Email", telefone: "(11) 99999-0003", email: "anaferreira@email.com", completude: 60, vaga: "Recepcionista", urgente: false, distancia: "11.2 km", tempo: "35 min", score_final: 55, score_tec: 70, score_geo: 40, score_comp: 80, disponibilidade: "30 dias", pretensao: "R$ 3.500", faixa_vaga: "R$ 2.000 - R$ 2.500", fit_salarial: false, etapa: "Triagem", engajamento: "Lenta"
        },
        {
            id: 4, nome: "Carlos Lima", origem: "Upload", telefone: "(11) 99999-0004", email: "carloslima@email.com", completude: 100, vaga: "Assistente Financeiro", urgente: false, distancia: "5.1 km", tempo: "18 min", score_final: 78, score_tec: 82, score_geo: 75, score_comp: 70, disponibilidade: "15 dias", pretensao: "R$ 2.800", faixa_vaga: "R$ 2.500 - R$ 3.000", fit_salarial: true, etapa: "Proposta", engajamento: "Rápida"
        }
    ];

    const favorites = new Set();
    window.toggleFavorite = function (id) {
        if (favorites.has(id)) favorites.delete(id);
        else favorites.add(id);
        renderCandidatos();
    };

    // Filters
    const filterInputs = ['Search', 'Score', 'Etapa', 'Fonte', 'Disp'].map(id => document.getElementById(`filter${id}`));
    filterInputs.forEach(input => {
        if (input) input.addEventListener('input', renderCandidatos);
    });

    const candidatosGrid = document.getElementById('candidatosGrid');

    function renderCandidatos() {
        if (!candidatosGrid) return;
        const candidates = JSON.parse(localStorage.getItem('rh_candidates_tw')) || initialMockCandidates;

        const qSearch = (filterInputs[0]?.value || "").toLowerCase();
        const qScore = filterInputs[1]?.value || "Todos";
        const qEtapa = filterInputs[2]?.value || "Todos";
        const qFonte = filterInputs[3]?.value || "Todos";
        const qDisp = filterInputs[4]?.value || "Todos";

        const filtered = candidates.filter(c => {
            const matchSearch = c.nome.toLowerCase().includes(qSearch) || c.vaga.toLowerCase().includes(qSearch);
            let matchScore = true;
            if (qScore === "Alto") matchScore = c.score_final >= 80;
            if (qScore === "Médio") matchScore = c.score_final >= 60 && c.score_final < 80;
            if (qScore === "Baixo") matchScore = c.score_final < 60;

            const matchEtapa = qEtapa === "Todos" || c.etapa === qEtapa;
            const matchFonte = qFonte === "Todos" || c.origem === qFonte;
            const matchDisp = qDisp === "Todos" || c.disponibilidade === qDisp;

            return matchSearch && matchScore && matchEtapa && matchFonte && matchDisp;
        });

        candidatosGrid.innerHTML = '';
        if (filtered.length === 0) {
            candidatosGrid.innerHTML = `<tr><td colspan="10" class="text-center py-12 text-gray-500">Nenhum candidato encontrado.</td></tr>`;
            return;
        }

        filtered.forEach(c => {
            // Badges
            let origemColor = 'bg-purple-100 text-purple-700';
            if (c.origem === 'WhatsApp') origemColor = 'bg-emerald-100 text-emerald-700';
            if (c.origem === 'Email') origemColor = 'bg-blue-100 text-blue-700';

            let scoreColor = 'bg-emerald-100 text-emerald-700';
            if (c.score_final < 60) scoreColor = 'bg-red-100 text-red-600';
            else if (c.score_final < 80) scoreColor = 'bg-amber-100 text-amber-700';

            const steps = { "Triagem": 1, "Entrevista": 2, "Proposta": 3, "Contratado": 4 };
            const currStep = steps[c.etapa] || 1;

            let etapaBadge = 'bg-gray-100 text-gray-600';
            let activeColor = 'bg-gray-400';
            if (c.etapa === 'Entrevista') { etapaBadge = 'bg-blue-100 text-blue-700'; activeColor = 'bg-blue-500'; }
            if (c.etapa === 'Proposta') { etapaBadge = 'bg-purple-100 text-purple-700'; activeColor = 'bg-purple-500'; }
            if (c.etapa === 'Contratado') { etapaBadge = 'bg-emerald-100 text-emerald-700'; activeColor = 'bg-emerald-500'; }

            let funnelDots = '';
            for (let i = 1; i <= 4; i++) {
                funnelDots += `<div class="w-1.5 h-1.5 rounded-full ${i <= currStep ? activeColor : 'bg-gray-200'}"></div>`;
            }

            let dispBadge = 'bg-gray-100 text-gray-700';
            if (c.disponibilidade === 'Imediato') dispBadge = 'bg-emerald-100 text-emerald-700';
            if (c.disponibilidade === '15 dias') dispBadge = 'bg-amber-100 text-amber-700';

            const isFav = favorites.has(c.id);

            candidatosGrid.innerHTML += `
                <tr class="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                    <td class="px-4 py-3 align-top">
                        <div class="font-bold text-gray-900 flex items-center gap-2">
                            ${c.nome} 
                            <span class="${origemColor} px-2 py-0.5 rounded-lg text-[10px] font-semibold">${c.origem}</span>
                        </div>
                        <div class="text-xs text-gray-500 flex flex-col gap-1 mt-1.5 flex flex-col gap-1 mt-1.5">
                            <span class="flex items-center gap-1.5"><i data-lucide="phone" class="w-3 h-3"></i> ${c.telefone}</span>
                            <span class="flex items-center gap-1.5"><i data-lucide="mail" class="w-3 h-3"></i> ${c.email}</span>
                        </div>
                        <div class="text-[10px] text-gray-400 mt-1 font-medium">Perfil ${c.completude}% completo</div>
                    </td>
                    
                    <td class="px-4 py-3 font-semibold text-gray-700 align-top">
                        <div class="mb-1.5">${c.vaga}</div>
                        ${c.urgente ? `<div class="inline-flex items-center gap-1 bg-red-100 text-red-600 px-2 py-0.5 rounded-lg text-[10px] font-bold uppercase tracking-wider animate-pulse"><i data-lucide="zap" class="w-2.5 h-2.5 fill-current"></i> Urgente</div>` : ''}
                    </td>
                    
                    <td class="px-5 py-4 text-xs text-gray-600 align-top">
                        <div class="flex items-center gap-1.5 mb-1.5"><i data-lucide="map-pin" class="w-3.5 h-3.5 text-gray-400"></i> ${c.distancia}</div>
                        <div class="flex items-center gap-1.5"><i data-lucide="clock" class="w-3 h-3 text-gray-400"></i> ~${c.tempo}</div>
                    </td>
                    
                    <td class="px-5 py-4 align-top">
                        <div class="${scoreColor} w-10 h-10 rounded-xl flex items-center justify-center font-bold text-base shadow-sm">${c.score_final}%</div>
                    </td>
                    
                    <td class="px-5 py-4 align-top w-32">
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-[10px] text-gray-500 w-6">Téc</span>
                            <div class="h-1.5 flex-1 bg-gray-100 rounded-full overflow-hidden"><div class="h-full bg-blue-500 rounded-full" style="width:${c.score_tec}%"></div></div>
                            <span class="text-[10px] font-semibold w-5 text-right">${c.score_tec}</span>
                        </div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="text-[10px] text-gray-500 w-6">Geo</span>
                            <div class="h-1.5 flex-1 bg-gray-100 rounded-full overflow-hidden"><div class="h-full bg-purple-500 rounded-full" style="width:${c.score_geo}%"></div></div>
                            <span class="text-[10px] font-semibold w-5 text-right">${c.score_geo}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-[10px] text-gray-500 w-6">Cmp</span>
                            <div class="h-1.5 flex-1 bg-gray-100 rounded-full overflow-hidden"><div class="h-full bg-orange-500 rounded-full" style="width:${c.score_comp}%"></div></div>
                            <span class="text-[10px] font-semibold w-5 text-right">${c.score_comp}</span>
                        </div>
                    </td>
                    
                    <td class="px-5 py-4 align-top">
                        <span class="${dispBadge} inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold">
                            <i data-lucide="calendar" class="w-3 h-3"></i> ${c.disponibilidade}
                        </span>
                    </td>
                    
                    <td class="px-5 py-4 align-top">
                        <div class="tooltip-wrap inline-flex items-center gap-1.5 font-bold text-gray-900">
                            ${c.pretensao}
                            ${c.fit_salarial ? '<i data-lucide="check" class="w-4 h-4 text-emerald-500"></i>' : '<i data-lucide="x" class="w-4 h-4 text-red-500"></i>'}
                            <div class="tooltip-text">Faixa: ${c.faixa_vaga}</div>
                        </div>
                    </td>
                    
                    <td class="px-5 py-4 align-top">
                        <span class="${etapaBadge} px-2 py-0.5 rounded-lg font-bold text-[10px] uppercase tracking-wider">${c.etapa}</span>
                        <div class="flex gap-1 mt-1.5">${funnelDots}</div>
                    </td>
                    
                    <td class="px-5 py-4 align-top">
                        <div class="flex items-center gap-1 text-xs font-bold ${c.engajamento === 'Rápida' ? 'text-emerald-600' : 'text-red-600'}">
                            <i data-lucide="zap" class="w-3.5 h-3.5 fill-current"></i> Resposta ${c.engajamento.toLowerCase()}
                        </div>
                    </td>
                    
                    <td class="px-5 py-4 align-top text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button onclick="window.toggleFavorite(${c.id})" class="p-1.5 rounded-lg hover:bg-gray-100 ${isFav ? 'text-amber-400' : 'text-gray-400'} transition-colors">
                                <i data-lucide="star" class="w-4 h-4 ${isFav ? 'fill-current' : ''}"></i>
                            </button>
                            <button onclick="window.openDrawer(${c.id})" class="bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-3 py-1.5 rounded-xl text-xs font-bold transition-colors shadow-sm">
                                Ver Perfil
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        if (window.lucide) window.lucide.createIcons();
    }
    renderCandidatos();

    // --- Drawer Control ---
    const drawerOverlay = document.getElementById('drawerOverlay');
    const drawerPanel = document.getElementById('drawerPanel');
    const closeDrawerBtn = document.getElementById('closeDrawerBtn');
    const drawerContentBody = document.getElementById('drawerContentBody');

    function closeDrawer() {
        drawerOverlay.classList.remove('animate-fadeIn');
        drawerOverlay.style.opacity = '0';
        drawerPanel.classList.remove('open');
        setTimeout(() => {
            drawerOverlay.classList.add('hidden');
            drawerOverlay.style.opacity = '1';
        }, 300);
    }

    if (closeDrawerBtn) closeDrawerBtn.addEventListener('click', closeDrawer);
    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', (e) => {
            if (e.target === drawerOverlay) closeDrawer();
        });
    }

    window.openDrawer = function (id) {
        const candidates = JSON.parse(localStorage.getItem('rh_candidates_tw')) || initialMockCandidates;
        const c = candidates.find(cand => cand.id === id);
        if (!c) return;

        drawerContentBody.innerHTML = `
            <div class="flex items-center gap-4 mb-8">
                <div class="w-16 h-16 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center shrink-0">
                    <i data-lucide="user" class="w-8 h-8 text-gray-400"></i>
                </div>
                <div>
                    <h3 class="text-2xl font-bold tracking-tight text-gray-900">${c.nome}</h3>
                    <div class="flex items-center gap-2 mt-1">
                        <span class="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-lg text-[10px] font-bold uppercase tracking-wider">${c.origem}</span>
                        <span class="text-xs text-gray-500 font-medium tracking-tight">Aplicou para ${c.vaga}</span>
                    </div>
                </div>
            </div>

            <div class="bg-gray-50 border border-gray-100 rounded-2xl p-6 flex justify-between items-center mb-8 shadow-sm">
                <div>
                    <div class="text-sm font-bold text-gray-700">Lead Score Geral</div>
                    <div class="text-xs text-gray-400 font-medium">Recomendação da IA</div>
                </div>
                <div class="text-4xl font-black ${c.score_final >= 80 ? 'text-emerald-600' : c.score_final >= 60 ? 'text-amber-600' : 'text-red-600'}">
                    ${c.score_final}%
                </div>
            </div>

            <div class="mb-8">
                <h4 class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-4">Análise Detalhada (IA)</h4>
                <div class="flex flex-col gap-3">
                    <div class="flex items-center gap-3"><span class="w-20 text-xs font-semibold text-gray-600">Técnico</span><div class="flex-1 h-2 bg-gray-100 rounded-full"><div class="h-full bg-blue-500 rounded-full" style="width:${c.score_tec}%"></div></div><span class="text-xs font-bold w-6 text-right">${c.score_tec}</span></div>
                    <div class="flex items-center gap-3"><span class="w-20 text-xs font-semibold text-gray-600">Geográfico</span><div class="flex-1 h-2 bg-gray-100 rounded-full"><div class="h-full bg-purple-500 rounded-full" style="width:${c.score_geo}%"></div></div><span class="text-xs font-bold w-6 text-right">${c.score_geo}</span></div>
                    <div class="flex items-center gap-3"><span class="w-20 text-xs font-semibold text-gray-600">Comport.</span><div class="flex-1 h-2 bg-gray-100 rounded-full"><div class="h-full bg-orange-500 rounded-full" style="width:${c.score_comp}%"></div></div><span class="text-xs font-bold w-6 text-right">${c.score_comp}</span></div>
                    
                    <div class="flex items-center gap-3 mt-2"><span class="w-20 text-xs font-semibold text-gray-600">Engajamento</span><div class="flex-1 h-2 bg-gray-100 rounded-full"><div class="h-full ${c.engajamento === 'Rápida' ? 'bg-emerald-500' : 'bg-red-500'} rounded-full" style="width:${c.engajamento === 'Rápida' ? '95%' : '40%'}"></div></div></div>
                    <div class="flex items-center gap-3"><span class="w-20 text-xs font-semibold text-gray-600">Fit Salarial</span><div class="flex-1 h-2 bg-gray-100 rounded-full"><div class="h-full ${c.fit_salarial ? 'bg-emerald-500' : 'bg-red-500'} rounded-full" style="width:${c.fit_salarial ? '100%' : '30%'}"></div></div></div>
                </div>
            </div>

            <hr class="border-gray-100 mb-6">

            <div class="flex flex-col gap-6">
                <div>
                    <h4 class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Contato</h4>
                    <div class="border border-gray-100 rounded-xl p-4 bg-white shadow-sm flex flex-col gap-2 text-sm font-medium text-gray-700">
                        <div class="flex items-center gap-3"><i data-lucide="phone" class="w-4 h-4 text-gray-400"></i> ${c.telefone}</div>
                        <div class="flex items-center gap-3"><i data-lucide="mail" class="w-4 h-4 text-gray-400"></i> ${c.email}</div>
                    </div>
                </div>
                
                <div>
                    <h4 class="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">Pretensão Salarial</h4>
                    <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 flex justify-between items-center">
                        <div>
                            <span class="block text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-0.5">Pretensão</span>
                            <strong class="text-lg ${c.fit_salarial ? 'text-emerald-700' : 'text-red-700'}">${c.pretensao}</strong>
                        </div>
                        <div class="text-gray-300 text-xl font-light">/</div>
                        <div class="text-right">
                            <span class="block text-[10px] font-semibold text-gray-500 uppercase tracking-wide mb-0.5">Faixa da Vaga</span>
                            <strong class="text-lg text-gray-800">${c.faixa_vaga}</strong>
                        </div>
                    </div>
                </div>
            </div>
        `;
        if (window.lucide) window.lucide.createIcons();
        drawerOverlay.classList.remove('hidden');
        drawerPanel.classList.add('open');
    };
});
