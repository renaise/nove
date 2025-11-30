import { useState, useEffect } from 'react';
import { Heart, Sparkles, User, Camera, ArrowRight, Star, Menu, X, Instagram, Facebook, Twitter } from 'lucide-react';

const NoviaLanding = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen font-sans bg-ivory text-[#4A4A4A]">
      {/* Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-500 ${scrolled ? 'bg-white/90 backdrop-blur-md shadow-sm py-3' : 'bg-transparent py-6'}`}>
        <div className="container mx-auto px-6 flex justify-between items-center">
          <span className="text-2xl font-serif italic font-semibold tracking-wide text-gold">Novia</span>
          <div className="hidden md:flex items-center gap-8">
            <a href="#how-it-works" className="hover:text-gold transition-colors">How it Works</a>
            <a href="#stories" className="hover:text-gold transition-colors">Love Stories</a>
            <a href="#partners" className="hover:text-gold transition-colors">Boutiques</a>
            <button className="px-6 py-2 rounded-full font-medium btn-primary">Start Your Joyful Discovery</button>
          </div>
          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-white shadow-lg p-6 flex flex-col gap-4">
            <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)}>How it Works</a>
            <a href="#stories" onClick={() => setMobileMenuOpen(false)}>Love Stories</a>
            <a href="#partners" onClick={() => setMobileMenuOpen(false)}>Boutiques</a>
            <button className="w-full py-3 rounded-full btn-primary">Start Your Joyful Discovery</button>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <header className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img src="https://images.unsplash.com/photo-1515934751635-c81c6bc9a2d8?auto=format&fit=crop&q=80" alt="Happy bride in soft light" className="w-full h-full object-cover opacity-90" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/30 via-transparent to-ivory"></div>
        </div>
        <div className="container mx-auto px-6 relative z-10 text-center mt-20">
          <div className="inline-block px-4 py-1 rounded-full mb-6 glass-card text-sm tracking-widest uppercase">The Effortless Romantic</div>
          <h1 className="text-5xl md:text-7xl font-serif mb-6 text-gray-800 leading-tight">Joyful, Intuitive, <br/> and <span className="italic text-gold">Stress-Free.</span></h1>
          <p className="text-xl md:text-2xl mb-10 max-w-2xl mx-auto text-gray-600 font-light">Welcome, Love. Let's find your perfect match, effortlessly. Blend emotional fulfillment with the magic of AI-powered try-on.</p>
          <div className="flex flex-col md:flex-row gap-4 justify-center items-center">
            <button className="btn-primary px-8 py-4 rounded-full text-lg flex items-center gap-2 group">Start Your Joyful Discovery <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" /></button>
            <button className="px-8 py-4 rounded-full text-lg border border-gold text-gold hover:bg-blush transition-colors">See Our Boutique Partners</button>
          </div>
          <div className="mt-12 flex items-center justify-center gap-2 text-sm text-gray-500">
            <div className="flex">{[1,2,3,4,5].map(i => <Star key={i} size={14} className="fill-gold stroke-gold" />)}</div>
            <span className="font-semibold text-gray-700">47 Dresses Tested. 1 Dream Found.</span>
          </div>
        </div>
      </header>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 relative overflow-hidden bg-ivory">
        <div className="absolute top-0 left-0 w-64 h-64 rounded-full blur-3xl opacity-30 -translate-x-1/2 -translate-y-1/2 bg-rose"></div>
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-serif mb-4">Your Journey to "Yes"</h2>
            <p className="text-lg text-gray-600">Four simple steps to discover your silhouette.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { step: 1, icon: Camera, title: 'Capture Your True Silhouette', img: 'photo-1517841905240-472988babdf9', desc: 'Wear fitted activewear or a simple bodysuit—think of it as a blank canvas for your transformation. Your photos are strictly private.' },
              { step: 2, icon: Sparkles, title: 'The Dream Filter', img: 'photo-1596386461350-326256694e4d', desc: '"Endless Love, Zero Effort." Swipe through thousands of styles, effortlessly. Filter by Fairy-tale, Modern, or Lace.' },
              { step: 3, icon: Heart, title: 'The Moment of Truth', img: 'photo-1606800052052-a08af7148866', desc: '"Is It The One?" See yourself in your dream dress, flawlessly fitted by our AI technology.' },
              { step: 4, icon: User, title: 'The Next Step', img: 'photo-1595777457583-95e059d581b8', desc: '"Ready to Feel the Fabric?" Connect with a stylist or book a fitting at a local boutique instantly.' }
            ].map(({ step, icon: Icon, title, img, desc }, idx) => (
              <div key={step} className={`group relative ${idx % 2 === 1 ? 'mt-12 md:mt-0' : ''}`}>
                <div className="rounded-2xl overflow-hidden aspect-[3/4] mb-6 shadow-lg transition-transform duration-500 group-hover:-translate-y-2">
                  <img src={`https://images.unsplash.com/${img}?auto=format&fit=crop&q=80`} alt={title} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors"></div>
                  <div className="absolute bottom-4 left-4 right-4 glass-card p-4 rounded-xl">
                    <div className="flex items-center gap-2 text-gold mb-1">
                      <Icon size={16} />
                      <span className="text-xs uppercase tracking-wider font-bold">Step {step}</span>
                    </div>
                    <h3 className="font-serif text-lg">{title}</h3>
                  </div>
                </div>
                <p className="text-gray-600 text-sm leading-relaxed px-2">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust & Testimonials */}
      <section id="stories" className="py-24 bg-blush">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="md:w-1/2">
              <div className="relative">
                <div className="absolute -top-4 -left-4 w-20 h-20 text-gold opacity-20">
                  <svg fill="currentColor" viewBox="0 0 32 32"><path d="M10 8c-3.3 0-6 2.7-6 6v10h10V14H6c0-2.2 1.8-4 4-4V8zm16 0c-3.3 0-6 2.7-6 6v10h10V14h-8c0-2.2 1.8-4 4-4V8z"/></svg>
                </div>
                <h2 className="text-3xl md:text-5xl font-serif leading-tight mb-8">"Novia turned my panic into pure joy. I walked into the boutique feeling so confident!"</h2>
                <div className="flex items-center gap-4">
                  <img src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&q=80" alt="Sarah M." className="w-16 h-16 rounded-full object-cover border-2 border-white" />
                  <div>
                    <p className="font-bold text-gray-800">Sarah Jenkins</p>
                    <p className="text-gray-500 text-sm">Married June 2024</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="md:w-1/2 bg-white p-8 md:p-12 rounded-3xl shadow-xl">
              <h3 className="text-xl font-serif mb-6 text-center">Trusted by the Finest Boutiques</h3>
              <div className="grid grid-cols-2 gap-8 opacity-60 grayscale hover:grayscale-0 transition-all">
                <div className="flex items-center justify-center font-serif text-2xl italic">Lumière</div>
                <div className="flex items-center justify-center font-serif text-2xl tracking-widest uppercase">VOWS</div>
                <div className="flex items-center justify-center font-serif text-2xl font-bold">Bella</div>
                <div className="flex items-center justify-center font-serif text-2xl underline">Eternity</div>
              </div>
              <div className="mt-8 pt-8 border-t text-center text-sm text-gray-400">
                <p>Your Moment is Private: Your photos are secure and never shared.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MVP Accessories Preview */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-6 text-center">
          <span className="text-gold text-sm font-bold tracking-widest uppercase mb-2 block">Coming Soon</span>
          <h2 className="text-4xl font-serif mb-12">Complete The Look</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[{ name: 'Veils', icon: '✨' }, { name: 'Tiaras', icon: '👑' }, { name: 'Pendants', icon: '💎' }, { name: 'Earrings', icon: '👂' }].map((item, idx) => (
              <div key={idx} className="p-8 rounded-2xl border border-blush hover:border-gold transition-colors cursor-pointer group">
                <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">{item.icon}</div>
                <h4 className="font-serif text-lg text-gray-700">{item.name}</h4>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Footer */}
      <footer className="py-20 relative overflow-hidden bg-ivory">
        <div className="absolute top-0 right-0 w-96 h-96 bg-champagne rounded-full blur-3xl opacity-30 translate-x-1/2 -translate-y-1/2"></div>
        <div className="container mx-auto px-6 text-center relative z-10">
          <h2 className="text-5xl md:text-6xl font-serif mb-8">Discover Your Silhouette</h2>
          <p className="text-xl text-gray-600 mb-10">Try on 50+ looks now. It's time to fall in love.</p>
          <button className="btn-primary px-12 py-5 rounded-full text-xl shadow-xl hover:shadow-2xl mb-16">Start Your Joyful Discovery</button>
          <div className="border-t border-gray-200 pt-12 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="text-2xl font-serif italic text-gold">Novia</div>
            <div className="flex gap-8 text-sm text-gray-500">
              <a href="#" className="hover:text-gold">Privacy Policy</a>
              <a href="#" className="hover:text-gold">Terms of Service</a>
              <a href="#" className="hover:text-gold">Stylist Login</a>
            </div>
            <div className="flex gap-4">
              <button className="p-2 rounded-full bg-blush hover:bg-rose transition-colors text-gray-600"><Instagram size={20} /></button>
              <button className="p-2 rounded-full bg-blush hover:bg-rose transition-colors text-gray-600"><Facebook size={20} /></button>
              <button className="p-2 rounded-full bg-blush hover:bg-rose transition-colors text-gray-600"><Twitter size={20} /></button>
            </div>
          </div>
          <div className="mt-12 text-gray-400 text-xs">© 2024 Novia. Empowering brides through joyful discovery.</div>
        </div>
      </footer>
    </div>
  );
};

export default NoviaLanding;
