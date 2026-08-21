import { useEffect, useState } from 'react';
import VoyaraLogo from './VoyaraLogo';

export default function VoyaraIntro({ children }) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const timer = window.setTimeout(() => setVisible(false), reducedMotion ? 700 : 2800);
    return () => window.clearTimeout(timer);
  }, []);

  return <div className="homepage-shell">{visible && <section className="voyara-intro" aria-label="Voyara introduction"><div className="intro-mark"><VoyaraLogo compact /><strong className="intro-wordmark">VOYARA</strong><span className="intro-tagline">Discover. Compare. Wander.</span></div></section>}<div className={`homepage-content ${visible ? 'homepage-content-hidden' : ''}`}>{children}</div></div>;
}
