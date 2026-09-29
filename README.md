# Omnipair brand guidelines preview

Live on [brand.omnipair.fi](https://brand.omnipair.fi)

Two reading experiences share the same content and assets: individual topics with shareable query links, and a continuous document with topic anchors. The interface opens in dark mode and remembers the reader's theme choice.

## Development

- `npm install`
- `npm run dev` (port 4173)
- `npm run build` (static output in `dist`)

`app.js`, `style.css` and `index.html` define the interface. `content.json` and `content.css` are extracted from `source/simple-original.html` by `python3 scripts/extract-content.py`. The source snapshot comes from `madebypuru/omnipair-brand-guidelines`, commit `99903b5d0fccc9e9c53303ac26b45a3af4776be1`.

The extraction preserves the Foundation and Verbal Identity writing, removes unfinished chapters and uses only M Saans. Brand assets remain in `public/assets`. Re-running extraction rebuilds the M Saans font download from the supplied variable font.

This project is a separate sample site. It does not change the existing GitHub Pages deployment.
