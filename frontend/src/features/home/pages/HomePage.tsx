import { Link } from 'react-router-dom';
import { Card } from '@/shared/components/Card';
import { DisclaimerBanner } from '@/shared/components/DisclaimerBanner';

const techGroups: { title: string; items: string[] }[] = [
  {
    title: 'Backend',
    items: [
      'Python 3.11',
      'FastAPI',
      'SQLAlchemy (async)',
      'PostgreSQL',
      'Alembic',
      'Pydantic',
    ],
  },
  {
    title: 'AI / ML',
    items: [
      'PyTorch',
      'torchxrayvision',
      'OpenCV',
      'Pillow',
      'NumPy',
      'Pandas',
      'scikit-learn',
    ],
  },
  {
    title: 'Async & messaging',
    items: ['Celery', 'RabbitMQ'],
  },
  {
    title: 'Frontend',
    items: [
      'React 18',
      'TypeScript',
      'Vite',
      'React Query',
      'Zustand',
      'React Router',
      'TailwindCSS',
      'Recharts',
    ],
  },
  {
    title: 'Architecture & services',
    items: [
      'Clean Architecture',
      'Hexagonal (Ports & Adapters)',
      'Light DDD',
      'Async worker service',
      'REST API',
      'Feature-sliced frontend',
    ],
  },
  {
    title: 'Testing',
    items: ['Pytest', 'Vitest', 'Testing Library', 'Playwright'],
  },
  {
    title: 'DevOps & CI/CD',
    items: [
      'Docker',
      'Docker Compose',
      'GitHub Actions',
      'Makefile',
      'Nginx',
      'AWS-ready',
    ],
  },
];

const steps = [
  { n: 1, title: 'Upload', text: 'Send a chest X-ray image (JPG/PNG).' },
  { n: 2, title: 'Async analysis', text: 'A Celery worker runs the AI pipeline.' },
  { n: 3, title: 'Result', text: 'See class, confidence and a plain explanation.' },
];

export function HomePage() {
  return (
    <div className="space-y-10">
      <section className="grid gap-8 md:grid-cols-2 md:items-center">
        <div className="space-y-5">
          <span className="inline-flex rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
            HealthTech · Computer Vision · Clean Architecture
          </span>
          <h1 className="text-4xl font-bold leading-tight text-slate-900">
            AI-assisted chest X-ray analysis,{' '}
            <span className="text-brand-600">built like production software</span>.
          </h1>
          <p className="text-lg text-slate-600">
            HealthVision AI demonstrates an end-to-end HealthTech pipeline: image
            upload, asynchronous AI inference, persistence, dashboards and a
            clean, modular codebase — front to back.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/upload"
              className="rounded-lg bg-brand-600 px-5 py-2.5 font-medium text-white shadow-sm hover:bg-brand-700"
            >
              Upload an exam →
            </Link>
            <Link
              to="/dashboard"
              className="rounded-lg border border-slate-300 bg-white px-5 py-2.5 font-medium text-slate-700 hover:bg-slate-50"
            >
              View dashboard
            </Link>
          </div>
        </div>
        <Card className="p-6">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
            How it works
          </h2>
          <ol className="space-y-4">
            {steps.map((s) => (
              <li key={s.n} className="flex gap-3">
                <span className="grid h-7 w-7 flex-none place-items-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
                  {s.n}
                </span>
                <div>
                  <p className="font-medium text-slate-800">{s.title}</p>
                  <p className="text-sm text-slate-500">{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </Card>
      </section>

      <DisclaimerBanner />

      <section>
        <h2 className="mb-1 text-lg font-semibold text-slate-900">Technology stack</h2>
        <p className="mb-5 text-sm text-slate-500">
          Architecture, services, AI, frontend, testing and CI/CD — the full
          engineering surface of the project.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {techGroups.map((group) => (
            <Card key={group.title} className="p-4">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand-700">
                {group.title}
              </h3>
              <div className="flex flex-wrap gap-2">
                {group.items.map((t) => (
                  <span
                    key={t}
                    className="rounded-md border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
