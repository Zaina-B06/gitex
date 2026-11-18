import React from 'react'

const svg = (d: React.ReactNode) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
    {d}
  </svg>
)

/** One icon per `Action.icon` key from the backend's fixed list (HANDOFF, Part D). Unknown keys fall back to the behaviour icon. */
export const ACTION_ICON: Record<string, React.ReactNode> = {
  walk: svg(
    <>
      <circle cx="13" cy="4" r="2" />
      <path d="M9 20l2-6 3 3v4M7 11l3-3 4 1 2 4" />
    </>,
  ),
  stretch: svg(
    <>
      <circle cx="12" cy="4" r="2" />
      <path d="M4 8l8 2 8-2M12 10v5l-3 6M12 15l3 6" />
    </>,
  ),
  seat: svg(<path d="M7 3v9h9v9M7 12l-1 9M17 8h-6" />),
  balance: svg(
    <>
      <circle cx="12" cy="4" r="2" />
      <path d="M12 6v8l-2 7M12 14h4M5 10h14" />
    </>,
  ),
  moon: svg(<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />),
  sun: svg(
    <>
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M5 19l1.5-1.5M17.5 6.5L19 5" />
    </>,
  ),
  bed: svg(<path d="M3 18V6M3 14h18v4M21 14v-3a3 3 0 0 0-3-3h-7v6M7 11h.01" />),
  water: svg(<path d="M12 3s6 7 6 11a6 6 0 0 1-12 0c0-4 6-11 6-11z" />),
  plate: svg(
    <>
      <circle cx="12" cy="12" r="8" />
      <circle cx="12" cy="12" r="4" />
    </>,
  ),
  fruit: svg(<path d="M12 7c-4-2-8 1-7 6s4 8 7 7c3 1 6-2 7-7s-3-8-7-6zM12 7c0-2 1-4 3-4" />),
  cup: svg(<path d="M4 8h13v5a6 6 0 0 1-6 6h-1a6 6 0 0 1-6-6zM17 10h2a2 2 0 0 1 0 4h-2" />),
  cook: svg(<path d="M4 11h16v3a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6zM2 11h20M9 7c0-1 1-1 1-2s-1-1-1-2M14 7c0-1 1-1 1-2s-1-1-1-2" />),
  basket: svg(<path d="M3 10h18l-2 10H5zM8 10l4-6 4 6" />),
  clock: svg(
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>,
  ),
  no_smoking: svg(
    <>
      <path d="M2 16h12v3H2zM17 16h1.5v3H17zM20 16h1v3h-1" />
      <path d="M3 3l18 18" />
    </>,
  ),
  hand: svg(<path d="M8 13V5a1.5 1.5 0 0 1 3 0v6M11 10V4a1.5 1.5 0 0 1 3 0v6M14 10V5a1.5 1.5 0 0 1 3 0v8a7 7 0 0 1-12 5l-2-3a1.5 1.5 0 0 1 2.5-1.6L8 15" />),
  door: svg(<path d="M5 21V4a1 1 0 0 1 1-1h12v18M3 21h18M14 12h.01" />),
  breath: svg(<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7" />),
  phone_off: svg(
    <>
      <rect x="7" y="2" width="10" height="20" rx="2" />
      <path d="M3 3l18 18" />
    </>,
  ),
  rest: svg(<path d="M4 18h16M6 18c0-4 3-7 6-7s6 3 6 7M12 11V7M9 4h6" />),
  family: svg(
    <>
      <circle cx="8" cy="7" r="2.5" />
      <circle cx="16" cy="7" r="2.5" />
      <circle cx="12" cy="13" r="2" />
      <path d="M3 21c0-3 2-6 5-6M21 21c0-3-2-6-5-6M9 21c0-2 1.5-4 3-4s3 2 3 4" />
    </>,
  ),
}
