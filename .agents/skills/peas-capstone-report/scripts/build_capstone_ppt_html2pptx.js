#!/usr/bin/env node
/**
 * Build report/專題報告.pptx from MD + ppt-style.json via html2pptx (pptx skill).
 *
 * Usage (student project root):
 *   node "<skill>/scripts/build_capstone_ppt_html2pptx.js" --report-dir report --skill-root "<skill>"
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const os = require('os');

const VALID_STYLES = new Set(['classic-blue', 'teal-coral', 'sage-terracotta']);
const MAX_BULLETS = 6;
const MAX_BULLET_LEN = 80;

function parseArgs(argv) {
  const args = { reportDir: 'report', skillRoot: null, projectRoot: process.cwd() };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--report-dir' && argv[i + 1]) args.reportDir = argv[++i];
    else if (argv[i] === '--skill-root' && argv[i + 1]) args.skillRoot = path.resolve(argv[++i]);
    else if (argv[i] === '--project-root' && argv[i + 1]) args.projectRoot = path.resolve(argv[++i]);
  }
  if (!args.skillRoot) {
    args.skillRoot = path.join(__dirname, '..');
  }
  args.reportPath = path.join(args.projectRoot, args.reportDir);
  return args;
}

function setupGlobalModules() {
  try {
    const globalRoot = execSync('npm root -g', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
    if (globalRoot && !module.paths.includes(globalRoot)) {
      module.paths.unshift(globalRoot);
    }
  } catch {
    /* ignore */
  }
}

function resolvePptxSkillRoot(projectRoot) {
  const home = os.homedir();
  const candidates = [
    path.join(projectRoot, '.agents', 'skills', 'pptx'),
    path.join(home, '.agents', 'skills', 'pptx'),
    path.join(projectRoot, '.cursor', 'skills', 'pptx'),
    path.join(home, '.cursor', 'skills', 'pptx'),
  ];
  for (const c of candidates) {
    if (fs.existsSync(path.join(c, 'scripts', 'html2pptx.js'))) return c;
  }
  return null;
}

function readStyleJson(reportPath) {
  const p = path.join(reportPath, 'ppt-style.json');
  if (!fs.existsSync(p)) throw new Error(`Missing ${p}`);
  const data = JSON.parse(fs.readFileSync(p, 'utf8'));
  if (!VALID_STYLES.has(data.style)) {
    throw new Error(`Invalid style "${data.style}"; must be one of: ${[...VALID_STYLES].join(', ')}`);
  }
  return data.style;
}

function truncate(text, max = MAX_BULLET_LEN) {
  const t = String(text).trim();
  return t.length <= max ? t : `${t.slice(0, max - 1)}…`;
}

