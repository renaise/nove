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
          <div className="hidden md:flex items-center gap-1 absolute left-1/2 -translate-x-1/2">
            <a href="#about" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>About</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#for-brides" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>For Brides</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#boutiques" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>For Boutiques</a>
            <span className={`text-[8px] transition-colors duration-300 ${scrolled ? 'text-black/30' : 'text-[#FAFAFA]/30'}`}>·</span>
            <a href="#browse" className={`text-[10px] uppercase tracking-[0.12em] px-2 transition-colors duration-300 ${
              scrolled ? 'text-black/60 hover:text-black' : 'text-[#FAFAFA]/70 hover:text-[#FAFAFA]'
            }`}>Browse</a>
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
            <a href="#about" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black">About</a>
            <a href="#for-brides" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black">For Brides</a>
            <a href="#boutiques" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black">For Boutiques</a>
            <a href="#browse" onClick={() => setMobileMenuOpen(false)} className="text-sm uppercase tracking-[0.15em] text-black">Browse</a>
            <a href="#for-brides" onClick={() => setMobileMenuOpen(false)} className="mt-4 w-full py-3 border border-black text-black text-xs uppercase tracking-[0.15em] text-center">
              Start Trying on
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
        <div className="relative z-10 text-center px-6 max-w-2xl mx-auto mb-16 md:mb-24">
          <svg className="h-5 mx-auto mb-3 opacity-70" viewBox="0 0 47 17" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3.936 3.12H3.888V13.008C3.888 14.136 4.008 14.832 4.248 15.12C4.512 15.408 5.136 15.552 6.144 15.576V15.888H0.936V15.576C1.896 15.552 2.52 15.408 2.784 15.12C3.048 14.832 3.192 14.136 3.192 13.008V2.208C2.832 1.752 2.544 1.416 2.304 1.2C1.848 0.744 1.032 0.312 0 0.312V0H3.384L14.184 13.248H14.232V2.976C14.232 1.848 14.088 1.128 13.824 0.816001C13.56 0.504001 12.936 0.336001 11.976 0.312V0H17.184V0.312C16.248 0.336001 15.648 0.504001 15.36 0.816001C15.072 1.128 14.928 1.848 14.928 2.976V16.152H14.592L3.936 3.12Z" fill="white"/>
            <path d="M22.1897 4.824C23.4617 4.824 24.6137 5.352 25.5977 6.408C26.5817 7.44 27.0857 8.736 27.0857 10.272C27.0857 11.256 26.9177 12.192 26.5817 13.08C25.9097 14.808 24.3017 16.224 22.1657 16.224C20.8937 16.224 19.7657 15.672 18.7817 14.568C17.7977 13.464 17.2937 12.168 17.2937 10.656C17.2937 9 17.7737 7.632 18.7097 6.504C19.6457 5.376 20.8217 4.824 22.1897 4.824ZM21.9497 5.424C21.0617 5.424 20.3417 5.808 19.7417 6.6C19.1417 7.392 18.8537 8.424 18.8537 9.696C18.8537 11.4 19.1897 12.84 19.8857 13.968C20.5817 15.096 21.4937 15.648 22.5977 15.648C24.9497 15.648 25.5257 12.984 25.5257 11.304C25.5257 7.464 24.0377 5.424 21.9497 5.424Z" fill="white"/>
            <path d="M30.4978 7.44L33.1618 13.896L35.8498 7.416C36.0898 6.84 36.2098 6.408 36.2098 6.096C36.2098 5.64 35.9218 5.496 35.0578 5.472V5.16H38.2498V5.472C37.9378 5.472 37.6498 5.568 37.4098 5.76C36.9538 6.144 36.8578 6.432 36.5458 7.176L32.8498 16.224H32.5858L28.6978 6.792C28.2898 5.832 27.9058 5.544 26.9458 5.472V5.16H31.3858V5.472C30.5218 5.472 30.1378 5.616 30.1378 6.216C30.1378 6.432 30.2578 6.84 30.4978 7.44Z" fill="white"/>
            <path d="M46.986 9.216H39.33C39.33 12.888 40.89 14.904 43.122 14.904C44.874 14.904 46.05 13.848 46.65 11.76L46.914 11.904C46.698 13.128 46.218 14.136 45.474 14.976C44.73 15.816 43.794 16.224 42.69 16.224C41.346 16.224 40.242 15.696 39.378 14.664C38.538 13.632 38.106 12.288 38.106 10.656C38.106 7.08 40.002 4.824 42.906 4.824C44.13 4.824 45.114 5.232 45.858 6.048C46.602 6.864 46.986 7.92 46.986 9.216ZM39.354 8.616H45.162C45.186 6.672 44.058 5.448 42.402 5.448C41.658 5.448 40.962 5.76 40.362 6.36C39.762 6.96 39.426 7.704 39.354 8.616Z" fill="white"/>
          </svg>
          <h1 className="text-2xl md:text-3xl lg:text-4xl font-light leading-snug mb-4 tracking-[-0.02em] text-[#FAFAFA]">
            See the moment before it happens.
          </h1>
          <div className="flex flex-row gap-4 justify-center items-center">
            <button className="px-4 py-1.5 border border-[#FAFAFA] bg-transparent text-[#FAFAFA] text-[10px] uppercase tracking-[0.12em] hover:bg-[#FAFAFA] hover:text-black transition-all">
              Start Trying on
            </button>
            <a href="mailto:developer@codexfoundry.com" className="text-[#FAFAFA]/60 text-[10px] uppercase tracking-[0.12em] hover:text-[#FAFAFA] transition-all">
              Contact Us
            </a>
          </div>
        </div>
      </section>

      {/* --- ABOUT SECTION --- */}
      <section id="about" className="py-24 bg-white scroll-mt-20">
        <div className="max-w-5xl mx-auto px-6 lg:px-12">
          {/* Text */}
          <div className="text-center mb-16">
            <p className="text-xs uppercase tracking-[0.3em] text-black/50 mb-4">About</p>
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-light tracking-[-0.02em] mb-6 text-black">
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

      {/* --- FOR BRIDES SECTION --- */}
      <section id="for-brides" className="py-24 bg-[#F5F5F5] scroll-mt-20">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16">
            {/* Left - Steps */}
            <div className="space-y-8">
              <p className="text-xs uppercase tracking-[0.3em] text-black/50">For Brides</p>

              {/* Step 01 */}
              <div
                className={`border-t pt-6 cursor-pointer transition-all ${bridesStep >= 1 ? 'border-black/30' : 'border-black/10'}`}
                onClick={() => setBridesStep(1)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`text-xs mr-4 ${bridesStep >= 1 ? 'text-black' : 'text-black/40'}`}>01</span>
                    <span className={`text-lg ${bridesStep === 1 ? 'text-black' : 'text-black/50'}`}>The Silhouette Analysis</span>
                  </div>
                  <span className={`text-[10px] uppercase tracking-wider ${bridesStep >= 1 ? 'text-black/60' : 'text-black/40'}`}>Capture</span>
                </div>
                {bridesStep === 1 && (
                  <>
                    <p className="text-sm text-black/50 mb-4 pl-8">Upload a photo of yourself. Our AI analyzes your body shape to determine which silhouettes will flatter you most.</p>
                    <button
                      onClick={(e) => { e.stopPropagation(); setBridesStep(2); }}
                      className="ml-8 px-6 py-2 border border-black text-black text-[10px] uppercase tracking-wider hover:bg-black hover:text-white transition-all"
                    >
                      Begin Analysis
                    </button>
                  </>
                )}
              </div>

              {/* Step 02 */}
              <div
                className={`border-t pt-6 transition-all ${bridesStep >= 2 ? 'border-black/30 cursor-pointer' : 'border-black/10 opacity-50'}`}
                onClick={() => bridesStep >= 2 && setBridesStep(2)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`text-xs mr-4 ${bridesStep >= 2 ? 'text-black' : 'text-black/40'}`}>02</span>
                    <span className={`text-lg ${bridesStep === 2 ? 'text-black' : 'text-black/50'}`}>Silhouette Result</span>
                  </div>
                  <span className={`text-[10px] uppercase tracking-wider ${bridesStep >= 2 ? 'text-black/60' : 'text-black/40'}`}>Analyze</span>
                </div>
                {bridesStep === 2 && (
                  <div className="grid grid-cols-4 gap-2 pl-8">
                    {['A-line', 'Ball Gown', 'Mermaid', 'Sheath'].map((style) => (
                      <button
                        key={style}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedBridesSilhouette(style);
                          setTimeout(() => setBridesStep(3), 300);
                        }}
                        className={`py-3 border text-center text-[10px] uppercase tracking-wider transition-all ${
                          selectedBridesSilhouette === style
                            ? 'border-black bg-black text-white'
                            : 'border-black/20 text-black/50 hover:border-black hover:text-black'
                        }`}
                      >
                        {style}
                      </button>
                    ))}
                  </div>
                )}
                {bridesStep > 2 && selectedBridesSilhouette && (
                  <p className="text-sm text-black/50 pl-8">Selected: <span className="text-black">{selectedBridesSilhouette}</span></p>
                )}
              </div>

              {/* Step 03 */}
              <div
                className={`border-t pt-6 transition-all ${bridesStep >= 3 ? 'border-black/30 cursor-pointer' : 'border-black/10 opacity-50'}`}
                onClick={() => bridesStep >= 3 && setBridesStep(3)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`text-xs mr-4 ${bridesStep >= 3 ? 'text-black' : 'text-black/40'}`}>03</span>
                    <span className={`text-lg ${bridesStep === 3 ? 'text-black' : 'text-black/50'}`}>Refine the Aesthetic</span>
                  </div>
                  <span className={`text-[10px] uppercase tracking-wider ${bridesStep >= 3 ? 'text-black/60' : 'text-black/40'}`}>Style</span>
                </div>
                {bridesStep === 3 && (
                  <div className="grid grid-cols-2 gap-2 pl-8">
                    {['Minimalist', 'Romantic', 'Avant-Garde', 'Classic'].map((aesthetic) => (
                      <button
                        key={aesthetic}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedAesthetic(aesthetic);
                          setTimeout(() => setBridesStep(4), 300);
                        }}
                        className={`py-3 border text-center text-[10px] uppercase tracking-wider transition-all ${
                          selectedAesthetic === aesthetic
                            ? 'border-black bg-black text-white'
                            : 'border-black/20 text-black/50 hover:border-black hover:text-black'
                        }`}
                      >
                        {aesthetic}
                      </button>
                    ))}
                  </div>
                )}
                {bridesStep > 3 && selectedAesthetic && (
                  <p className="text-sm text-black/50 pl-8">Selected: <span className="text-black">{selectedAesthetic}</span></p>
                )}
              </div>

              {/* Step 04 */}
              <div
                className={`border-t pt-6 transition-all ${bridesStep >= 4 ? 'border-black/30' : 'border-black/10 opacity-50'}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`text-xs mr-4 ${bridesStep >= 4 ? 'text-black' : 'text-black/40'}`}>04</span>
                    <span className={`text-lg ${bridesStep === 4 ? 'text-black' : 'text-black/50'}`}>Curated Selection</span>
                  </div>
                  <span className={`text-[10px] uppercase tracking-wider ${bridesStep >= 4 ? 'text-black/60' : 'text-black/40'}`}>Result</span>
                </div>
                {bridesStep === 4 && (
                  <div className="pl-8">
                    <p className="text-sm text-black/50 mb-4">Based on your {selectedBridesSilhouette} silhouette and {selectedAesthetic} style preference, we've curated the perfect selection for you.</p>
                    <a
                      href="#browse"
                      className="inline-block px-6 py-2 bg-black text-white text-[10px] uppercase tracking-wider hover:bg-black/80 transition-all"
                    >
                      View Your Matches
                    </a>
                    <button
                      onClick={() => { setBridesStep(1); setSelectedBridesSilhouette(null); setSelectedAesthetic(null); }}
                      className="ml-4 px-6 py-2 border border-black/20 text-black/50 text-[10px] uppercase tracking-wider hover:border-black hover:text-black transition-all"
                    >
                      Start Over
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Right - Image Upload Preview */}
            <div className="relative">
              <div className="aspect-[3/4] bg-black/10 rounded-lg overflow-hidden relative">
                <img
                  src="/hero-bride.jpg"
                  alt="Bride preview"
                  className={`w-full h-full object-cover transition-opacity duration-500 ${bridesStep >= 2 ? 'opacity-100' : 'opacity-50'}`}
                />
                {bridesStep === 1 && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div
                      className="bg-white/90 backdrop-blur-sm rounded-lg px-6 py-4 text-center cursor-pointer hover:bg-white transition-all"
                      onClick={() => setBridesStep(2)}
                    >
                      <p className="text-sm text-black mb-1">Upload Image</p>
                      <p className="text-xs text-black/50">Drag and Drop or Click to Browse</p>
                    </div>
                  </div>
                )}
                {bridesStep === 4 && (
                  <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-3">
                    <p className="text-[10px] uppercase tracking-wider text-black/60 mb-1">Your Perfect Match</p>
                    <p className="text-sm text-black">{selectedBridesSilhouette} · {selectedAesthetic}</p>
                  </div>
                )}
              </div>
              {/* Progress indicator */}
              <div className="flex justify-center gap-2 mt-4">
                {[1, 2, 3, 4].map((step) => (
                  <div
                    key={step}
                    className={`h-1 rounded-full transition-all ${
                      step <= bridesStep ? 'w-8 bg-black' : 'w-2 bg-black/20'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* --- BROWSE / MARKETPLACE SECTION --- */}
      <section id="browse" className="py-16 bg-white scroll-mt-20">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          {/* Header */}
          <div className="text-center mb-12">
            <p className="text-[10px] uppercase tracking-[0.15em] text-black/50 mb-3 font-light">Browse</p>
            <h2 className="text-3xl md:text-4xl font-light tracking-[-0.02em] mb-4 text-black">
              Find Your Dream Dress
            </h2>
            <p className="text-black/50 max-w-xl mx-auto">
              Browse thousands of wedding dresses from top designers. Try them on virtually before you buy.
            </p>
          </div>

          {/* Filters */}
          <div className="overflow-x-auto pb-2 mb-4 -mx-6 px-6 md:overflow-visible md:mx-0 md:px-0">
            <div className="flex gap-2 justify-start md:justify-center md:flex-wrap min-w-max md:min-w-0">
              {silhouetteFilters.map((filter) => (
                <button
                  key={filter}
                  onClick={() => setSelectedSilhouette(filter)}
                  className={`px-3 md:px-4 py-1.5 text-[10px] uppercase tracking-[0.1em] border transition-all whitespace-nowrap ${
                    selectedSilhouette === filter
                      ? 'bg-black text-white border-black'
                      : 'bg-transparent text-black/50 border-black/20 hover:border-black hover:text-black'
                  }`}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div className="overflow-x-auto pb-2 mb-10 -mx-6 px-6 md:overflow-visible md:mx-0 md:px-0">
            <div className="flex gap-2 justify-start md:justify-center md:flex-wrap min-w-max md:min-w-0">
              {priceFilters.map((price, index) => (
                <button
                  key={price.label}
                  onClick={() => setSelectedPriceIndex(index)}
                  className={`px-3 py-1 text-[10px] border transition-all whitespace-nowrap ${
                    selectedPriceIndex === index
                      ? 'bg-black text-white border-black'
                      : 'text-black/50 border-black/20 hover:border-black hover:text-black'
                  }`}
                >
                  {price.label}
                </button>
              ))}
            </div>
          </div>

          {/* Dress Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
            {filteredDresses.length > 0 ? filteredDresses.map((dress, index) => (
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
            )) : (
              <div className="col-span-full text-center py-16">
                <p className="text-black/50 text-lg">No dresses match your filters.</p>
                <button
                  onClick={() => { setSelectedSilhouette('All'); setSelectedPriceIndex(0); }}
                  className="mt-4 text-sm text-black/50 underline hover:text-black transition-colors"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>

          {/* View All Button */}
          <div className="text-center mt-12">
            <a
              href="https://www.stillwhite.com/dresses"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-10 py-4 border border-black text-black text-xs uppercase tracking-[0.15em] hover:bg-black hover:text-white transition-all"
            >
              View All Dresses
            </a>
          </div>
        </div>
      </section>

      {/* --- FOR BOUTIQUES SECTION --- */}
      <section id="boutiques" className="py-24 bg-black scroll-mt-20">
        <div className="max-w-3xl mx-auto px-6 lg:px-12 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-[#FAFAFA]/50 mb-4">for Boutiques</p>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-light tracking-[-0.02em] mb-6 text-[#FAFAFA]">
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

      {/* --- MARQUEE SECTION --- */}
      <section className="py-6 bg-white border-t border-b border-black/10 overflow-hidden">
        <div className="relative">
          <div className="flex animate-marquee whitespace-nowrap">
            {[...Array(8)].map((_, i) => (
              <span key={i} className="mx-8 text-sm uppercase tracking-[0.2em] text-black/60">
                Follow us on Instagram
                <span className="mx-8 text-black/30">·</span>
                @nove.bridal
                <span className="mx-8 text-black/30">·</span>
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="py-16 bg-black text-[#FAFAFA]">
        <div className="max-w-6xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8 mb-12">
            <svg className="h-5" viewBox="0 0 47 17" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3.936 3.12H3.888V13.008C3.888 14.136 4.008 14.832 4.248 15.12C4.512 15.408 5.136 15.552 6.144 15.576V15.888H0.936V15.576C1.896 15.552 2.52 15.408 2.784 15.12C3.048 14.832 3.192 14.136 3.192 13.008V2.208C2.832 1.752 2.544 1.416 2.304 1.2C1.848 0.744 1.032 0.312 0 0.312V0H3.384L14.184 13.248H14.232V2.976C14.232 1.848 14.088 1.128 13.824 0.816001C13.56 0.504001 12.936 0.336001 11.976 0.312V0H17.184V0.312C16.248 0.336001 15.648 0.504001 15.36 0.816001C15.072 1.128 14.928 1.848 14.928 2.976V16.152H14.592L3.936 3.12Z" fill="white"/>
              <path d="M22.1897 4.824C23.4617 4.824 24.6137 5.352 25.5977 6.408C26.5817 7.44 27.0857 8.736 27.0857 10.272C27.0857 11.256 26.9177 12.192 26.5817 13.08C25.9097 14.808 24.3017 16.224 22.1657 16.224C20.8937 16.224 19.7657 15.672 18.7817 14.568C17.7977 13.464 17.2937 12.168 17.2937 10.656C17.2937 9 17.7737 7.632 18.7097 6.504C19.6457 5.376 20.8217 4.824 22.1897 4.824ZM21.9497 5.424C21.0617 5.424 20.3417 5.808 19.7417 6.6C19.1417 7.392 18.8537 8.424 18.8537 9.696C18.8537 11.4 19.1897 12.84 19.8857 13.968C20.5817 15.096 21.4937 15.648 22.5977 15.648C24.9497 15.648 25.5257 12.984 25.5257 11.304C25.5257 7.464 24.0377 5.424 21.9497 5.424Z" fill="white"/>
              <path d="M30.4978 7.44L33.1618 13.896L35.8498 7.416C36.0898 6.84 36.2098 6.408 36.2098 6.096C36.2098 5.64 35.9218 5.496 35.0578 5.472V5.16H38.2498V5.472C37.9378 5.472 37.6498 5.568 37.4098 5.76C36.9538 6.144 36.8578 6.432 36.5458 7.176L32.8498 16.224H32.5858L28.6978 6.792C28.2898 5.832 27.9058 5.544 26.9458 5.472V5.16H31.3858V5.472C30.5218 5.472 30.1378 5.616 30.1378 6.216C30.1378 6.432 30.2578 6.84 30.4978 7.44Z" fill="white"/>
              <path d="M46.986 9.216H39.33C39.33 12.888 40.89 14.904 43.122 14.904C44.874 14.904 46.05 13.848 46.65 11.76L46.914 11.904C46.698 13.128 46.218 14.136 45.474 14.976C44.73 15.816 43.794 16.224 42.69 16.224C41.346 16.224 40.242 15.696 39.378 14.664C38.538 13.632 38.106 12.288 38.106 10.656C38.106 7.08 40.002 4.824 42.906 4.824C44.13 4.824 45.114 5.232 45.858 6.048C46.602 6.864 46.986 7.92 46.986 9.216ZM39.354 8.616H45.162C45.186 6.672 44.058 5.448 42.402 5.448C41.658 5.448 40.962 5.76 40.362 6.36C39.762 6.96 39.426 7.704 39.354 8.616Z" fill="white"/>
            </svg>
            <div className="flex gap-8 text-xs uppercase tracking-[0.15em]">
              <a href="#about" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">About</a>
              <a href="#for-brides" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">For Brides</a>
              <a href="#boutiques" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">For Boutiques</a>
              <a href="#browse" className="text-[#FAFAFA]/70 hover:text-[#FAFAFA] transition-colors">Browse</a>
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
