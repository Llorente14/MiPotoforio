import Fuse from 'fuse.js';
import { useEffect, useId, useMemo, useRef, useState } from 'react';

export interface PaletteItem {
  label: string;
  group: 'Section' | 'Project' | 'Certificate' | 'Link';
  url: string;
  keywords?: string;
}

declare global {
  interface Window {
    __paletteRequested?: boolean;
  }
}

export default function CommandPalette({ items }: { items: PaletteItem[] }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const returnFocus = useRef<HTMLElement | null>(null);
  const listId = useId();

  const fuse = useMemo(
    () => new Fuse(items, { keys: ['label', 'keywords', 'group'], threshold: 0.4, ignoreLocation: true }),
    [items],
  );
  const results = useMemo(
    () => (query.trim() ? fuse.search(query.trim()).map((r) => r.item) : items),
    [fuse, items, query],
  );

  // The Astro navbar owns the trigger and shortcut so they work before hydration.
  useEffect(() => {
    const show = () => {
      returnFocus.current = (document.activeElement as HTMLElement | null) ?? null;
      setQuery('');
      setActive(0);
      setOpen(true);
    };
    window.addEventListener('palette:open', show);
    if (window.__paletteRequested) {
      window.__paletteRequested = false;
      show();
    }
    return () => window.removeEventListener('palette:open', show);
  }, []);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) {
      dialog.showModal();
      inputRef.current?.focus();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  const close = () => {
    setOpen(false);
    returnFocus.current?.focus();
  };

  const go = (item: PaletteItem | undefined) => {
    if (!item) return;
    setOpen(false);
    window.location.href = item.url;
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActive((i) => Math.min(i + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      go(results[active]);
    }
  };

  useEffect(() => {
    document.getElementById(`${listId}-${active}`)?.scrollIntoView({ block: 'nearest' });
  }, [active, listId]);

  return (
    <dialog
      ref={dialogRef}
      aria-label="Command palette"
      onClose={() => {
        setOpen(false);
        returnFocus.current?.focus();
      }}
      onClick={(e) => {
        if (e.target === dialogRef.current) close();
      }}
      className="m-auto mt-[12vh] w-[min(92vw,36rem)] rounded-xl bg-paper p-0 text-ink shadow-2xl backdrop:bg-black/60"
    >
      <div className="p-3">
        <input
          ref={inputRef}
          type="text"
          role="combobox"
          aria-expanded="true"
          aria-controls={listId}
          aria-activedescendant={results.length ? `${listId}-${active}` : undefined}
          aria-label="Search sections, projects, certificates and links"
          placeholder="Search…"
          autoComplete="off"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setActive(0);
          }}
          onKeyDown={onKeyDown}
          className="w-full rounded-md border border-ink/30 bg-transparent px-3 py-2 text-base"
        />
      </div>
      <ul id={listId} role="listbox" aria-label="Results" className="max-h-[50vh] overflow-auto px-2 pb-2">
        {results.map((item, i) => (
          <li
            key={`${item.group}-${item.label}-${item.url}`}
            id={`${listId}-${i}`}
            role="option"
            aria-selected={i === active}
            onMouseMove={() => setActive(i)}
            onClick={() => go(item)}
            className="flex cursor-pointer items-center justify-between rounded-md px-3 py-2 aria-selected:bg-torii aria-selected:text-paper"
          >
            <span>{item.label}</span>
            <span className="text-sm opacity-70">{item.group}</span>
          </li>
        ))}
      </ul>
      {results.length === 0 && (
        <p role="status" className="px-5 pb-5 text-center">
          No results
        </p>
      )}
    </dialog>
  );
}
