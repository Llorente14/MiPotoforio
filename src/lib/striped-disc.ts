// Geometry of the site's striped disc, shared by the SVG motif and the CSS mask that cuts video to it.
// A 200 x 200 disc: solid top half, then bands that get thinner and further apart toward the bottom.

export function discBands(bands = 10): { y: number; h: number }[] {
  const rects = [{ y: 0, h: 104 }];
  let y = 108;
  for (let i = 0; i < bands; i++) {
    const t = i / bands;
    const h = 9 * (1 - t) + 1.5;
    rects.push({ y, h });
    y += h + 2.5 + 6 * t;
  }
  return rects;
}

// The disc as an SVG data URL for `mask-image`.
export function discMaskUrl(bands = 10): string {
  const rects = discBands(bands)
    .map((r) => `<rect x='0' y='${r.y.toFixed(2)}' width='200' height='${r.h.toFixed(2)}'/>`)
    .join('');
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 200'><clipPath id='c'><circle cx='100' cy='100' r='100'/></clipPath><g clip-path='url(#c)'>${rects}</g></svg>`;
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}
