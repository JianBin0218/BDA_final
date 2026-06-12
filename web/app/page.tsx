"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import {
  AreaChart,
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Activity, ArrowUpRight, Database, Layers3, MapPin, Radar, Search, Sparkles, WalletCards } from "lucide-react";
import initialPayload from "../public/data/skillscope-taiwan.json";

type Job = {
  job_id: string;
  title: string;
  company: string;
  city: string | null;
  district: string | null;
  location: string | null;
  experience: string | null;
  seniority: string | null;
  job_type: string | null;
  salary_monthly_min: number | null;
  salary_monthly_max: number | null;
  source_platform: string;
  source_url: string;
  source_updated_at: string | null;
  skills: string[];
  career_cluster: string;
  career_cluster_zh: string;
};

type FacetOption = {
  value: string;
  label: string;
};

type Payload = {
  generated_at: string;
  summary: {
    job_count: number;
    city_count: number;
    source_count: number;
    salary_count: number;
    latest_source_update: string | null;
  };
  facets: {
    sources: string[];
    cities: string[];
    clusters: FacetOption[];
    skills: string[];
  };
  cluster_labels: Record<string, string>;
  jobs: Job[];
};

type TabKey = "overview" | "skills" | "salary" | "report" | "jobs";

const COLORS = ["#2DD4BF", "#60A5FA", "#FBBF24", "#FB7185", "#A78BFA", "#34D399", "#F97316"];

const TAB_LABELS: Record<TabKey, string> = {
  overview: "市場總覽",
  skills: "技能需求",
  salary: "薪資與地區",
  report: "技能缺口報告",
  jobs: "職缺明細"
};

const STATIC_PAYLOAD = initialPayload as Payload;

