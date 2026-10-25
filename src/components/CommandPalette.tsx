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
      className="palette m-auto mt-[10vh] w-[min(calc(100vw-2rem),36rem)] overflow-hidden rounded-2xl bg-paper p-0 text-ink backdrop:bg-[#0b0f1c]/70 backdrop:backdrop-blur-[2px]"
    >
      <div className="p-3">
        <label className="flex items-center gap-3 rounded-xl bg-ink/[0.06] px-4 py-3 ring-1 ring-ink/10 transition-shadow focus-within:ring-ink/20">
          <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" className="shrink-0 opacity-60">
            <circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" strokeWidth="2" />
            <path d="M16 16l4.5 4.5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            role="combobox"
            aria-expanded="true"
            aria-controls={listId}
            aria-activedescendant={results.length ? `${listId}-${active}` : undefined}
            aria-label="Search sections, projects, certificates and links"
            placeholder="Search projects, certificates, sections"
            autoComplete="off"
            spellCheck={false}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            onKeyDown={onKeyDown}
            className="palette__input w-full min-w-0 bg-transparent text-[1.0625rem] leading-6 placeholder:text-ink/45"
          />
        </label>
      </div>
      <ul id={listId} role="listbox" aria-label="Results" className="palette__list max-h-[min(52vh,26rem)] overflow-auto px-2 pb-2">
        {results.map((item, i) => (
          <li
            key={`${item.group}-${item.label}-${item.url}`}
            id={`${listId}-${i}`}
            role="option"
            aria-selected={i === active}
            onMouseMove={() => setActive(i)}
            onClick={() => go(item)}
            className="group flex cursor-pointer items-center gap-4 rounded-[10px] px-3 py-2.5 transition-colors aria-selected:bg-ink/[0.09]"
          >
            {/* Phones stack the group under the title so long certificate names stay readable. */}
            <span className="flex min-w-0 flex-1 flex-col gap-0.5 sm:flex-row sm:items-center sm:gap-4">
              <span className="min-w-0 flex-1 text-[0.975rem] leading-snug [text-wrap:pretty] sm:line-clamp-2">{item.label}</span>
              <span className="label shrink-0 tracking-[0.12em] opacity-55">{item.group}</span>
            </span>
            <svg
              viewBox="0 0 24 24"
              width="16"
              height="16"
              aria-hidden="true"
              className="shrink-0 text-torii opacity-0 transition-opacity group-aria-selected:opacity-100 [@media(pointer:coarse)]:hidden"
            >
              <path d="M19 5v7a3 3 0 0 1-3 3H6m0 0 4-4m-4 4 4 4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </li>
        ))}
      </ul>
      {results.length === 0 && (
        <p role="status" className="px-5 pb-6 pt-3 text-center opacity-70">
          Nothing matches “{query.trim()}”. Try a project or certificate name.
        </p>
      )}
      <div className="flex items-center gap-4 border-t border-rule px-5 py-2.5 text-[0.75rem] opacity-70 [@media(pointer:coarse)]:hidden" aria-hidden="true">
        <span className="flex items-center gap-1.5">
          <kbd className="palette__key">↑</kbd>
          <kbd className="palette__key">↓</kbd> move
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="palette__key">↵</kbd> open
        </span>
        <span className="flex items-center gap-1.5">
          <kbd className="palette__key">esc</kbd> close
        </span>
        <span className="ml-auto font-jp text-[0.8rem]">索引</span>
      </div>
    </dialog>
  );
}
