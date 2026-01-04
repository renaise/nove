import { useState, useEffect } from 'react';
import { Camera, Sparkles, User, Menu, X, Upload } from 'lucide-react';
import heroVideo from './assets/hero_video.mp4';

const NoveLanding = () => {
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
    <div className="min-h-screen font-sans bg-[#F5F5F5] text-[#4A4A4A]">
      {/* Navigation */}
      <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'bg-white/95 backdrop-blur-sm shadow-sm' : 'bg-transparent'}`}>
        <div className="container mx-auto px-6 py-5 flex justify-between items-center">
          <a href="#" className="text-2xl font-light tracking-wide text-[#1C1C1E]">Nove</a>
          <div className="hidden md:flex items-center gap-8">
            <a href="#shop" className="text-sm uppercase tracking-wider hover:text-[#E6B88A] transition-colors">Shop</a>
            <a href="#for-brides" className="text-sm uppercase tracking-wider hover:text-[#E6B88A] transition-colors">for Brides</a>
            <a href="#for-boutiques" className="text-sm uppercase tracking-wider hover:text-[#E6B88A] transition-colors">for Boutiques</a>
            <a href="#about" className="text-sm uppercase tracking-wider hover:text-[#E6B88A] transition-colors">About</a>
            <button className="px-6 py-2 border border-[#1C1C1E] text-[#1C1C1E] hover:bg-[#1C1C1E] hover:text-white transition-all text-sm uppercase tracking-wider">Start Trying on</button>
          </div>
          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-white shadow-lg p-6 flex flex-col gap-4">
            <a href="#shop" onClick={() => setMobileMenuOpen(false)} className="uppercase tracking-wider">Shop</a>
            <a href="#for-brides" onClick={() => setMobileMenuOpen(false)} className="uppercase tracking-wider">for Brides</a>
            <a href="#for-boutiques" onClick={() => setMobileMenuOpen(false)} className="uppercase tracking-wider">for Boutiques</a>
            <a href="#about" onClick={() => setMobileMenuOpen(false)} className="uppercase tracking-wider">About</a>
            <button className="w-full py-3 border border-[#1C1C1E] uppercase tracking-wider">Start Trying on</button>
          </div>
        )}
      </nav>

      {/* Hero Section - Minimal */}
      <header className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Video Background */}
        <div className="absolute inset-0 z-0">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover"
          >
            <source src={heroVideo} type="video/mp4" />
          </video>
          {/* Overlay to ensure text readability */}
          <div className="absolute inset-0 bg-white/30 backdrop-blur-[1px]"></div>
        </div>

        <div className="container mx-auto px-6 relative z-10 text-center mt-12">
          <p className="text-sm uppercase tracking-widest text-[#8E8E93] mb-4">Nove</p>
          <h1 className="text-5xl md:text-7xl font-light mb-12 text-[#1C1C1E] leading-tight max-w-4xl mx-auto">
            See the moment before it happens.
          </h1>
          <div className="flex flex-col md:flex-row gap-4 justify-center items-center">
            <button className="px-10 py-4 border border-[#1C1C1E] text-[#1C1C1E] hover:bg-[#1C1C1E] hover:text-white transition-all text-sm uppercase tracking-wider">Start Trying on</button>
            <button className="px-10 py-4 text-[#8E8E93] hover:text-[#1C1C1E] transition-all text-sm uppercase tracking-wider">For Boutiques</button>
          </div>
        </div>
      </header>

      {/* For Brides - Detailed Workflow */}
      <section id="for-brides" className="py-24 bg-white">
        <div className="container mx-auto px-6">
          <div className="mb-20 text-center">
            <p className="text-sm uppercase tracking-widest text-[#8E8E93] mb-2">for BRIDES</p>
            <h2 className="text-4xl md:text-5xl font-light text-[#1C1C1E]">Your Journey to The One</h2>
          </div>

          {/* Step 01: Silhouette Analysis */}
          <div className="grid md:grid-cols-2 gap-16 mb-24 items-center">
            <div>
              <div className="flex items-baseline gap-4 mb-6">
                <span className="text-6xl font-light text-[#E6B88A]">01</span>
                <div>
                  <h3 className="text-3xl font-light mb-2">The Silhouette Analysis</h3>
                  <p className="text-xs uppercase tracking-widest text-[#8E8E93]">CAPTURE</p>
                </div>
              </div>
              <p className="text-[#6E6E73] leading-relaxed mb-6">
                Upload a full-body photograph to begin the structural mapping process. Our system extracts 12-point landmarks to determine your precise proportion logic.
              </p>
              <button className="px-8 py-3 border border-[#1C1C1E] text-[#1C1C1E] hover:bg-[#1C1C1E] hover:text-white transition-all text-sm uppercase tracking-wider">
                Begin Analysis
              </button>
            </div>
            <div className="relative">
              <img
                src="/images/step1-silhouette.png"
                alt="Silhouette capture"
                className="w-full rounded-lg shadow-xl"
              />
              <div className="absolute inset-0 flex items-center justify-center bg-black/5 rounded-lg">
                <div className="text-center bg-white/90 backdrop-blur-sm px-8 py-6 rounded-lg">
                  <Upload className="mx-auto mb-3 text-[#E6B88A]" size={32} />
                  <p className="text-sm text-[#1C1C1E] mb-2">Upload Image</p>
                  <p className="text-xs text-[#8E8E93]">Drag and Drop or Click to Browse</p>
                </div>
              </div>
            </div>
          </div>

          {/* Step 02: Silhouette Result */}
          <div className="grid md:grid-cols-2 gap-16 mb-24 items-center">
            <div className="order-2 md:order-1">
              <img
                src="/images/step2-filter.png"
                alt="Analysis results"
                className="w-full rounded-lg shadow-xl"
              />
            </div>
            <div className="order-1 md:order-2">
              <div className="flex items-baseline gap-4 mb-6">
                <span className="text-6xl font-light text-[#E6B88A]">02</span>
                <div>
                  <h3 className="text-3xl font-light mb-2">Silhouette Result</h3>
                  <p className="text-xs uppercase tracking-widest text-[#8E8E93]">ANALYSIS</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-6">
                {['Volume', 'Body Contour', 'Waistline'].map((metric) => (
                  <div key={metric} className="border border-[#E5E5EA] p-6 rounded text-center hover:border-[#E6B88A] transition-colors">
                    <p className="text-sm text-[#6E6E73]">{metric}</p>
                  </div>
                ))}
              </div>
              <p className="text-[#6E6E73] leading-relaxed">
                Our AI analyzes your unique proportions to identify dress styles that will complement your natural silhouette.
              </p>
            </div>
          </div>

          {/* Step 03: Refine the Aesthetic */}
          <div className="grid md:grid-cols-2 gap-16 mb-24 items-center">
            <div>
              <div className="flex items-baseline gap-4 mb-6">
                <span className="text-6xl font-light text-[#E6B88A]">03</span>
                <div>
                  <h3 className="text-3xl font-light mb-2">Refine the Aesthetic</h3>
                  <p className="text-xs uppercase tracking-widest text-[#8E8E93]">STYLIST</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-6">
                {['Minimalist', 'Romantic', 'Avant-Garde', 'Classic'].map((style) => (
                  <button
                    key={style}
                    className="border border-[#E5E5EA] p-8 rounded text-center hover:border-[#E6B88A] hover:bg-[#F7F2EE] transition-all"
                  >
                    <p className="text-sm text-[#1C1C1E]">{style}</p>
                  </button>
                ))}
              </div>
              <p className="text-[#6E6E73] leading-relaxed">
                Choose the aesthetic that resonates with your vision. Our stylist AI will curate selections aligned with your personal taste.
              </p>
            </div>
            <div>
              <img
                src="/images/step3-tryon.png"
                alt="Aesthetic refinement"
                className="w-full rounded-lg shadow-xl"
              />
            </div>
          </div>

          {/* Step 04: Curated Selection */}
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <div className="order-2 md:order-1">
              <img
                src="/images/step4-nextstep.png"
                alt="Curated selection"
                className="w-full rounded-lg shadow-xl"
              />
            </div>
            <div className="order-1 md:order-2">
              <div className="flex items-baseline gap-4 mb-6">
                <span className="text-6xl font-light text-[#E6B88A]">04</span>
                <div>
                  <h3 className="text-3xl font-light mb-2">Curated Selection</h3>
                  <p className="text-xs uppercase tracking-widest text-[#8E8E93]">REVEAL</p>
                </div>
              </div>
              <p className="text-[#6E6E73] leading-relaxed mb-6">
                See yourself in your dream dresses. Try on dozens of gowns virtually, then connect with boutiques to experience them in person.
              </p>
              <button className="px-8 py-3 bg-[#E6B88A] text-white hover:bg-[#D4AF37] transition-all text-sm uppercase tracking-wider">
                Start Your Journey
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* For Boutiques - Brief Section */}
      <section id="for-boutiques" className="py-24 bg-[#F7F2EE]">
        <div className="container mx-auto px-6 text-center max-w-4xl">
          <p className="text-sm uppercase tracking-widest text-[#8E8E93] mb-4">for BOUTIQUES</p>
          <h2 className="text-4xl md:text-5xl font-light text-[#1C1C1E] mb-6">
            Empower Your Brides
          </h2>
          <p className="text-lg text-[#6E6E73] leading-relaxed mb-10">
            Nove helps your boutique connect with informed, excited brides who already know what styles work for them. Reduce try-on time, increase conversions, and create unforgettable experiences.
          </p>
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {[
              { icon: Camera, title: 'Pre-Qualified Leads', desc: 'Brides arrive knowing their silhouette' },
              { icon: Sparkles, title: 'Enhanced Experience', desc: 'Virtual try-on before in-person visits' },
              { icon: User, title: 'Seamless Integration', desc: 'Connect directly with your inventory' },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="text-center">
                <Icon className="mx-auto mb-4 text-[#E6B88A]" size={40} />
                <h3 className="text-lg font-medium text-[#1C1C1E] mb-2">{title}</h3>
                <p className="text-sm text-[#6E6E73]">{desc}</p>
              </div>
            ))}
          </div>
          <button className="px-10 py-4 border border-[#1C1C1E] text-[#1C1C1E] hover:bg-[#1C1C1E] hover:text-white transition-all text-sm uppercase tracking-wider">
            Partner With Us
          </button>
        </div>
      </section>

      {/* About / Trust Section */}
      <section id="about" className="py-24 bg-white">
        <div className="container mx-auto px-6 text-center max-w-3xl">
          <p className="text-sm uppercase tracking-widest text-[#8E8E93] mb-4">About</p>
          <h2 className="text-4xl md:text-5xl font-light text-[#1C1C1E] mb-6">
            Privacy First, Always
          </h2>
          <p className="text-lg text-[#6E6E73] leading-relaxed mb-8">
            Your photos are encrypted, processed securely, and never shared. We believe your wedding journey should be joyful, stress-free, and completely private.
          </p>
          <div className="inline-block px-6 py-2 bg-[#F7F2EE] rounded-full text-sm text-[#6E6E73]">
            🔒 Strictly Private • AI-Powered • Boutique Connected
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 bg-[#1C1C1E] text-white">
        <div className="container mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8 mb-12">
            <div className="text-2xl font-light tracking-wide">Nove</div>
            <div className="flex gap-8 text-sm uppercase tracking-wider">
              <a href="#shop" className="hover:text-[#E6B88A] transition-colors">Shop</a>
              <a href="#for-brides" className="hover:text-[#E6B88A] transition-colors">for Brides</a>
              <a href="#for-boutiques" className="hover:text-[#E6B88A] transition-colors">for Boutiques</a>
              <a href="#about" className="hover:text-[#E6B88A] transition-colors">About</a>
            </div>
          </div>
          <div className="border-t border-white/20 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-white/60">
            <p>© 2025 Nove. See the moment before it happens.</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default NoveLanding;