export default function Home() {
  const [payload, setPayload] = useState<Payload>(STATIC_PAYLOAD);
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [sources, setSources] = useState<string[]>(() => STATIC_PAYLOAD.facets.sources);
  const [clusters, setClusters] = useState<string[]>(() => STATIC_PAYLOAD.facets.clusters.map((cluster) => cluster.value));
  const [city, setCity] = useState("全部城市");
  const [skill, setSkill] = useState("全部技能");
  const [minSalary, setMinSalary] = useState(0);
  const [targetCluster, setTargetCluster] = useState(STATIC_PAYLOAD.facets.clusters[0]?.value ?? "");
  const [selectedSkillToAdd, setSelectedSkillToAdd] = useState(STATIC_PAYLOAD.facets.skills[0] ?? "");
  const [currentSkills, setCurrentSkills] = useState<string[]>([]);

  useEffect(() => {
    fetch("/data/skillscope-taiwan.json")
      .then((response) => response.json())
      .then((data: Payload) => {
        setPayload(data);
        setSources(data.facets.sources);
        setClusters(data.facets.clusters.map((cluster) => cluster.value));
        setTargetCluster(data.facets.clusters[0]?.value ?? "");
        setSelectedSkillToAdd(data.facets.skills[0] ?? "");
      })
      .catch(() => {
        setPayload(STATIC_PAYLOAD);
      });
  }, []);

  const filteredJobs = useMemo(() => {
    return payload.jobs.filter((job) => {
      const salaryMax = job.salary_monthly_max ?? job.salary_monthly_min ?? 0;
      return (
        sources.includes(job.source_platform) &&
        clusters.includes(job.career_cluster) &&
        (city === "全部城市" || job.city === city) &&
        (skill === "全部技能" || job.skills.includes(skill)) &&
        salaryMax >= minSalary
      );
    });
  }, [payload, sources, clusters, city, skill, minSalary]);

  const summary = useMemo(() => summarize(filteredJobs, payload), [filteredJobs, payload]);

  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">
            <Radar size={16} />
            SkillScope Taiwan Radar
          </div>
          <h1>台灣 CS 職缺市場總覽</h1>
          <p>
            以台灣就業通、Cake 與 Meet.jobs 的職缺資料為基礎，整理出台灣科技職涯分布、技能需求、薪資輪廓與個人技能缺口。
          </p>
          <div className="hero-meta">
            <span>最近資料更新：{summary.latestSourceUpdate ?? "未知"}</span>
            <span>前端資料產生：{formatDate(payload.generated_at)}</span>
          </div>
        </div>
        <div className="radar-card" aria-label="資料來源摘要">
          <div className="radar-ring" />
          <div className="radar-number">{summary.jobCount.toLocaleString()}</div>
          <div className="radar-label">目前篩選職缺</div>
        </div>
      </section>

      <section className="dashboard-grid">
        <aside className="filters">
          <div className="filter-heading">
            <Search size={16} />
            <span>篩選條件</span>
          </div>
          <FilterGroup title="資料來源" values={payload.facets.sources} selected={sources} onChange={setSources} />
          <FilterGroup
            title="職涯群集"
            values={payload.facets.clusters.map((clusterOption) => clusterOption.value)}
            selected={clusters}
            onChange={setClusters}
            labelFor={(value) => payload.cluster_labels[value] ?? value}
          />
          <label className="field">
            <span>城市</span>
            <select value={city} onChange={(event) => setCity(event.target.value)}>
              <option>全部城市</option>
              {payload.facets.cities.map((facetCity) => (
                <option key={facetCity}>{facetCity}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>技能</span>
            <select value={skill} onChange={(event) => setSkill(event.target.value)}>
              <option>全部技能</option>
              {payload.facets.skills.map((facetSkill) => (
                <option key={facetSkill}>{facetSkill}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>最低可比月薪</span>
            <input
              type="range"
              min="0"
              max="200000"
              step="5000"
              value={minSalary}
              onChange={(event) => setMinSalary(Number(event.target.value))}
            />
            <strong className="mono">NT$ {minSalary.toLocaleString()}</strong>
          </label>
          <p className="filter-note">正式 demo 採 Next.js 靜態 JSON；Python 管線仍負責資料擷取、清理與輸出。</p>
        </aside>

        <section className="content">
          <div className="metric-grid">
            <Metric icon={<Database size={18} />} label="台灣 IT/CS 職缺" value={summary.jobCount.toLocaleString()} />
            <Metric icon={<MapPin size={18} />} label="涵蓋城市" value={summary.cityCount.toLocaleString()} />
            <Metric icon={<WalletCards size={18} />} label="可解析薪資" value={summary.salaryCount.toLocaleString()} />
            <Metric icon={<Layers3 size={18} />} label="資料來源" value={summary.sourceCount.toLocaleString()} />
          </div>

          <nav className="tabs" aria-label="dashboard tabs">
            {(Object.keys(TAB_LABELS) as TabKey[]).map((tab) => (
              <button key={tab} className={activeTab === tab ? "active" : ""} onClick={() => setActiveTab(tab)}>
                {TAB_LABELS[tab]}
              </button>
            ))}
          </nav>

          {activeTab === "overview" && <Overview jobs={filteredJobs} />}
          {activeTab === "skills" && <SkillsPanel jobs={filteredJobs} />}
          {activeTab === "salary" && <SalaryPanel jobs={filteredJobs} />}
          {activeTab === "report" && (
            <SkillGapPanel
              jobs={filteredJobs}
              skills={payload.facets.skills}
              clusters={payload.facets.clusters}
              labels={payload.cluster_labels}
              targetCluster={targetCluster}
              setTargetCluster={setTargetCluster}
              selectedSkillToAdd={selectedSkillToAdd}
              setSelectedSkillToAdd={setSelectedSkillToAdd}
              currentSkills={currentSkills}
              setCurrentSkills={setCurrentSkills}
            />
          )}
          {activeTab === "jobs" && <JobsTable jobs={filteredJobs} />}
        </section>
      </section>
    </main>
  );
}

function FilterGroup({
  title,
  values,
  selected,
  onChange,
  labelFor = (value) => value
}: {
  title: string;
  values: string[];
  selected: string[];
  onChange: (next: string[]) => void;
  labelFor?: (value: string) => string;
}) {
  function toggle(value: string) {
    if (selected.includes(value)) {
      onChange(selected.filter((item) => item !== value));
    } else {
      onChange([...selected, value]);
    }
  }

  return (
    <div className="filter-group">
      <div className="filter-title">{title}</div>
      <div className="check-list">
        {values.map((value) => (
          <label key={value} className="check-item">
            <input type="checkbox" checked={selected.includes(value)} onChange={() => toggle(value)} />
            <span>{labelFor(value)}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div>
        <div className="metric-label">{label}</div>
        <div className="metric-value mono">{value}</div>
      </div>
    </div>
  );
}

function Overview({ jobs }: { jobs: Job[] }) {
  const clusterData = countBy(jobs, (job) => job.career_cluster_zh).slice(0, 10);
  const sourceData = countBy(jobs, (job) => job.source_platform);

  return (
    <div className="panel-grid two">
      <ChartCard title="職涯群集分布" subtitle="看台灣科技職缺集中在哪些方向">
        <ResponsiveContainer width="100%" height={330}>
          <BarChart data={clusterData} layout="vertical" margin={{ left: 16, right: 20 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" horizontal={false} />
            <XAxis type="number" stroke="#8A93A3" />
            <YAxis dataKey="name" type="category" stroke="#CBD5E1" width={112} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="value" radius={[0, 7, 7, 0]} fill="#2DD4BF" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="資料來源占比">
        <ResponsiveContainer width="100%" height={330}>
          <PieChart>
            <Pie data={sourceData} dataKey="value" nameKey="name" innerRadius={78} outerRadius={112} paddingAngle={4}>
              {sourceData.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function SkillsPanel({ jobs }: { jobs: Job[] }) {
  const skillData = countSkills(jobs).slice(0, 18);
  const clusterSkills = topClusterSkills(jobs);

  return (
    <div className="panel-grid two">
      <ChartCard title="熱門技能排行" subtitle="技能名稱保留市場常用英文，方便對照履歷">
        <ResponsiveContainer width="100%" height={380}>
          <BarChart data={skillData} layout="vertical" margin={{ left: 12, right: 20 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" horizontal={false} />
            <XAxis type="number" stroke="#8A93A3" />
            <YAxis dataKey="name" type="category" stroke="#CBD5E1" width={96} />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="value" radius={[0, 7, 7, 0]} fill="#60A5FA" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <div className="card">
        <div className="card-head">
          <h2>各職涯群集 Top Skills</h2>
          <p>快速看不同方向的技能差異。</p>
        </div>
        <div className="cluster-skill-list">
          {clusterSkills.map((cluster) => (
            <div className="cluster-row" key={cluster.cluster}>
              <div className="cluster-name">{cluster.cluster}</div>
              <div className="chip-wrap">
                {cluster.skills.map((clusterSkill) => (
                  <span className="chip" key={`${cluster.cluster}-${clusterSkill}`}>
                    {clusterSkill}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SalaryPanel({ jobs }: { jobs: Job[] }) {
  const cityData = countBy(
    jobs.filter((job) => job.city),
    (job) => job.city ?? "未標示"
  ).slice(0, 12);
  const salaryData = salaryHistogram(jobs);

  return (
    <div className="panel-grid two">
      <ChartCard title="城市分布" subtitle="主要城市與科學園區周邊職缺密度">
        <ResponsiveContainer width="100%" height={330}>
          <BarChart data={cityData}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis dataKey="name" stroke="#8A93A3" />
            <YAxis stroke="#8A93A3" />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="value" radius={[7, 7, 0, 0]} fill="#2DD4BF" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="可比月薪分布" subtitle="年薪除以 12，時薪以 8 小時與 22 個工作天估算">
        <ResponsiveContainer width="100%" height={330}>
          <AreaChart data={salaryData}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis dataKey="name" stroke="#8A93A3" />
            <YAxis stroke="#8A93A3" />
            <Tooltip content={<ChartTooltip />} />
            <Area type="monotone" dataKey="value" stroke="#FBBF24" fill="rgba(251,191,36,0.22)" />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function SkillGapPanel({
  jobs,
  skills,
  clusters,
  labels,
  targetCluster,
  setTargetCluster,
  selectedSkillToAdd,
  setSelectedSkillToAdd,
  currentSkills,
  setCurrentSkills
}: {
  jobs: Job[];
  skills: string[];
  clusters: FacetOption[];
  labels: Record<string, string>;
  targetCluster: string;
  setTargetCluster: (value: string) => void;
  selectedSkillToAdd: string;
  setSelectedSkillToAdd: (value: string) => void;
  currentSkills: string[];
  setCurrentSkills: (skills: string[]) => void;
}) {
  const targetJobs = jobs.filter((job) => job.career_cluster === targetCluster);
  const required = countSkills(targetJobs).slice(0, 12).map((item) => item.name);
  const matched = currentSkills.filter((skillName) => required.includes(skillName));
  const missing = required.filter((skillName) => !currentSkills.includes(skillName));
  const fitScore = Math.round((matched.length / Math.max(required.length, 1)) * 100);
  const alternativeFit = clusters
    .map((cluster) => {
      const clusterRequired = new Set(countSkills(jobs.filter((job) => job.career_cluster === cluster.value)).map((item) => item.name));
      const score = Math.round((currentSkills.filter((skillName) => clusterRequired.has(skillName)).length / Math.max(clusterRequired.size, 1)) * 100);
      return { name: cluster.label, value: score };
    })
    .sort((a, b) => b.value - a.value)
    .slice(0, 5);

  function addSkill() {
    if (selectedSkillToAdd && !currentSkills.includes(selectedSkillToAdd)) {
      setCurrentSkills([...currentSkills, selectedSkillToAdd]);
    }
  }

  return (
    <div className="report-layout">
      <div className="card">
        <div className="card-head">
          <h2>個人技能缺口報告</h2>
          <p>以目前篩選後的台灣職缺資料計算，不是通用模板建議。</p>
        </div>
        <div className="report-controls">
          <label className="field">
            <span>目標職涯方向</span>
            <select value={targetCluster} onChange={(event) => setTargetCluster(event.target.value)}>
              {clusters.map((cluster) => (
                <option key={cluster.value} value={cluster.value}>
                  {labels[cluster.value] ?? cluster.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>加入目前技能</span>
            <div className="inline-control">
              <select value={selectedSkillToAdd} onChange={(event) => setSelectedSkillToAdd(event.target.value)}>
                {skills.map((skillName) => (
                  <option key={skillName}>{skillName}</option>
                ))}
              </select>
              <button onClick={addSkill}>加入</button>
            </div>
          </label>
        </div>
        <div className="score-row">
          <Metric icon={<Sparkles size={18} />} label="適配分數" value={`${fitScore}%`} />
          <Metric icon={<Activity size={18} />} label="已對上技能" value={matched.length.toString()} />
          <Metric icon={<Layers3 size={18} />} label="優先補強" value={missing.length.toString()} />
        </div>
        <ChipSection title="已具備技能" items={currentSkills} onRemove={(item) => setCurrentSkills(currentSkills.filter((skillName) => skillName !== item))} />
        <ChipSection title="符合市場需求" items={matched} />
        <ChipSection title="建議優先補強" items={missing.slice(0, 8)} variant="warn" />
      </div>
      <ChartCard title="相近職涯方向" subtitle="依你目前技能與各群集技能需求的交集估算">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={alternativeFit}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
            <XAxis dataKey="name" stroke="#8A93A3" />
            <YAxis stroke="#8A93A3" />
            <Tooltip content={<ChartTooltip />} />
            <Bar dataKey="value" radius={[7, 7, 0, 0]} fill="#FB7185" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function ChipSection({
  title,
  items,
  variant = "default",
  onRemove
}: {
  title: string;
  items: string[];
  variant?: "default" | "warn";
  onRemove?: (item: string) => void;
}) {
  return (
    <div className="chip-section">
      <h3>{title}</h3>
      <div className="chip-wrap">
        {items.length === 0 ? (
          <span className="muted">尚無資料</span>
        ) : (
          items.map((item) => (
            <button key={item} className={`chip ${variant === "warn" ? "warn" : ""}`} onClick={() => onRemove?.(item)}>
              {item}
            </button>
          ))
        )}
      </div>
    </div>
  );
}

function JobsTable({ jobs }: { jobs: Job[] }) {
  return (
    <div className="card">
      <div className="card-head">
        <h2>職缺明細</h2>
        <p>顯示目前篩選條件下前 120 筆職缺。</p>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>職缺名稱</th>
              <th>公司</th>
              <th>城市</th>
              <th>職涯群集</th>
              <th>可比月薪</th>
              <th>技能</th>
              <th>來源</th>
            </tr>
          </thead>
          <tbody>
            {jobs.slice(0, 120).map((job) => (
              <tr key={job.job_id}>
                <td>
                  <div className="job-title">{job.title}</div>
                  <div className="job-sub">{job.experience || job.seniority || "資歷未標示"}</div>
                </td>
                <td>{job.company || "未標示"}</td>
                <td>{job.city || "未標示"}</td>
                <td>{job.career_cluster_zh}</td>
                <td className="mono">{formatSalary(job.salary_monthly_min, job.salary_monthly_max)}</td>
                <td>
                  <div className="mini-chips">
                    {job.skills.slice(0, 3).map((skillName) => (
                      <span key={`${job.job_id}-${skillName}`}>{skillName}</span>
                    ))}
                  </div>
                </td>
                <td>
                  <a href={job.source_url} target="_blank" rel="noreferrer">
                    {job.source_platform}
                    <ArrowUpRight size={12} />
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="card chart-card">
      <div className="card-head">
        <h2>{title}</h2>
        {subtitle ? <p>{subtitle}</p> : null}
      </div>
      {children}
    </div>
  );
}

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number; name?: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="tooltip">
      <div>{label ?? payload[0].name}</div>
      <strong>{payload[0].value.toLocaleString()}</strong>
    </div>
  );
}

function summarize(jobs: Job[], payload: Payload | null) {
  const latest = jobs
    .map((job) => job.source_updated_at)
    .filter(Boolean)
    .sort()
    .at(-1);
  return {
    jobCount: jobs.length,
    cityCount: new Set(jobs.map((job) => job.city).filter(Boolean)).size,
    sourceCount: new Set(jobs.map((job) => job.source_platform)).size,
    salaryCount: jobs.filter((job) => job.salary_monthly_min !== null).length,
    latestSourceUpdate: latest ? formatDate(latest) : (payload?.summary.latest_source_update ?? null)
  };
}

function countBy(jobs: Job[], getter: (job: Job) => string) {
  const map = new Map<string, number>();
  jobs.forEach((job) => {
    const key = getter(job) || "未標示";
    map.set(key, (map.get(key) ?? 0) + 1);
  });
  return Array.from(map, ([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

function countSkills(jobs: Job[]) {
  const map = new Map<string, number>();
  jobs.forEach((job) => {
    job.skills.forEach((skillName) => map.set(skillName, (map.get(skillName) ?? 0) + 1));
  });
  return Array.from(map, ([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
}

function topClusterSkills(jobs: Job[]) {
  const clusters = new Map<string, Job[]>();
  jobs.forEach((job) => {
    const cluster = job.career_cluster_zh;
    clusters.set(cluster, [...(clusters.get(cluster) ?? []), job]);
  });
  return Array.from(clusters, ([cluster, clusterJobs]) => ({
    cluster,
    skills: countSkills(clusterJobs)
      .slice(0, 5)
      .map((item) => item.name)
  }))
    .filter((item) => item.skills.length)
    .slice(0, 8);
}

function salaryHistogram(jobs: Job[]) {
  const bins = [
    { name: "<40k", min: 0, max: 40000, value: 0 },
    { name: "40-60k", min: 40000, max: 60000, value: 0 },
    { name: "60-80k", min: 60000, max: 80000, value: 0 },
    { name: "80-100k", min: 80000, max: 100000, value: 0 },
    { name: "100-140k", min: 100000, max: 140000, value: 0 },
    { name: "140k+", min: 140000, max: Number.POSITIVE_INFINITY, value: 0 }
  ];
  jobs.forEach((job) => {
    const salary = midpoint(job.salary_monthly_min, job.salary_monthly_max);
    if (salary === null) return;
    const bin = bins.find((candidate) => salary >= candidate.min && salary < candidate.max);
    if (bin) bin.value += 1;
  });
  return bins;
}

function midpoint(min: number | null, max: number | null) {
  if (min !== null && max !== null) return (min + max) / 2;
  if (min !== null) return min;
  if (max !== null) return max;
  return null;
}

function formatSalary(min: number | null, max: number | null) {
  if (min === null && max === null) return "未揭露";
  if (min !== null && max !== null) return `NT$${Math.round(min).toLocaleString()}-${Math.round(max).toLocaleString()}`;
  if (min !== null) return `NT$${Math.round(min).toLocaleString()}+`;
  return `最高 NT$${Math.round(max ?? 0).toLocaleString()}`;
}

function formatDate(value: string) {
  return value.slice(0, 10);
}
