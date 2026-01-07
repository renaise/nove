import { useState, useEffect, useMemo } from 'react';
import { Menu, X } from 'lucide-react';

// Dress data with silhouette types
const dressData = [
  { designer: 'Jenny Yoo', name: 'Briar', size: '4', price: 550, originalPrice: 3260, silhouette: 'A-Line', image: 'https://cdn.stillwhite.com/assets/cd/82/da/cd82da9e778b11ee832a06fde254d401/650x.jpg' },
  { designer: 'Pallas Couture', name: 'Roussillon', size: '2', price: 5500, originalPrice: 18000, silhouette: 'Mermaid', image: 'https://cdn.stillwhite.com/assets/20/fe/5f/20fe5f1c6e5c11ee832a06fde254d401/650x.jpg' },
  { designer: 'Danielle Frankel', name: 'Eloise', size: '4', price: 2500, originalPrice: 5000, silhouette: 'Sheath', image: 'https://cdn.stillwhite.com/assets/fc/86/5e/fc865e214f1d11ef8aca02ffec65b5dd/650x.jpg' },
  { designer: 'Essense of Australia', name: 'D2760', size: '6', price: 650, originalPrice: 2000, silhouette: 'Ballgown', image: 'https://cdn.stillwhite.com/assets/fe/13/1d/fe131d878acb11eb8f00068d169f9261/650x.jpg' },
  { designer: 'Danielle Frankel', name: 'Clara', size: '6', price: 475, originalPrice: 585, silhouette: 'Sheath', image: 'https://cdn.stillwhite.com/assets/9f/3c/d8/9f3cd868b6dd11ed868f06fde254d401/650x.jpg' },
  { designer: 'Morilee', name: 'Kristabelle', size: '10', price: 800, originalPrice: 2050, silhouette: 'Ballgown', image: 'https://cdn.stillwhite.com/assets/ca/b4/22/cab4220e011811f09e7402ffec65b5dd/650x.jpg' },
  { designer: 'Stella York', name: '6840', size: '8', price: 750, originalPrice: 1550, silhouette: 'Fit & Flare', image: 'https://cdn.stillwhite.com/assets/bc/52/ee/bc52ee6dc36011eab70502dadaedef01/650x.jpg' },
  { designer: 'Martina Liana', name: '1749', size: '10', price: 2100, originalPrice: 3100, silhouette: 'A-Line', image: 'https://cdn.stillwhite.com/assets/6a/c1/52/6ac152c2bc5011efa7fa06f0a0b47845/650x.jpg' },
  { designer: 'Pronovias', name: 'Draco', size: '8', price: 1200, originalPrice: 2800, silhouette: 'Mermaid', image: 'https://cdn.stillwhite.com/assets/8a/7e/3c/8a7e3c5e9f8a11ee832a06fde254d401/650x.jpg' },
  { designer: 'Vera Wang', name: 'Liesel', size: '6', price: 1800, originalPrice: 4500, silhouette: 'A-Line', image: 'https://cdn.stillwhite.com/assets/b2/4d/9e/b24d9e7a8c6b11ed868f06fde254d401/650x.jpg' },
  { designer: 'Monique Lhuillier', name: 'Bliss', size: '4', price: 3200, originalPrice: 6800, silhouette: 'Ballgown', image: 'https://cdn.stillwhite.com/assets/d4/6f/2a/d46f2a3c7d9e11ef8aca02ffec65b5dd/650x.jpg' },
  { designer: 'Oscar de la Renta', name: 'Caroline', size: '2', price: 4500, originalPrice: 9000, silhouette: 'Fit & Flare', image: 'https://cdn.stillwhite.com/assets/e5/8a/1b/e58a1b4d6c8f11ee832a06fde254d401/650x.jpg' },
];