function bulletsToHtml(items) {
  const list = items.slice(0, MAX_BULLETS).map((b) => `<li>${escapeHtml(truncate(b))}</li>`);
  return list.length ? `<ul>${list.join('')}</ul>` : '<ul><li>（無條列）</li></ul>';
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function parseMd(mdText) {
  const lines = mdText.split(/\r?\n/);
  let title = '專題報告';
  const meta = [];
  const sections = [];
  let current = null;
  let inAppendix = false;

  function flush() {
    if (current) sections.push({ ...current });
    current = null;
  }

  for (const line of lines) {
    if (line.startsWith('# ') && sections.length === 0 && !current) {
      title = line.slice(2).trim();
      continue;
    }
    if (/^\*\*組別/.test(line) || /^\*\*日期/.test(line)) {
      meta.push(line.replace(/^\*\*|\*\*$/g, '').trim());
      continue;
    }
    const hm = line.match(/^(#{1,3})\s+(.+)$/);
    if (hm) {
      flush();
      const level = hm[1].length;
      const heading = hm[2].trim();
      if (level === 2 && heading.includes('附錄')) {
        inAppendix = true;
        current = { heading, level, bullets: [], images: [], demos: [] };
        continue;
      }
      if (inAppendix && level === 3) {
        if (!current.demos) current.demos = [];
        current.demos.push({ name: heading, bullets: [], images: [] });
        continue;
      }
      inAppendix = level === 2 && heading.includes('附錄');
      current = { heading, level, bullets: [], images: [], demos: [] };
      continue;
    }
    const img = line.match(/!\[[^\]]*\]\(([^)]+)\)/);
    if (img) {
      const rel = img[1].trim();
      if (inAppendix && current?.demos?.length) {
        current.demos[current.demos.length - 1].images.push(rel);
      } else if (current) {
        current.images.push(rel);
      }
      continue;
    }
    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet && current) {
      if (inAppendix && current.demos?.length) {
        current.demos[current.demos.length - 1].bullets.push(bullet[1].trim());
      } else {
        current.bullets.push(bullet[1].trim());
      }
      continue;
    }
    if (line.trim() && current && !line.startsWith('---') && !line.startsWith('![')) {
      if (!inAppendix || !current.demos?.length) {
        current.bullets.push(line.trim());
      }
    }
  }
  flush();

  function findSection(pred) {
    return sections.find(pred);
  }

  const intro = findSection((s) => /^1\.\s/.test(s.heading) || s.heading.includes('專題介紹'));
  const server = findSection((s) => s.heading.includes('Server') || s.heading.includes('server') || /^2\./.test(s.heading));
  const overview = findSection((s) => s.heading.includes('系統概覽') || /^3\./.test(s.heading));
  const results = sections.find((s) => s.heading.includes('4.1') || s.heading.includes('成果'));
  const innovation = sections.find((s) => s.heading.includes('4.2') || s.heading.includes('創新'));
  const tech = findSection((s) => /^5\./.test(s.heading) || s.heading.includes('技術'));
  const appendix = sections.find((s) => s.heading.includes('附錄'));

  return { title, meta, intro, server, overview, results, innovation, tech, appendix };
}

function metaToHtml(meta) {
  return meta.map((m) => `<p>${escapeHtml(m)}</p>`).join('\n') || '<p>Agent Studio 專題報告</p>';
}

function resolveImage(reportPath, rel) {
  const p = path.resolve(reportPath, rel);
  if (!fs.existsSync(p)) throw new Error(`Image not found: ${p}`);
  return p.replace(/\\/g, '/');
}

function fillTemplate(template, vars) {
  let out = template;
  for (const [k, v] of Object.entries(vars)) {
    out = out.split(`{{${k}}}`).join(v);
  }
  return out;
}

function loadTemplate(skillRoot, style, name) {
  const p = path.join(skillRoot, 'assets', 'ppt-styles', style, name);
  if (!fs.existsSync(p)) throw new Error(`Template missing: ${p}`);
  return fs.readFileSync(p, 'utf8');
}

