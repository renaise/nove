import { useState } from '@lynx-js/react';
import { useApp } from '../context/AppContext.jsx';
import { BackIcon, HeartIcon } from '../components/Icons.jsx';

// This should match the DRESSES array in DressMarketplaceScreen
// In production, this would come from a shared data source
const DRESSES: Record<string, { name: string; category: string; price: string; image: string }> = {
  '1': { name: 'Enchanted Garden', category: 'ballgown', price: '$2,800', image: 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=600&q=80' },
  '2': { name: 'Modern Romance', category: 'aline', price: '$1,950', image: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=600&q=80' },
  '3': { name: 'Ocean Breeze', category: 'bohemian', price: '$1,400', image: 'https://images.unsplash.com/photo-1522653216850-4f1415a174fb?w=600&q=80' },
  '4': { name: 'Royal Elegance', category: 'ballgown', price: '$4,200', image: 'https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=600&q=80' },
  '5': { name: 'Sleek Silhouette', category: 'mermaid', price: '$2,100', image: 'https://images.unsplash.com/photo-1550005809-91ad75fb315f?w=600&q=80' },
  '6': { name: 'Timeless Classic', category: 'sheath', price: '$1,650', image: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80' },
  '7': { name: 'Fairy Tale Dream', category: 'ballgown', price: '$3,500', image: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&q=80' },
  '8': { name: 'Boho Chic', category: 'bohemian', price: '$1,250', image: 'https://images.unsplash.com/photo-1525257944581-1bcb36a54be3?w=600&q=80' },
  '9': { name: 'Sculpted Beauty', category: 'mermaid', price: '$2,400', image: 'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=600&q=80' },
  '10': { name: 'Graceful Flow', category: 'aline', price: '$1,800', image: 'https://images.unsplash.com/photo-1518889735218-3e3c81fc4906?w=600&q=80' },
  '11': { name: 'Minimalist Bride', category: 'sheath', price: '$1,350', image: 'https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=600&q=80' },
  '12': { name: 'Romantic Lace', category: 'aline', price: '$2,200', image: 'https://images.unsplash.com/photo-1549416853-67360aed1e10?w=600&q=80' },
};

const TryOnScreen = () => {
  const { goBack, state, navigateTo } = useApp();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const selectedDress = state.selectedDress ? DRESSES[state.selectedDress] : null;

  const handleBackPress = () => {
    goBack();
  };

  const handleFavoriteToggle = () => {
    setIsFavorite(!isFavorite);
  };

  const handleGenerateTryOn = async () => {
    if (!state.selectedPhoto || !state.selectedDress) return;

    setIsGenerating(true);
    console.log('[TryOnScreen] Generating try-on with:', {
      photo: state.selectedPhoto,
      dress: state.selectedDress,
    });

    // TODO: Call AI try-on API here (e.g., Nano Banana Pro)
    // For now, simulate a delay
    setTimeout(() => {
      setIsGenerating(false);
      navigateTo('results');
    }, 3000);
  };

  if (!selectedDress) {
    return (
      <view className="flex-1 w-full bg-ivory items-center justify-center">
        <text className="text-muted-foreground">No dress selected</text>
        <view
          bindtap={() => navigateTo('marketplace')}
          className="mt-4 bg-gold py-3 px-6 rounded-xl"
        >
          <text className="text-white font-semibold">Browse Dresses</text>
        </view>
      </view>
    );
  }

  return (
    <view className="flex-1 w-full bg-ivory">
      {/* Full-screen dress image */}
      <view className="absolute top-0 left-0 right-0 bottom-0">
        <image
          src={selectedDress.image}
          className="w-full h-full"
          mode="aspectFill"
        />
        {/* Gradient overlay for readability */}
        <view
          className="absolute bottom-0 left-0 right-0 h-[300px]"
          style={{
            background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
          }}
        />
      </view>

      {/* Header */}
      <view className="absolute top-0 left-0 right-0 flex-row items-center justify-between pt-[60px] px-5">
        <view
          bindtap={handleBackPress}
          className="w-10 h-10 rounded-full items-center justify-center"
          style={{ backgroundColor: 'rgba(255,255,255,0.9)' }}
        >
          <BackIcon size={24} color="#2D2D2D" />
        </view>
        <view
          bindtap={handleFavoriteToggle}
          className="w-10 h-10 rounded-full items-center justify-center"
          style={{ backgroundColor: isFavorite ? '#D4AF37' : 'rgba(255,255,255,0.9)' }}
        >
          <HeartIcon size={20} color={isFavorite ? '#FFFFFF' : '#D4AF37'} />
        </view>
      </view>

      {/* Bottom Content */}
      <view className="absolute bottom-0 left-0 right-0 px-5 pb-10">
        {/* Dress Info */}
        <view className="mb-6">
          <text className="text-3xl font-bold text-white mb-1">
            {selectedDress.name}
          </text>
          <view className="flex-row items-center">
            <text className="text-base text-white/80 capitalize mr-3">
              {selectedDress.category}
            </text>
            <text className="text-xl font-bold text-gold">
              {selectedDress.price}
            </text>
          </view>
        </view>

        {/* Your Photo Preview */}
        {state.selectedPhoto && (
          <novia-liquid-glass
            glassStyle="regular"
            tintColor="#FFFFFF"
            tintAlpha={0.2}
            cornerRadius={16}
            addBorder={false}
            className="flex-row items-center p-3 mb-4"
          >
            <view className="w-14 h-14 rounded-xl overflow-hidden mr-3">
              <image
                src={state.selectedPhoto}
                className="w-full h-full"
                mode="aspectFill"
              />
            </view>
            <view className="flex-1">
              <text className="text-sm font-semibold text-white">
                Your silhouette photo
              </text>
              <text className="text-xs text-white/70">
                Ready for virtual try-on
              </text>
            </view>
            <view className="w-3 h-3 rounded-full bg-green-400" />
          </novia-liquid-glass>
        )}

        {/* Generate Button */}
        <view
          bindtap={isGenerating ? undefined : handleGenerateTryOn}
          className="py-4 rounded-2xl items-center flex-row justify-center"
          style={{
            backgroundColor: isGenerating ? '#E5E5E5' : '#D4AF37',
            opacity: isGenerating ? 0.8 : 1,
          }}
        >
          {isGenerating ? (
            <text className="text-muted-foreground font-semibold text-lg">
              Creating your moment...
            </text>
          ) : (
            <>
              <HeartIcon size={20} color="#FFFFFF" />
              <text className="text-white font-semibold text-lg ml-2">
                Try This Dress On Me
              </text>
            </>
          )}
        </view>

        {/* Privacy Note */}
        <view className="mt-4 items-center">
          <text className="text-xs text-white/60 text-center">
            Your photos are processed securely and never shared
          </text>
        </view>
      </view>
    </view>
  );
};

export default TryOnScreen;
