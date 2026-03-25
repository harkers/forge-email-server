import { mockActivity, mockSources, mockTasks } from '../../lib/forge-pipeline/mock-data';
import { getFocusScore } from '../../lib/forge-pipeline/derived-state';

export default function ForgePipelinePage() {
  const focus = [...mockTasks].sort((a, b) => getFocusScore(b) - getFocusScore(a))[0];

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-[1600px] px-6 py-6 lg:px-10">
        <header className="rounded-[28px] border border-white/10 bg-slate-900 p-6">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-300/80">Project workspace</p>
          <div className="mt-3 flex items-center gap-3">
            <h1 className="text-4xl font-semibold tracking-tight text-white">Forge Pipeline</h1>
            <span className="rounded-full border border-sky-400/30 bg-sky-400/10 px-3 py-1 text-xs font-medium text-sky-200">v1.0.0</span>
          </div>
          <p className="mt-4 max-w-3xl text-lg text-slate-300">Projects, actions, notes, and momentum in one clean view.</p>
          <div className="mt-5 inline-flex flex-wrap items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-200">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-300" />
            <span>Live</span>
            <span className="text-emerald-100/70">•</span>
            <span>updated 18:16:52</span>
            <span className="text-emerald-100/70">•</span>
            <span>4/4 sources healthy</span>
          </div>
        </header>

        <section className="mt-6 grid grid-cols-2 gap-4 xl:grid-cols-4">
          {[
            { label: 'Projects', value: 13, delta: '+1 this week' },
            { label: 'Active tasks', value: 60, delta: '+4 today' },
            { label: 'At risk', value: 8, delta: '-2 today' },
            { label: 'Completed', value: 15, delta: '+3 today' },
          ].map((item) => (
            <div key={item.label} className="rounded-[28px] border border-white/10 bg-white/[0.06] p-5">
              <div className="text-4xl font-semibold tracking-tight text-sky-200">{item.value}</div>
              <div className="mt-2 text-sm font-medium text-slate-200">{item.label}</div>
              <div className="mt-2 text-xs text-slate-400">{item.delta}</div>
            </div>
          ))}
        </section>

        <section className="mt-6 rounded-[28px] border border-white/10 bg-white/[0.04] p-4">
          <div className="flex flex-wrap gap-3">
            {['2 high-priority tasks due this week', '0 active blockers', '3 stale items need review', 'Most activity: Memory Stack'].map((item) => (
              <span key={item} className="rounded-full border border-slate-700 bg-slate-900/80 px-4 py-2 text-sm text-slate-200">{item}</span>
            ))}
          </div>
        </section>

        <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-[1.15fr_0.85fr_1fr]">
          <div className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5">
            <h2 className="text-2xl font-semibold text-white">Next up</h2>
            <p className="mt-1 text-sm text-slate-400">Highest-priority work</p>
            <div className="mt-5 space-y-4">
              {mockTasks.map((task) => (
                <div key={task.id} className="rounded-[24px] border border-white/10 bg-slate-800/70 p-5">
                  <h3 className="text-xl font-semibold leading-tight text-white">{task.title}</h3>
                  <p className="mt-2 text-sm text-slate-400">{task.sourceRef}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5">
            <h2 className="text-2xl font-semibold text-white">Blocked</h2>
            <p className="mt-1 text-sm text-slate-400">Needs intervention</p>
            <div className="mt-5 flex min-h-[220px] flex-col items-center justify-center rounded-[24px] border border-dashed border-white/10 bg-slate-900/50 p-6 text-center">
              <h3 className="text-lg font-semibold text-white">No active blockers</h3>
              <p className="mt-2 max-w-sm text-sm text-slate-400">All tracked work is currently moving.</p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5">
            <h2 className="text-2xl font-semibold text-white">Recently changed</h2>
            <p className="mt-1 text-sm text-slate-400">Latest activity</p>
            <div className="mt-5 space-y-3">
              {mockActivity.map((item) => (
                <div key={item.id} className="rounded-[22px] border border-white/10 bg-slate-900/80 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="text-base font-semibold text-white">{item.details}</h3>
                      <p className="mt-1 text-sm text-slate-400">{item.source}</p>
                    </div>
                    <span className="shrink-0 text-xs text-slate-500">{item.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          <div className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5">
            <h2 className="text-2xl font-semibold text-white">Focus now</h2>
            <p className="mt-1 text-sm text-slate-400">Top recommended action</p>
            <div className="mt-5 rounded-[24px] border border-sky-400/20 bg-sky-400/5 p-5">
              <h3 className="text-xl font-semibold text-white">{focus?.title}</h3>
              <p className="mt-2 text-sm text-slate-400">{focus?.sourceRef}</p>
            </div>
          </div>

          <div className="rounded-[28px] border border-white/10 bg-white/[0.05] p-5">
            <h2 className="text-2xl font-semibold text-white">Source health</h2>
            <p className="mt-1 text-sm text-slate-400">Freshness and trust</p>
            <div className="mt-5 space-y-3">
              {mockSources.map((source) => (
                <div key={source.id} className="flex items-center justify-between rounded-[22px] border border-white/10 bg-slate-900/80 p-4">
                  <div>
                    <div className="font-medium text-white">{source.name}</div>
                    <div className="mt-1 text-sm text-slate-400">Last sync {source.lastSyncAt}</div>
                  </div>
                  <span className="rounded-full border px-3 py-1 text-xs capitalize">{source.healthState}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
