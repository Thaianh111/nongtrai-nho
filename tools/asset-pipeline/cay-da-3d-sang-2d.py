"""Render cây đa thành sprite kiểu hoạt hình cho Nông Trại Nhỏ, 4 mùa.
python3 stylize.py full.glb outdir"""
import sys, os, struct, json, io
import numpy as np
from PIL import Image, ImageFilter

path, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
b = open(path, 'rb').read()
L = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + L]); bin0 = 20 + L + 8
def acc(i):
    a = j['accessors'][i]; dt = {5126: np.float32, 5125: np.uint32}[a['componentType']]
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3}[a['type']]
    bv = j['bufferViews'][a['bufferView']]; o = bin0 + bv.get('byteOffset', 0)
    r = np.frombuffer(b, dt, a['count'] * n, o)
    return r.reshape(-1, n) if n > 1 else r
pr = j['meshes'][0]['primitives'][0]
P = acc(pr['attributes']['POSITION']).astype(float); UV = acc(pr['attributes']['TEXCOORD_0']); I = acc(pr['indices']).reshape(-1, 3)
ti = j['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']
bv = j['bufferViews'][j['images'][j['textures'][ti]['source']]['bufferView']]
tex = np.array(Image.open(io.BytesIO(b[bin0 + bv.get('byteOffset', 0):][:bv['byteLength']])).convert('RGB')).astype(float)
th, tw = tex.shape[:2]

p0, p1, p2 = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]
cen = (p0 + p1 + p2) / 3
h = (cen[:, 1] - P[:, 1].min()) / np.ptp(P[:, 1])
r = np.hypot(cen[:, 0], cen[:, 2])
# bỏ ụ đất: phần rất thấp và xa thân
keep = ~((h < 0.11) & (r > 0.15))
nrm = np.cross(p1 - p0, p2 - p0); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
uvc = (UV[I[:, 0]] + UV[I[:, 1]] + UV[I[:, 2]]) / 3
c = tex[np.clip(((1 - uvc[:, 1]) * (th - 1)).astype(int), 0, th - 1), np.clip((uvc[:, 0] * (tw - 1)).astype(int), 0, tw - 1)]
# phân loại lá / thân theo màu gốc: lá xanh hơn đỏ
greenish = c[:, 1] > c[:, 0] * 0.98
leaf = (h > 0.5) | ((h > 0.4) & greenish & (r > 0.12))
leaf &= ~((r < 0.07) & (h < 0.62))

light = np.array([-0.55, 0.75, 0.5]); light /= np.linalg.norm(light)
lam = np.abs(nrm @ light)

SEASONS = {
    'xuan': [(46, 110, 58), (70, 150, 66), (112, 188, 78), (164, 216, 98), (214, 238, 140)],
    'ha':   [(32, 88, 52), (48, 122, 60), (78, 160, 70), (122, 192, 84), (170, 218, 110)],
    'thu':  [(126, 58, 30), (178, 92, 36), (220, 138, 48), (240, 182, 70), (252, 222, 128)],
    'dong': [(96, 110, 92), (128, 140, 118), (166, 176, 152), (206, 214, 196), (238, 242, 236)],
}
BARK = [(92, 62, 42), (124, 88, 60), (158, 118, 80), (190, 152, 108)]
OUTLINE = (59, 42, 32)

def render(elev, azim, size, leafpal, leaf_keep=1.0):
    a, e = np.radians(azim), np.radians(elev)
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    V = P @ Ry.T @ Rx.T
    m = keep.copy()
    if leaf_keep < 1:  # mùa đông: rụng bớt lá
        rnd = (np.sin(cen[:, 0] * 91.7 + cen[:, 2] * 53.3 + cen[:, 1] * 17.1) * 43758.5) % 1
        m &= ~(leaf & (np.abs(rnd) > leaf_keep))
    idx = np.where(m)[0]
    vv = V[np.unique(I[idx].ravel())]
    mn, mx = vv[:, :2].min(0), vv[:, :2].max(0); sc = size * 0.95 / (mx - mn).max()
    X = (V[:, 0] - (mn[0] + mx[0]) / 2) * sc + size / 2
    Y = size * 0.975 - (V[:, 1] - mn[1]) * sc
    Z = V[:, 2]
    tri = I[idx]
    zc = Z[tri].mean(1)
    # tô màu: lá theo bảng mùa, thân theo bảng vỏ; bậc sáng theo ánh sáng + độ cao + mặt hướng camera
    zn = (zc - zc.min()) / np.ptp(zc)
    t = np.clip(0.12 + 0.45 * lam[idx] + 0.35 * h[idx] + 0.35 * (zn - 0.5), 0, 0.999)
    lp = np.array(leafpal); bp = np.array(BARK)
    col = np.where(leaf[idx][:, None], lp[(t * len(lp)).astype(int)], bp[(np.clip(t * 1.1, 0, .999) * len(bp)).astype(int)])
    img = np.zeros((size * size, 3)); zb = np.full(size * size, -1e9); al = np.zeros(size * size, bool)
    for wa, wb, wc in ((1/3, 1/3, 1/3), (1, 0, 0), (0, 1, 0), (0, 0, 1), (.5, .5, 0), (0, .5, .5), (.5, 0, .5)):
        px = X[tri[:, 0]] * wa + X[tri[:, 1]] * wb + X[tri[:, 2]] * wc
        py = Y[tri[:, 0]] * wa + Y[tri[:, 1]] * wb + Y[tri[:, 2]] * wc
        ix = np.clip(px.astype(int), 0, size - 1); iy = np.clip(py.astype(int), 0, size - 1)
        o = np.argsort(zc); lin = iy[o] * size + ix[o]
        u, last = np.unique(lin[::-1], return_index=True); sel = o[::-1][last]
        better = zc[sel] > zb[u]
        img[u[better]] = col[sel[better]]; zb[u[better]] = zc[sel[better]]; al[u[better]] = True
    A = np.zeros((size, size, 4), np.uint8); A[..., :3] = img.reshape(size, size, 3); A[..., 3] = al.reshape(size, size) * 255
    im = Image.fromarray(A)
    # lấp lỗ li ti rồi làm khối mềm kiểu tranh vẽ
    Af = np.array(im.filter(ImageFilter.MaxFilter(3))); msk = A[..., 3] > 0; Af[msk] = A[msk]
    im = Image.fromarray(Af).filter(ImageFilter.ModeFilter(7))
    return im

def finish(im, out_w):
    im = im.resize((out_w, out_w), Image.LANCZOS)
    A = np.array(im); A[..., 3] = np.where(A[..., 3] > 128, 255, 0)
    m = A[..., 3] > 0; ring = np.zeros_like(m)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if dy * dy + dx * dx <= 4: ring |= np.roll(np.roll(m, dy, 0), dx, 1)
    ring &= ~m; A[ring] = (*OUTLINE, 255)
    return Image.fromarray(A)

for name, pal in SEASONS.items():
    im = render(24, 30, 900, pal, leaf_keep=0.35 if name == 'dong' else 1.0)
    sp = finish(im, 384); sp = sp.crop(sp.getbbox()); sp.save(os.path.join(outdir, f'cay-da-{name}.png'), optimize=True)
    print('ok', name)