function buildSlidePlan(data, reportPath) {
  const slides = [];
  slides.push({ type: 'cover.html', vars: { TITLE: escapeHtml(data.title), META_HTML: metaToHtml(data.meta) } });
  slides.push({
    type: 'bullets.html',
    vars: { HEADING: '專題介紹', BULLETS_HTML: bulletsToHtml(data.intro?.bullets || []) },
  });

  const serverImg = data.server?.images[0] || 'assets/server-topology.png';
  const serverCaption = (data.server?.bullets || []).slice(0, 2);
  slides.push({
    type: 'image-full.html',
    vars: {
      HEADING: '學校 Server 環境',
      IMAGE_PATH: resolveImage(reportPath, serverImg),
      CAPTION_HTML: serverCaption.length
        ? serverCaption.map((b) => `<p>${escapeHtml(truncate(b, 120))}</p>`).join('')
        : '<p></p>',
    },
  });

  const archImg = data.overview?.images[0] || 'assets/project-architecture.png';
  slides.push({
    type: 'image-caption.html',
    vars: {
      HEADING: '系統概覽',
      IMAGE_PATH: resolveImage(reportPath, archImg),
      BULLETS_HTML: bulletsToHtml((data.overview?.bullets || []).slice(0, 4)),
    },
  });

  slides.push({
    type: 'bullets.html',
    vars: { HEADING: '成果', BULLETS_HTML: bulletsToHtml(data.results?.bullets || []) },
  });
  slides.push({
    type: 'bullets.html',
    vars: { HEADING: '創新／亮點', BULLETS_HTML: bulletsToHtml(data.innovation?.bullets || []) },
  });
  slides.push({
    type: 'bullets.html',
    vars: { HEADING: '技術含量', BULLETS_HTML: bulletsToHtml(data.tech?.bullets || []) },
  });

  const demos = data.appendix?.demos || [];
  if (demos.length) {
    for (const d of demos) {
      const img = d.images[0];
      if (!img) continue;
      slides.push({
        type: 'demo.html',
        vars: {
          HEADING: d.name,
          IMAGE_PATH: resolveImage(reportPath, img),
        },
      });
    }
  } else {
    const assetsDir = path.join(reportPath, 'assets');
    if (fs.existsSync(assetsDir)) {
      const demoFiles = fs.readdirSync(assetsDir).filter((f) => /^demo-\d+\.png$/i.test(f)).sort();
      demoFiles.forEach((f, i) => {
        slides.push({
          type: 'demo.html',
          vars: {
            HEADING: `Demo ${i + 1}`,
            IMAGE_PATH: resolveImage(reportPath, path.join('assets', f)),
          },
        });
      });
    }
  }

  return slides;
}

async function main() {
  const args = parseArgs(process.argv);
  setupGlobalModules();

  const mdPath = path.join(args.reportPath, '專題報告.md');
  if (!fs.existsSync(mdPath)) {
    console.error(`ERROR: Missing ${mdPath}`);
    process.exit(1);
  }

  const style = readStyleJson(args.reportPath);
  const pptxSkillRoot = resolvePptxSkillRoot(args.projectRoot);
  if (!pptxSkillRoot) {
    console.error('ERROR: pptx skill not found (.agents/skills/pptx). Run companion preflight.');
    process.exit(1);
  }

  let PptxGenJS;
  let html2pptx;
  try {
    PptxGenJS = require('pptxgenjs');
    html2pptx = require(path.join(pptxSkillRoot, 'scripts', 'html2pptx.js'));
  } catch (e) {
    console.error(`ERROR: html2pptx deps missing: ${e.message}`);
    console.error('Install: npm install -g pptxgenjs playwright sharp');
    process.exit(1);
  }

  const mdData = parseMd(fs.readFileSync(mdPath, 'utf8'));
  const slidePlan = buildSlidePlan(mdData, args.reportPath);

  const tmpDir = path.join(args.reportPath, '.ppt-build-tmp');
  fs.mkdirSync(tmpDir, { recursive: true });

  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_16x9';
  pptx.author = 'peas-capstone-report';

  for (let i = 0; i < slidePlan.length; i++) {
    const spec = slidePlan[i];
    const tpl = loadTemplate(args.skillRoot, style, spec.type);
    const html = fillTemplate(tpl, spec.vars);
    const htmlPath = path.join(tmpDir, `slide-${String(i + 1).padStart(2, '0')}.html`);
    fs.writeFileSync(htmlPath, html, 'utf8');
    try {
      await html2pptx(htmlPath, pptx);
    } catch (err) {
      console.error(`ERROR on slide ${i + 1} (${spec.type}): ${err.message}`);
      process.exit(1);
    }
  }

  const outPath = path.join(args.reportPath, '專題報告.pptx');
  await pptx.writeFile({ fileName: outPath });
  console.log(`OK: ${outPath} (${slidePlan.length} slides, style=${style})`);
}

main().catch((err) => {
  console.error(`ERROR: ${err.message}`);
  process.exit(1);
});
