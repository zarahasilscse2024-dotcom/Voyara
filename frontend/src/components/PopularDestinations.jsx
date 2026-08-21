import { useNavigate } from 'react-router-dom';

const destinations = [
  ['Kerala', 'Backwaters, beaches and lush landscapes.', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=85'],
  ['Kashmir', 'Snowy mountains and breathtaking valleys.', 'https://images.unsplash.com/photo-1598091383021-15ddea10925d?auto=format&fit=crop&w=900&q=85'],
  ['Munnar', 'Misty hills and peaceful tea plantations.', 'https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=900&q=85'],
  ['Manali', 'High trails, pine air and mountain light.', 'https://images.unsplash.com/photo-1518005020951-eccb494ad742?auto=format&fit=crop&w=900&q=85'],
  ['Goa', 'Turquoise water, salt air and quiet coves.', 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=900&q=85'],
  ['Ooty', 'Tea hills, old railways and cool mornings.', 'https://images.unsplash.com/photo-1593693411515-c20261bcad6e?auto=format&fit=crop&w=900&q=85'],
  ['Coorg', 'Coffee estates and rainforest green.', 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=900&q=85'],
  ['Rajasthan', 'Palaces, craft trails and desert skies.', 'https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=900&q=85'],
];

export default function PopularDestinations() { const navigate = useNavigate(); return <section className="section popular-destinations"><div className="section-head"><div><span className="kicker">The places calling</span><h2>Popular right now</h2></div><button className="text-button" onClick={() => navigate('/explore')}>See the full collection ↗</button></div><div className="popular-destination-grid">{destinations.map(([name,description,image]) => <article className="popular-destination-card" key={name} style={{backgroundImage:`linear-gradient(0deg,rgba(15,38,32,.82),rgba(15,38,32,.06) 72%),url(${image})`}}><div><h3>{name}</h3><p>{description}</p><button onClick={() => navigate(`/explore?destination=${encodeURIComponent(name)}`)}>Explore {name} ↗</button></div></article>)}</div></section> }
