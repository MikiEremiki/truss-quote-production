// IFC Viewer (client-side, three.js + web-ifc-three, загружается лениво с CDN)

const THREE_URL = 'https://esm.sh/three@0.152.2';
const IFC_LOADER_SRC = 'https://unpkg.com/web-ifc-three@0.0.126/IFCLoader.js';
const WEB_IFC_URL = 'https://unpkg.com/web-ifc@0.0.36/web-ifc-api.js';
const BVH_UTILS_URL = 'https://esm.sh/three@0.152.2/examples/jsm/utils/BufferGeometryUtils.js';
const WASM_PATH = 'https://unpkg.com/web-ifc@0.0.36/';

// esm.sh подставляет полифил process, из-за чего web-ifc считает, что запущен в Node ("Dynamic require of fs").
// Поэтому IFCLoader берём «сырым» с unpkg и подменяем импорты на браузерные модули.
async function loadIfcLoader() {
  let src = await (await fetch(IFC_LOADER_SRC)).text();
  src = src
    .replace(/from\s*'web-ifc'/g, `from '${WEB_IFC_URL}'`)
    .replace(/from\s*'three'/g, `from '${THREE_URL}'`)
    .replace(/from\s*'three\/examples\/jsm\/utils\/BufferGeometryUtils'/g, `from '${BVH_UTILS_URL}'`);
  const blobUrl = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
  try {
    return await import(blobUrl);
  } finally {
    URL.revokeObjectURL(blobUrl);
  }
}

let ctx = null;

function setStatus(text, isError = false) {
  const el = document.getElementById('ifc-status');
  if (!el) return;
  el.innerText = text;
  el.className = 'text-xs ' + (isError ? 'text-red-600' : 'text-slate-500');
}

async function initViewer() {
  if (ctx) return ctx;
  const container = document.getElementById('ifc-canvas-container');
  const THREE = await import(THREE_URL);
  const { IFCLoader } = await loadIfcLoader();

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf1f5f9);
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 10000);
  camera.position.set(15, 12, 15);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.7));
  const dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(20, 30, 10);
  scene.add(dir);
  scene.add(new THREE.GridHelper(50, 50, 0x94a3b8, 0xcbd5e1));

  // Простое орбитальное управление: ЛКМ — вращение, колесо — масштаб, ПКМ — сдвиг
  const target = new THREE.Vector3();
  const sph = new THREE.Spherical().setFromVector3(camera.position.clone().sub(target));
  let mode = null, lx = 0, ly = 0;
  const update = () => {
    camera.position.setFromSpherical(sph).add(target);
    camera.lookAt(target);
  };
  const dom = renderer.domElement;
  dom.addEventListener('contextmenu', e => e.preventDefault());
  dom.addEventListener('pointerdown', e => { mode = e.button === 0 ? 'rot' : 'pan'; lx = e.clientX; ly = e.clientY; dom.setPointerCapture(e.pointerId); });
  dom.addEventListener('pointerup', () => { mode = null; });
  dom.addEventListener('pointermove', e => {
    if (!mode) return;
    const dx = e.clientX - lx, dy = e.clientY - ly;
    lx = e.clientX; ly = e.clientY;
    if (mode === 'rot') {
      sph.theta -= dx * 0.008;
      sph.phi = Math.min(Math.PI - 0.01, Math.max(0.01, sph.phi - dy * 0.008));
    } else {
      const k = sph.radius * 0.0015;
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 0);
      const up = new THREE.Vector3().setFromMatrixColumn(camera.matrix, 1);
      target.addScaledVector(right, -dx * k).addScaledVector(up, dy * k);
    }
    update();
  });
  dom.addEventListener('wheel', e => {
    e.preventDefault();
    sph.radius = Math.max(0.5, sph.radius * (e.deltaY > 0 ? 1.1 : 0.9));
    update();
  }, { passive: false });

  const resize = () => {
    const w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  };
  window.addEventListener('resize', resize);
  resize();

  const loader = new IFCLoader();
  await loader.ifcManager.setWasmPath(WASM_PATH);

  (function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  })();

  ctx = { THREE, scene, camera, loader, sph, target, update, resize, model: null };
  return ctx;
}

export async function handleIfcUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;
  const wrap = document.getElementById('ifc-viewer-wrap');
  if (wrap) wrap.classList.remove('hidden');
  setStatus(`Загрузка ${file.name}...`);
  try {
    const c = await initViewer();
    c.resize();
    if (c.model) {
      c.scene.remove(c.model);
      c.model.geometry?.dispose?.();
      c.model = null;
    }
    const url = URL.createObjectURL(file);
    c.loader.load(url, model => {
      URL.revokeObjectURL(url);
      c.model = model;
      c.scene.add(model);
      const box = new c.THREE.Box3().setFromObject(model);
      const center = box.getCenter(new c.THREE.Vector3());
      const size = box.getSize(new c.THREE.Vector3());
      c.target.copy(center);
      c.sph.radius = Math.max(size.x, size.y, size.z) * 1.8 || 20;
      c.sph.theta = Math.PI / 4;
      c.sph.phi = Math.PI / 3;
      c.update();
      setStatus(`${file.name} — модель загружена`);
    }, undefined, err => {
      setStatus('Ошибка чтения IFC: ' + (err && err.message ? err.message : err), true);
    });
  } catch (e) {
    setStatus('Не удалось инициализировать просмотрщик (нужен доступ к CDN): ' + e.message, true);
  }
  event.target.value = '';
}
