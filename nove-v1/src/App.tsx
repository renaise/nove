import { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';

export default function NoveLanding() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const heroHeight = window.innerHeight;
      setScrolled(window.scrollY > heroHeight - 100);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-white text-black font-serif selection:bg-black selection:text-white">

      {/* --- NAVBAR --- */}
      <nav className={`fixed w-full top-0 z-50 transition-all duration-300 ${
        scrolled ? 'bg-white/80 backdrop-blur-xl' : 'bg-transparent'
      }`}>
        <div className="flex justify-between items-center px-6 py-4 lg:px-10">
          {/* Logo */}
          <a href="#" className={`text-xl font-normal tracking-wide transition-colors duration-300 ${
            scrolled ? 'text-black' : 'text-[#FAFAFA]'
          }`}>Nove</a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            <a href="#" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>Browse</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>For Brides</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>For Boutiques</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>About</a>
          </div>

          {/* CTA Button */}
          <button className={`hidden md:block px-5 py-2 border text-[10px] uppercase tracking-[0.15em] transition-all duration-300 ${
            scrolled
              ? 'border-black text-black hover:bg-black hover:text-white'
              : 'border-[#FAFAFA] text-[#FAFAFA] hover:bg-[#FAFAFA] hover:text-black'
          }`}>
            Start Trying on
          </button>

          {/* Mobile Menu Button */}
          <button className={`md:hidden transition-colors duration-300 ${
            scrolled ? 'text-black' : 'text-[#FAFAFA]'
          }`} onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-white/90 backdrop-blur-xl p-6 flex flex-col gap-4">
            <a href="#" className="text-sm uppercase tracking-[0.15em] text-black">Browse</a>
            <a href="#" className="text-sm uppercase tracking-[0.15em] text-black">for Brides</a>
            <a href="#" className="text-sm uppercase tracking-[0.15em] text-black">for Boutiques</a>
            <a href="#" className="text-sm uppercase tracking-[0.15em] text-black">About</a>
            <button className="mt-4 w-full py-3 border border-black text-black text-xs uppercase tracking-[0.15em]">
              Start Trying on
            </button>
          </div>
        )}
      </nav>

      {/* --- HERO SECTION --- */}
      <section className="relative min-h-screen flex flex-col justify-end">
        {/* Full Viewport Background Image */}
        <div className="absolute inset-0">
          <img
            src="/hero-bride.jpg"
            alt="Bride in wedding dress"
            className="w-full h-full object-cover"
          />
          {/* Dark overlay for text readability */}
          <div className="absolute inset-0 bg-black/30" />
        </div>

        {/* Content at Bottom */}
        <div className="relative z-10 text-center px-6 max-w-2xl mx-auto mb-16 md:mb-24">
          <p className="text-[10px] uppercase tracking-[0.3em] text-[#FAFAFA]/60 mb-2 font-normal">Nove</p>
          <h1 className="text-2xl md:text-3xl lg:text-4xl font-normal leading-snug mb-4 tracking-[-0.02em] text-[#FAFAFA]">
            See the moment before it happens.
          </h1>
          <div className="flex flex-row gap-4 justify-center items-center">
            <button className="px-4 py-1.5 border border-[#FAFAFA] bg-transparent text-[#FAFAFA] text-[10px] uppercase tracking-[0.12em] hover:bg-[#FAFAFA] hover:text-black transition-all">
              Start Trying on
            </button>
            <button className="text-[#FAFAFA]/60 text-[10px] uppercase tracking-[0.12em] hover:text-[#FAFAFA] transition-all">
              For Boutiques
            </button>
          </div>
        </div>
      </section>

      {/* --- BROWSE / MARKETPLACE SECTION --- */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[10px] uppercase tracking-[0.15em] text-black/50 mb-3 font-normal">Browse</p>
            <h2 className="text-3xl md:text-4xl font-normal tracking-[-0.02em] mb-4 text-black">
              Find Your Dream Dress
            </h2>
            <p className="text-black/50 max-w-xl mx-auto">
              Browse thousands of wedding dresses from top designers. Try them on virtually before you buy.
            </p>
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-2 justify-center mb-4">
            {['All', 'A-Line', 'Ballgown', 'Mermaid', 'Sheath', 'Fit & Flare'].map((filter, i) => (
              <button
                key={filter}
                className={`px-4 py-1.5 text-[10px] uppercase tracking-[0.1em] border transition-all ${
                  i === 0
                    ? 'bg-black text-white border-black'
                    : 'bg-transparent text-black/50 border-black/20 hover:border-black hover:text-black'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          {/* Price Range */}
          <div className="flex flex-wrap gap-2 justify-center mb-10">
            {['Under $1,000', '$1,000 - $2,500', '$2,500 - $5,000', '$5,000+'].map((price) => (
              <button
                key={price}
                className="px-3 py-1 text-[10px] text-black/50 border border-black/20 hover:border-black hover:text-black transition-all"
              >
                {price}
              </button>
            ))}
          </div>

          {/* Dress Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {[
              { designer: 'Jenny Yoo', name: 'Briar', size: '4', price: 550, originalPrice: 3260, image: 'https://cdn.stillwhite.com/assets/cd/82/da/cd82da9e778b11ee832a06fde254d401/650x.jpg' },
              { designer: 'Pallas Couture', name: 'Roussillon', size: '2', price: 5500, originalPrice: 18000, image: 'https://cdn.stillwhite.com/assets/20/fe/5f/20fe5f1c6e5c11ee832a06fde254d401/650x.jpg' },
              { designer: 'Danielle Frankel', name: 'Eloise', size: '4', price: 2500, originalPrice: 5000, image: 'https://cdn.stillwhite.com/assets/fc/86/5e/fc865e214f1d11ef8aca02ffec65b5dd/650x.jpg' },
              { designer: 'Essense of Australia', name: 'D2760', size: '6', price: 650, originalPrice: 2000, image: 'https://cdn.stillwhite.com/assets/fe/13/1d/fe131d878acb11eb8f00068d169f9261/650x.jpg' },
              { designer: 'Danielle Frankel', name: 'Clara', size: '6', price: 475, originalPrice: 585, image: 'https://cdn.stillwhite.com/assets/9f/3c/d8/9f3cd868b6dd11ed868f06fde254d401/650x.jpg' },
              { designer: 'Morilee', name: 'Kristabelle', size: '10', price: 800, originalPrice: 2050, image: 'https://cdn.stillwhite.com/assets/ca/b4/22/cab4220e011811f09e7402ffec65b5dd/650x.jpg' },
              { designer: 'Stella York', name: '6840', size: '8', price: 750, originalPrice: 1550, image: 'https://cdn.stillwhite.com/assets/bc/52/ee/bc52ee6dc36011eab70502dadaedef01/650x.jpg' },
              { designer: 'Martina Liana', name: '1749', size: '10', price: 2100, originalPrice: 3100, image: 'https://cdn.stillwhite.com/assets/6a/c1/52/6ac152c2bc5011efa7fa06f0a0b47845/650x.jpg' },
            ].map((dress, index) => (
              <div key={index} className="group cursor-pointer">
                {/* Image */}
                <div className="relative aspect-[2/3] bg-black/5 mb-3 overflow-hidden">
                  <img
                    src={dress.image}
                    alt={`${dress.designer} ${dress.name}`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  {/* Save Badge */}
                  <div className="absolute top-3 left-3 bg-black text-white text-[10px] uppercase tracking-wider px-2 py-1">
                    Save {Math.round((1 - dress.price / dress.originalPrice) * 100)}%
                  </div>
                  {/* Quick View */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                    <button className="opacity-0 group-hover:opacity-100 transition-opacity bg-white text-black px-6 py-2 text-xs uppercase tracking-wider">
                      Try On
                    </button>
                  </div>
                </div>
                {/* Info */}
                <div className="space-y-1">
                  <p className="text-xs text-black/50 uppercase tracking-wider">{dress.designer}</p>
                  <p className="text-sm text-black">{dress.name}</p>
                  <p className="text-xs text-black/50">Size {dress.size}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-black">${dress.price.toLocaleString()}</span>
                    <span className="text-xs text-black/50 line-through">${dress.originalPrice.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* View All Button */}
          <div className="text-center mt-12">
            <button className="px-10 py-4 border border-black text-black text-xs uppercase tracking-[0.15em] hover:bg-black hover:text-white transition-all">
              View All Dresses
            </button>
          </div>
        </div>
      </section>

      {/* --- FOR BOUTIQUES SECTION --- */}
      <section className="py-24 bg-black">
        <div className="max-w-3xl mx-auto px-6 lg:px-12 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-[#FAFAFA]/50 mb-4">for Boutiques</p>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal tracking-[-0.02em] mb-6 text-[#FAFAFA]">
            Empower Your Brides
          </h2>
          <p className="text-lg text-[#FAFAFA]/50 leading-relaxed mb-10">
            Nove helps your boutique connect with informed, excited brides who already know what styles work for them. Reduce try-on time, increase conversions, and create unforgettable experiences.
          </p>
          <button className="px-10 py-4 border border-[#FAFAFA] text-[#FAFAFA] text-xs uppercase tracking-[0.15em] hover:bg-[#FAFAFA] hover:text-black transition-all">
            Partner With Us
          </button>
        </div>
      </section>

      {/* --- ABOUT SECTION --- */}
      <section className="py-24 bg-white">
        <div className="max-w-5xl mx-auto px-6 lg:px-12">
          {/* Text */}
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.3em] text-black/50 mb-4">About</p>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal tracking-[-0.02em] mb-6 text-black">
              Confidence in every choice.
            </h2>
            <p className="text-lg text-black/50 leading-relaxed max-w-2xl mx-auto">
              Your wedding dress is a tradition, not a guess. We built Nove as a simple tool to help you see exactly how different styles look on you—before you ever step foot in a store. It is a private way to explore your options and find the silhouette that feels right.
            </p>
          </div>

          {/* Prototype Preview */}
          <div className="relative">
            {/* Browser Frame */}
            <div className="bg-black/5 rounded-lg overflow-hidden">
              {/* Browser Bar */}
              <div className="flex items-center gap-2 px-4 py-3 bg-black/5 border-b border-black/10">
                <div className="flex gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-black/20" />
                  <div className="w-2.5 h-2.5 rounded-full bg-black/20" />
                  <div className="w-2.5 h-2.5 rounded-full bg-black/20" />
                </div>
                <div className="flex-1 mx-4">
                  <div className="bg-white rounded px-3 py-1 text-[10px] text-black/40 text-center">
                    nove.app/try-on
                  </div>
                </div>
              </div>
              {/* Preview Content */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-6 md:p-8">
                {/* Before */}
                <div className="aspect-[3/4] bg-black/10 rounded flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-black/20 flex items-center justify-center">
                      <span className="text-black/40 text-lg">+</span>
                    </div>
                    <p className="text-[10px] uppercase tracking-wider text-black/40">Your Photo</p>
                  </div>
                </div>
                {/* Arrow */}
                <div className="hidden md:flex items-center justify-center">
                  <div className="text-2xl text-black/20">→</div>
                </div>
                {/* After */}
                <div className="aspect-[3/4] bg-black/10 rounded overflow-hidden relative">
                  <img
                    src="https://cdn.stillwhite.com/assets/fc/86/5e/fc865e214f1d11ef8aca02ffec65b5dd/650x.jpg"
                    alt="Try-on result"
                    className="w-full h-full object-cover opacity-80"
                  />
                  <div className="absolute bottom-3 left-3 right-3 bg-white/90 backdrop-blur-sm rounded px-3 py-2">
                    <p className="text-[10px] uppercase tracking-wider text-black/60">Virtual Try-On</p>
                    <p className="text-xs text-black">Danielle Frankel · Eloise</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="py-16 bg-black text-[#FAFAFA]">
        <div className="max-w-6xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8 mb-12">
            <div className="text-2xl font-normal tracking-wide">Nove</div>
            <div className="flex gap-8 text-xs uppercase tracking-[0.15em]">
              <a href="#" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">Browse</a>
              <a href="#" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">for Brides</a>
              <a href="#" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">for Boutiques</a>
              <a href="#" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">About</a>
            </div>
          </div>
          <div className="border-t border-[#FAFAFA]/20 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-[#FAFAFA]/50">
            <p>© 2025 Nove. See the moment before it happens.</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-[#FAFAFA] transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-[#FAFAFA] transition-colors">Terms</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
