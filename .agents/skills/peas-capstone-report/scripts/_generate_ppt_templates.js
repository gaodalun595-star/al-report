#!/usr/bin/env node
/** One-off generator for assets/ppt-styles/{style}/*.html — run from skill root. */
const fs = require('fs');
const path = require('path');

const SKILL_ROOT = path.join(__dirname, '..');
const STYLES = {
  'classic-blue': { name: '經典藍', primary: '#1C2833', accent: '#2E4053', bg: '#F4F6F6', highlight: '#2E4053' },
  'teal-coral': { name: '青綠珊瑚', primary: '#277884', accent: '#5EA8A7', bg: '#F4F6F6', highlight: '#FE4447' },
  'sage-terracotta': { name: '鼠尾草赤陶', primary: '#87A96B', accent: '#E07A5F', bg: '#F4F1DE', highlight: '#E07A5F' },
};

function baseCss(t) {
  return `
html { background: #ffffff; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: ${t.bg}; display: flex; flex-direction: column;
  font-family: Arial, Helvetica, sans-serif; box-sizing: border-box;
  overflow: hidden;
}
.bar { background: ${t.primary}; height: 10pt; width: 100%; flex-shrink: 0; }
.accent { color: ${t.highlight}; }
h1 { color: ${t.primary}; font-size: 32pt; margin: 0 0 12pt 0; }
h2 { color: ${t.primary}; font-size: 26pt; margin: 0 0 10pt 0; }
p { color: ${t.accent}; font-size: 16pt; margin: 4pt 0; }
ul { color: ${t.accent}; font-size: 16pt; margin: 0; padding-left: 20pt; }
li { margin-bottom: 6pt; }
img { object-fit: contain; }
`;
}

function wrap(title, css, body) {
  return `<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>${css}</style></head>
<body>${body}</body></html>`;
}

function cover(t) {
  const css = baseCss(t) + `
.content { flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 32pt 48pt; }
.title { font-size: 38pt; text-align: center; color: ${t.primary}; margin: 0 0 20pt 0; }
.meta p { text-align: center; font-size: 18pt; }
`;
  return wrap('cover', css, `
<div class="bar"></div>
<div class="content">
  <h1 class="title">{{TITLE}}</h1>
  <div class="meta">{{META_HTML}}</div>
</div>`);
}

function bullets(t) {
  const css = baseCss(t) + `
.pad { padding: 28pt 40pt 32pt 40pt; flex: 1; display: flex; flex-direction: column; }
`;
  return wrap('bullets', css, `
<div class="bar"></div>
<div class="pad">
  <h2>{{HEADING}}</h2>
  {{BULLETS_HTML}}
</div>`);
}

function imageFull(t) {
  const css = baseCss(t) + `
.pad { padding: 20pt 32pt 24pt 32pt; flex: 1; display: flex; flex-direction: column; }
.img-wrap { flex: 1; display: flex; align-items: center; justify-content: center; }
.img-wrap img { max-width: 640pt; max-height: 280pt; }
.caption p { font-size: 14pt; text-align: center; margin-top: 8pt; }
`;
  return wrap('image-full', css, `
<div class="bar"></div>
<div class="pad">
  <h2>{{HEADING}}</h2>
  <div class="img-wrap"><img src="{{IMAGE_PATH}}" alt=""></div>
  <div class="caption">{{CAPTION_HTML}}</div>
</div>`);
}

function imageCaption(t) {
  const css = baseCss(t) + `
.pad { padding: 20pt 28pt 24pt 28pt; flex: 1; display: flex; flex-direction: column; }
.row { flex: 1; display: flex; flex-direction: row; gap: 16pt; align-items: flex-start; }
.col-img { width: 340pt; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.col-img img { max-width: 340pt; max-height: 260pt; }
.col-text { flex: 1; }
`;
  return wrap('image-caption', css, `
<div class="bar"></div>
<div class="pad">
  <h2>{{HEADING}}</h2>
  <div class="row">
    <div class="col-img"><img src="{{IMAGE_PATH}}" alt=""></div>
    <div class="col-text">{{BULLETS_HTML}}</div>
  </div>
</div>`);
}

function demo(t) {
  const css = baseCss(t) + `
.pad { padding: 20pt 32pt 24pt 32pt; flex: 1; display: flex; flex-direction: column; }
.img-wrap { flex: 1; display: flex; align-items: center; justify-content: center; }
.img-wrap img { max-width: 620pt; max-height: 300pt; }
`;
  return wrap('demo', css, `
<div class="bar"></div>
<div class="pad">
  <h2>{{HEADING}}</h2>
  <div class="img-wrap"><img src="{{IMAGE_PATH}}" alt=""></div>
</div>`);
}

const types = { 'cover.html': cover, 'bullets.html': bullets, 'image-full.html': imageFull, 'image-caption.html': imageCaption, 'demo.html': demo };

for (const [id, theme] of Object.entries(STYLES)) {
  const dir = path.join(SKILL_ROOT, 'assets', 'ppt-styles', id);
  fs.mkdirSync(dir, { recursive: true });
  for (const [file, fn] of Object.entries(types)) {
    fs.writeFileSync(path.join(dir, file), fn(theme), 'utf8');
  }
}
console.log('OK: ppt-styles templates generated');