const silhouetteFilters = ['All', 'A-Line', 'Ballgown', 'Mermaid', 'Sheath', 'Fit & Flare'];
const priceFilters = [
  { label: 'All Prices', min: 0, max: Infinity },
  { label: 'Under $1,000', min: 0, max: 999 },
  { label: '$1,000 - $2,500', min: 1000, max: 2500 },
  { label: '$2,500 - $5,000', min: 2500, max: 5000 },
  { label: '$5,000+', min: 5000, max: Infinity },
];

export default function NoveLanding() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [selectedSilhouette, setSelectedSilhouette] = useState('All');
  const [selectedPriceIndex, setSelectedPriceIndex] = useState(0);

  // For Brides interactive state
  const [bridesStep, setBridesStep] = useState(1);
  const [selectedBridesSilhouette, setSelectedBridesSilhouette] = useState<string | null>(null);
  const [selectedAesthetic, setSelectedAesthetic] = useState<string | null>(null);

  // Filter dresses based on selected filters
  const filteredDresses = useMemo(() => {
    return dressData.filter(dress => {
      const matchesSilhouette = selectedSilhouette === 'All' || dress.silhouette === selectedSilhouette;
      const priceFilter = priceFilters[selectedPriceIndex];
      const matchesPrice = dress.price >= priceFilter.min && dress.price <= priceFilter.max;
      return matchesSilhouette && matchesPrice;
    });
  }, [selectedSilhouette, selectedPriceIndex]);

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
        <div className="relative flex items-center justify-between px-6 py-4 lg:px-10">
          {/* Logo */}
          <a href="#" className="transition-opacity duration-300">
            <svg className="h-4" viewBox="0 0 47 17" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3.936 3.12H3.888V13.008C3.888 14.136 4.008 14.832 4.248 15.12C4.512 15.408 5.136 15.552 6.144 15.576V15.888H0.936V15.576C1.896 15.552 2.52 15.408 2.784 15.12C3.048 14.832 3.192 14.136 3.192 13.008V2.208C2.832 1.752 2.544 1.416 2.304 1.2C1.848 0.744 1.032 0.312 0 0.312V0H3.384L14.184 13.248H14.232V2.976C14.232 1.848 14.088 1.128 13.824 0.816001C13.56 0.504001 12.936 0.336001 11.976 0.312V0H17.184V0.312C16.248 0.336001 15.648 0.504001 15.36 0.816001C15.072 1.128 14.928 1.848 14.928 2.976V16.152H14.592L3.936 3.12Z" className={`transition-colors duration-300 ${scrolled ? 'fill-black' : 'fill-[#FAFAFA]'}`}/>
              <path d="M22.1897 4.824C23.4617 4.824 24.6137 5.352 25.5977 6.408C26.5817 7.44 27.0857 8.736 27.0857 10.272C27.0857 11.256 26.9177 12.192 26.5817 13.08C25.9097 14.808 24.3017 16.224 22.1657 16.224C20.8937 16.224 19.7657 15.672 18.7817 14.568C17.7977 13.464 17.2937 12.168 17.2937 10.656C17.2937 9 17.7737 7.632 18.7097 6.504C19.6457 5.376 20.8217 4.824 22.1897 4.824ZM21.9497 5.424C21.0617 5.424 20.3417 5.808 19.7417 6.6C19.1417 7.392 18.8537 8.424 18.8537 9.696C18.8537 11.4 19.1897 12.84 19.8857 13.968C20.5817 15.096 21.4937 15.648 22.5977 15.648C24.9497 15.648 25.5257 12.984 25.5257 11.304C25.5257 7.464 24.0377 5.424 21.9497 5.424Z" className={`transition-colors duration-300 ${scrolled ? 'fill-black' : 'fill-[#FAFAFA]'}`}/>
              <path d="M30.4978 7.44L33.1618 13.896L35.8498 7.416C36.0898 6.84 36.2098 6.408 36.2098 6.096C36.2098 5.64 35.9218 5.496 35.0578 5.472V5.16H38.2498V5.472C37.9378 5.472 37.6498 5.568 37.4098 5.76C36.9538 6.144 36.8578 6.432 36.5458 7.176L32.8498 16.224H32.5858L28.6978 6.792C28.2898 5.832 27.9058 5.544 26.9458 5.472V5.16H31.3858V5.472C30.5218 5.472 30.1378 5.616 30.1378 6.216C30.1378 6.432 30.2578 6.84 30.4978 7.44Z" className={`transition-colors duration-300 ${scrolled ? 'fill-black' : 'fill-[#FAFAFA]'}`}/>
              <path d="M46.986 9.216H39.33C39.33 12.888 40.89 14.904 43.122 14.904C44.874 14.904 46.05 13.848 46.65 11.76L46.914 11.904C46.698 13.128 46.218 14.136 45.474 14.976C44.73 15.816 43.794 16.224 42.69 16.224C41.346 16.224 40.242 15.696 39.378 14.664C38.538 13.632 38.106 12.288 38.106 10.656C38.106 7.08 40.002 4.824 42.906 4.824C44.13 4.824 45.114 5.232 45.858 6.048C46.602 6.864 46.986 7.92 46.986 9.216ZM39.354 8.616H45.162C45.186 6.672 44.058 5.448 42.402 5.448C41.658 5.448 40.962 5.76 40.362 6.36C39.762 6.96 39.426 7.704 39.354 8.616Z" className={`transition-colors duration-300 ${scrolled ? 'fill-black' : 'fill-[#FAFAFA]'}`}/>
            </svg>
          </a>

          {/* Desktop Nav - Centered */}
          <div className="hidden md:flex items-center gap-10 absolute left-1/2 -translate-x-1/2">
            <a href="#about" className={`text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
              scrolled ? 'text-black/70 hover:text-black' : 'text-white/80 hover:text-white'
            }`}>About</a>
            <a href="#for-brides" className={`text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
              scrolled ? 'text-black/70 hover:text-black' : 'text-white/80 hover:text-white'
            }`}>For Brides</a>
            <a href="#boutiques" className={`text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
              scrolled ? 'text-black/70 hover:text-black' : 'text-white/80 hover:text-white'
            }`}>For Boutiques</a>
            <a href="#browse" className={`text-xs uppercase tracking-[0.15em] transition-colors duration-300 ${
              scrolled ? 'text-black/70 hover:text-black' : 'text-white/80 hover:text-white'
            }`}>Browse</a>
          </div>

          {/* CTA Button - underline style */}
          <a href="#for-brides" className={`hidden md:block text-xs uppercase tracking-[0.15em] transition-all duration-300 border-b ${
            scrolled
              ? 'text-black border-black/30 hover:border-black'
              : 'text-white border-white/30 hover:border-white'
          }`}>
            Try On
          </a>

          {/* Mobile Menu Button */}
          <button className={`md:hidden transition-colors duration-300 ${
            scrolled ? 'text-black' : 'text-[#FAFAFA]'
          }`} onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 w-full bg-white p-8 flex flex-col gap-6 border-t border-black/10">
            <a href="#about" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black/70">About</a>
            <a href="#for-brides" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black/70">For Brides</a>
            <a href="#boutiques" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black/70">For Boutiques</a>
            <a href="#browse" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black/70">Browse</a>
            <a href="#for-brides" onClick={() => setMobileMenuOpen(false)} className="mt-4 text-sm uppercase tracking-[0.15em] text-black border-b border-black/30 self-start pb-1">
              Try On
            </a>
          </div>
        )}
      </nav>

      {/* --- HERO SECTION --- */}
      <section className="relative min-h-screen flex flex-col justify-end">
        {/* Full Viewport Background Video */}
        <div className="absolute inset-0">
          <video
            autoPlay
            muted
            loop
            playsInline
            className="w-full h-full object-cover"
          >
            <source src="/hero_video.mp4" type="video/mp4" />
          </video>
          {/* Dark overlay for text readability */}
          <div className="absolute inset-0 bg-black/40" />
        </div>

        {/* Content at Bottom */}
        <div className="relative z-10 text-center px-6 max-w-2xl mx-auto mb-20 md:mb-32">
          <p className="text-xs uppercase tracking-[0.25em] text-white/60 mb-6">Virtual Bridal Studio</p>
          <h1 className="text-2xl md:text-3xl lg:text-4xl leading-relaxed mb-8 tracking-[-0.02em] text-white">
            See the moment before it happens
          </h1>
          <div className="flex flex-row gap-8 justify-center items-center">
            <a href="#for-brides" className="text-xs uppercase tracking-[0.15em] text-white border-b border-white/40 pb-1 hover:border-white transition-all">
              Try On
            </a>
            <a href="mailto:developer@codexfoundry.com" className="text-xs uppercase tracking-[0.15em] text-white/50 hover:text-white transition-all">
              Contact
            </a>
          </div>
        </div>
      </section>

      {/* --- ABOUT SECTION --- */}
      <section id="about" className="py-32 md:py-40 bg-[#FAFAFA] scroll-mt-20">
        <div className="max-w-4xl mx-auto px-6 lg:px-12">
          {/* Text */}
          <div className="text-center mb-20">
            <p className="text-xs uppercase tracking-[0.25em] text-black/40 mb-6">About</p>
            <h2 className="text-3xl md:text-4xl tracking-[-0.02em] mb-8 text-black">
              Confidence in every choice
            </h2>
            <p className="text-base text-black/50 leading-relaxed max-w-xl mx-auto">
              Your wedding dress is a tradition, not a guess. We built Nove as a simple tool to help you see exactly how different styles look on you—before you ever step foot in a store. A private way to explore your options and find the silhouette that feels right.
            </p>
          </div>

          {/* Prototype Preview */}
          <div className="relative">
            <div className="bg-white overflow-hidden">
              {/* Preview Content */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-1">
                {/* Before */}
                <div className="aspect-[3/4] bg-[#F0F0F0] flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-xs uppercase tracking-[0.15em] text-black/30">Your Photo</p>
                  </div>
                </div>
                {/* Arrow */}
                <div className="hidden md:flex items-center justify-center bg-[#F0F0F0]">
                  <span className="text-black/20 text-base tracking-widest">→</span>
                </div>
                {/* After */}
                <div className="aspect-[3/4] bg-[#F0F0F0] overflow-hidden relative group">
                  <img
                    src="https://cdn.stillwhite.com/assets/fc/86/5e/fc865e214f1d11ef8aca02ffec65b5dd/650x.jpg"
                    alt="Try-on result"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute bottom-0 left-0 right-0 bg-white/95 px-4 py-3">
                    <p className="text-xs uppercase tracking-[0.15em] text-black/40">Virtual Try-On</p>
                    <p className="text-sm text-black mt-1">Danielle Frankel · Eloise</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- FOR BRIDES SECTION --- */}
      <section id="for-brides" className="py-32 md:py-40 bg-white scroll-mt-20">
        <div className="max-w-6xl mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24">
            {/* Left - Steps */}
            <div className="space-y-10">
              <p className="text-xs uppercase tracking-[0.25em] text-black/40">For Brides</p>

              {/* Step 01 */}
              <div
                className={`border-t pt-8 cursor-pointer transition-all ${bridesStep >= 1 ? 'border-black/20' : 'border-black/10'}`}
                onClick={() => setBridesStep(1)}
              >
                <div className="flex justify-between items-start mb-5">
                  <div className="flex items-baseline gap-6">
                    <span className={`text-xs tracking-[0.15em] ${bridesStep >= 1 ? 'text-black/60' : 'text-black/30'}`}>01</span>
                    <span className={`text-base tracking-wide ${bridesStep === 1 ? 'text-black' : 'text-black/40'}`}>Silhouette Analysis</span>
                  </div>
                </div>
                {bridesStep === 1 && (
                  <>
                    <p className="text-sm text-black/40 mb-6 ml-12 leading-relaxed">Upload a photo. Our AI analyzes your shape to determine which silhouettes will flatter you most.</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); setBridesStep(2); }}
                      className="ml-12 text-xs uppercase tracking-[0.15em] text-black border-b border-black/30 pb-1 hover:border-black transition-all"
                    >
                      Begin
                    </button>
                  </>
                )}
              </div>

              {/* Step 02 */}
              <div
                className={`border-t pt-8 transition-all ${bridesStep >= 2 ? 'border-black/20 cursor-pointer' : 'border-black/10 opacity-40'}`}
                onClick={() => bridesStep >= 2 && setBridesStep(2)}
              >
                <div className="flex justify-between items-start mb-5">
                  <div className="flex items-baseline gap-6">
                    <span className={`text-xs tracking-[0.15em] ${bridesStep >= 2 ? 'text-black/60' : 'text-black/30'}`}>02</span>
                    <span className={`text-base tracking-wide ${bridesStep === 2 ? 'text-black' : 'text-black/40'}`}>Select Silhouette</span>
                  </div>
                </div>
                {bridesStep === 2 && (
                  <div className="grid grid-cols-4 gap-2 ml-12">
                    {['A-line', 'Ball Gown', 'Mermaid', 'Sheath'].map((style) => (
                      <button
                        key={style}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedBridesSilhouette(style);
                          setTimeout(() => setBridesStep(3), 300);
                        }}
                        className={`py-3 text-center text-xs uppercase tracking-[0.1em] transition-all ${
                          selectedBridesSilhouette === style
                            ? 'bg-black text-white'
                            : 'bg-[#F0F0F0] text-black/50 hover:bg-[#E5E5E5] hover:text-black'
                        }`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                )}
                {bridesStep > 2 && selectedBridesSilhouette && (
                  <p className="text-sm text-black/40 ml-12">{selectedBridesSilhouette}</p>
                )}
              </div>

              {/* Step 03 */}
              <div
                className={`border-t pt-8 transition-all ${bridesStep >= 3 ? 'border-black/20 cursor-pointer' : 'border-black/10 opacity-40'}`}
                onClick={() => bridesStep >= 3 && setBridesStep(3)}
              >
                <div className="flex justify-between items-start mb-5">
                  <div className="flex items-baseline gap-6">
                    <span className={`text-xs tracking-[0.15em] ${bridesStep >= 3 ? 'text-black/60' : 'text-black/30'}`}>03</span>
                    <span className={`text-base tracking-wide ${bridesStep === 3 ? 'text-black' : 'text-black/40'}`}>Refine Aesthetic</span>
                  </div>
                </div>
                {bridesStep === 3 && (
                  <div className="grid grid-cols-2 gap-2 ml-12">
                    {['Minimalist', 'Romantic', 'Avant-Garde', 'Classic'].map((aesthetic) => (
                      <button
                        key={aesthetic}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAesthetic(aesthetic);
                          setTimeout(() => setBridesStep(4), 300);
                        }}
                        className={`py-3 text-center text-xs uppercase tracking-[0.1em] transition-all ${
                          selectedAesthetic === aesthetic
                            ? 'bg-black text-white'
                            : 'bg-[#F0F0F0] text-black/50 hover:bg-[#E5E5E5] hover:text-black'
                        }`}
                      >
                        {aesthetic}
                      </button>
                    ))}
                  </div>
                )}
                {bridesStep > 3 && selectedAesthetic && (
                  <p className="text-sm text-black/40 ml-12">{selectedAesthetic}</p>
                )}
              </div>

              {/* Step 04 */}
              <div
                className={`border-t pt-8 transition-all ${bridesStep >= 4 ? 'border-black/20' : 'border-black/10 opacity-40'}`}
              >
                <div className="flex justify-between items-start mb-5">
                  <div className="flex items-baseline gap-6">
                    <span className={`text-xs tracking-[0.15em] ${bridesStep >= 4 ? 'text-black/60' : 'text-black/30'}`}>04</span>
                    <span className={`text-base tracking-wide ${bridesStep === 4 ? 'text-black' : 'text-black/40'}`}>Curated Selection</span>
                  </div>
                </div>
                {bridesStep === 4 && (
                  <div className="ml-12">
                    <p className="text-sm text-black/40 mb-6 leading-relaxed">Based on your {selectedBridesSilhouette} silhouette and {selectedAesthetic} aesthetic.</p>
                    <div className="flex gap-6">
                      <a
                        href="#browse"
                        className="text-xs uppercase tracking-[0.15em] text-black border-b border-black pb-1 hover:border-black/50 transition-all"
                      >
                        View Matches
                      </a>
                      <button
                        onClick={() => { setBridesStep(1); setSelectedBridesSilhouette(null); setSelectedAesthetic(null); }}
                        className="text-xs uppercase tracking-[0.15em] text-black/40 hover:text-black transition-all"
                      >
                        Start Over
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Right - Image Upload Preview */}
            <div className="relative">
              <div className="aspect-[3/4] bg-[#F0F0F0] overflow-hidden relative">
                <img
                  src="/hero-bride.jpg"
                  alt="Bride preview"
                  className={`w-full h-full object-cover transition-opacity duration-500 ${bridesStep >= 2 ? 'opacity-100' : 'opacity-30'}`}
                />
                {bridesStep === 1 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div
                      className="text-center cursor-pointer"
                      onClick={() => setBridesStep(2)}
                    >
                      <p className="text-xs uppercase tracking-[0.15em] text-black/40 mb-2">Upload Image</p>
                      <p className="text-sm text-black/30">Click to browse</p>
                    </div>
                  </div>
                )}
                {bridesStep === 4 && (
                  <div className="absolute bottom-0 left-0 right-0 bg-white/95 px-5 py-4">
                    <p className="text-xs uppercase tracking-[0.15em] text-black/40 mb-1">Your Match</p>
                    <p className="text-sm text-black">{selectedBridesSilhouette} · {selectedAesthetic}</p>
                  </div>
                )}
              </div>
              {/* Progress indicator */}
              <div className="flex justify-center gap-3 mt-6">
                {[1, 2, 3, 4].map((step) => (
                  <div
                    key={step}
                    className={`h-px transition-all ${
                      step <= bridesStep ? 'w-8 bg-black' : 'w-4 bg-black/20'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- BROWSE / MARKETPLACE SECTION --- */}
      <section id="browse" className="py-32 md:py-40 bg-[#FAFAFA] scroll-mt-20">
        <div className="max-w-6xl mx-auto px-6 lg:px-12">
          {/* Header */}
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.25em] text-black/40 mb-6">Browse</p>
            <h2 className="text-3xl md:text-4xl tracking-[-0.02em] mb-6 text-black">
              Find Your Dress
            </h2>
            <p className="text-base text-black/40 max-w-md mx-auto">
              Browse thousands of wedding dresses from top designers. Try them on virtually before you buy.
            </p>
          </div>

          {/* Filters */}
          <div className="overflow-x-auto pb-2 mb-6 -mx-6 px-6 md:overflow-visible md:mx-0 md:px-0">
            <div className="flex gap-8 justify-start md:justify-center min-w-max md:min-w-0">
              {silhouetteFilters.map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSelectedSilhouette(filter)}
                  className={`text-xs uppercase tracking-[0.15em] transition-all whitespace-nowrap pb-1 ${
                    selectedSilhouette === filter
                      ? 'text-black border-b border-black'
                      : 'text-black/40 hover:text-black'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div className="overflow-x-auto pb-2 mb-12 -mx-6 px-6 md:overflow-visible md:mx-0 md:px-0">
            <div className="flex gap-8 justify-start md:justify-center min-w-max md:min-w-0">
              {priceFilters.map((price, index) => (
                <button
                  key={price.label}
                  onClick={() => setSelectedPriceIndex(index)}
                  className={`text-xs uppercase tracking-[0.1em] transition-all whitespace-nowrap pb-1 ${
                    selectedPriceIndex === index
                      ? 'text-black border-b border-black'
                      : 'text-black/40 hover:text-black'
                  }`}
                >
                  {price.label}
                </button>
              ))}
            </div>
          </div>

          {/* Dress Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-1">
            {filteredDresses.length > 0 ? filteredDresses.map((dress, index) => (
              <div key={index} className="group cursor-pointer">
                {/* Image */}
                <div className="relative aspect-[2/3] bg-[#F0F0F0] overflow-hidden">
                  <img
                    src={dress.image}
                    alt={`${dress.designer} ${dress.name}`}
                    className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-700"
                  />
                  {/* Quick View hover */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-end justify-center pb-8">
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-xs uppercase tracking-[0.15em] text-white">
                      Try On
                    </span>
                  </div>
                </div>
                {/* Info */}
                <div className="py-4 px-1">
                  <p className="text-xs uppercase tracking-[0.15em] text-black/40 mb-1">{dress.designer}</p>
                  <p className="text-sm text-black mb-1">{dress.name}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-black">${dress.price.toLocaleString()}</span>
                    <span className="text-xs text-black/30 line-through">${dress.originalPrice.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )) : (
              <div className="col-span-full text-center py-20">
                <p className="text-base text-black/40 mb-4">No dresses match your filters</p>
                <button
                  onClick={() => { setSelectedSilhouette('All'); setSelectedPriceIndex(0); }}
                  className="text-xs uppercase tracking-[0.15em] text-black/40 border-b border-black/20 pb-1 hover:text-black hover:border-black transition-all"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>

          {/* View All Button */}
          <div className="text-center mt-16">
            <a
              href="https://www.stillwhite.com/dresses"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-xs uppercase tracking-[0.15em] text-black border-b border-black pb-1 hover:border-black/40 transition-all"
            >
              View All Dresses
            </a>
          </div>
        </div>
      </section>

      {/* --- FOR BOUTIQUES SECTION --- */}
      <section id="boutiques" className="py-32 md:py-40 bg-black scroll-mt-20">
        <div className="max-w-2xl mx-auto px-6 lg:px-12 text-center">
          <p className="text-xs uppercase tracking-[0.25em] text-white/40 mb-8">For Boutiques</p>
          <h2 className="text-3xl md:text-4xl tracking-[-0.02em] mb-8 text-white">
            Empower Your Brides
          </h2>
          <p className="text-base text-white/40 leading-relaxed mb-12">
            Nove helps your boutique connect with informed, excited brides who already know what styles work for them. Reduce try-on time, increase conversions, and create unforgettable experiences.
          </p>
          <a href="mailto:developer@codexfoundry.com" className="inline-block text-xs uppercase tracking-[0.15em] text-white border-b border-white/40 pb-1 hover:border-white transition-all">
            Partner With Us
          </a>
        </div>
      </section>

      {/* --- MARQUEE SECTION --- */}
      <section className="py-5 bg-white border-t border-black/5 overflow-hidden">
        <div className="relative">
          <div className="flex animate-marquee whitespace-nowrap">
            {[...Array(8)].map((_, i) => (
              <span key={i} className="mx-12 text-xs uppercase tracking-[0.2em] text-black/30">
                Follow us on Instagram
                <span className="mx-12">·</span>
                @nove.bridal
                <span className="mx-12">·</span>
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="py-20 bg-white border-t border-black/5">
        <div className="max-w-6xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-10 mb-16">
            <svg className="h-5" viewBox="0 0 47 17" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3.936 3.12H3.888V13.008C3.888 14.136 4.008 14.832 4.248 15.12C4.512 15.408 5.136 15.552 6.144 15.576V15.888H0.936V15.576C1.896 15.552 2.52 15.408 2.784 15.12C3.048 14.832 3.192 14.136 3.192 13.008V2.208C2.832 1.752 2.544 1.416 2.304 1.2C1.848 0.744 1.032 0.312 0 0.312V0H3.384L14.184 13.248H14.232V2.976C14.232 1.848 14.088 1.128 13.824 0.816001C13.56 0.504001 12.936 0.336001 11.976 0.312V0H17.184V0.312C16.248 0.336001 15.648 0.504001 15.36 0.816001C15.072 1.128 14.928 1.848 14.928 2.976V16.152H14.592L3.936 3.12Z" fill="black"/>
              <path d="M22.1897 4.824C23.4617 4.824 24.6137 5.352 25.5977 6.408C26.5817 7.44 27.0857 8.736 27.0857 10.272C27.0857 11.256 26.9177 12.192 26.5817 13.08C25.9097 14.808 24.3017 16.224 22.1657 16.224C20.8937 16.224 19.7657 15.672 18.7817 14.568C17.7977 13.464 17.2937 12.168 17.2937 10.656C17.2937 9 17.7737 7.632 18.7097 6.504C19.6457 5.376 20.8217 4.824 22.1897 4.824ZM21.9497 5.424C21.0617 5.424 20.3417 5.808 19.7417 6.6C19.1417 7.392 18.8537 8.424 18.8537 9.696C18.8537 11.4 19.1897 12.84 19.8857 13.968C20.5817 15.096 21.4937 15.648 22.5977 15.648C24.9497 15.648 25.5257 12.984 25.5257 11.304C25.5257 7.464 24.0377 5.424 21.9497 5.424Z" fill="black"/>
              <path d="M30.4978 7.44L33.1618 13.896L35.8498 7.416C36.0898 6.84 36.2098 6.408 36.2098 6.096C36.2098 5.64 35.9218 5.496 35.0578 5.472V5.16H38.2498V5.472C37.9378 5.472 37.6498 5.568 37.4098 5.76C36.9538 6.144 36.8578 6.432 36.5458 7.176L32.8498 16.224H32.5858L28.6978 6.792C28.2898 5.832 27.9058 5.544 26.9458 5.472V5.16H31.3858V5.472C30.5218 5.472 30.1378 5.616 30.1378 6.216C30.1378 6.432 30.2578 6.84 30.4978 7.44Z" fill="black"/>
              <path d="M46.986 9.216H39.33C39.33 12.888 40.89 14.904 43.122 14.904C44.874 14.904 46.05 13.848 46.65 11.76L46.914 11.904C46.698 13.128 46.218 14.136 45.474 14.976C44.73 15.816 43.794 16.224 42.69 16.224C41.346 16.224 40.242 15.696 39.378 14.664C38.538 13.632 38.106 12.288 38.106 10.656C38.106 7.08 40.002 4.824 42.906 4.824C44.13 4.824 45.114 5.232 45.858 6.048C46.602 6.864 46.986 7.92 46.986 9.216ZM39.354 8.616H45.162C45.186 6.672 44.058 5.448 42.402 5.448C41.658 5.448 40.962 5.76 40.362 6.36C39.762 6.96 39.426 7.704 39.354 8.616Z" fill="black"/>
            </svg>
            <div className="flex gap-10 text-xs uppercase tracking-[0.15em]">
              <a href="#about" className="text-black/40 hover:text-black transition-colors">About</a>
              <a href="#for-brides" className="text-black/40 hover:text-black transition-colors">For Brides</a>
              <a href="#boutiques" className="text-black/40 hover:text-black transition-colors">For Boutiques</a>
              <a href="#browse" className="text-black/40 hover:text-black transition-colors">Browse</a>
            </div>
          </div>
          <div className="border-t border-black/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-black/30 tracking-wide">
            <p>© 2025 Nove</p>
            <div className="flex gap-8">
              <a href="#" className="hover:text-black transition-colors">Privacy</a>
              <a href="#" className="hover:text-black transition-colors">Terms</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
