import { useApp } from '../context/AppContext.jsx';
import { DressIcon, HeartIcon } from '../components/Icons.jsx';

const HomeScreen = () => {
  const { navigateTo, state } = useApp();

  const handleTryOnPress = () => {
    navigateTo('marketplace');
  };

  return (
    <view className="flex-1 w-full pt-[60px] pb-10 px-5 App">
      {/* Header */}
      <view className="items-center mb-8">
        <text className="text-[36px] font-bold text-gold mb-1 font-serif italic">
          Novia
        </text>
        <text className="text-base text-muted-foreground text-center" style={{ lineHeight: '22px' }}>
          Your joyful discovery starts here
        </text>
      </view>

      {/* Welcome Message */}
      {state.user && (
        <view className="mb-6">
          <text className="text-lg text-foreground text-center">
            Welcome back, {state.user.name?.split(' ')[0] || 'Love'} 💕
          </text>
        </view>
      )}

      {/* Main CTA - Virtual Try-On */}
      <novia-liquid-glass
        glassStyle="clear"
        tintColor="#FFFFFF"
        tintAlpha={0.2}
        cornerRadius={24}
        addBorder={true}
        bindtap={handleTryOnPress}
        className="mb-5 p-6 w-full"
      >
        <view className="w-full h-[180px] bg-blush rounded-xl mb-4 items-center justify-center">
          <DressIcon size={64} color="#D4AF37" />
        </view>

        <text className="text-xl font-semibold text-foreground mb-2">
          Find Your "Yes" Dress
        </text>

        <text className="text-sm text-muted-foreground mb-4" style={{ lineHeight: '20px' }}>
          See yourself in stunning wedding dresses, effortlessly. Try on 50+ looks in minutes.
        </text>

        <view className="bg-gold py-3 px-6 rounded-xl items-center flex-row justify-center">
          <HeartIcon size={18} color="#FFFFFF" />
          <text className="text-white font-semibold text-base ml-2">
            Start Your Joyful Discovery
          </text>
        </view>
      </novia-liquid-glass>

      {/* Stats/Social Proof */}
      <view style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginBottom: '24px' }}>
        <view style={{ display: 'flex', flexDirection: 'row' }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <text key={i} className="text-gold">★</text>
          ))}
        </view>
        <text className="text-sm text-muted-foreground ml-2">
          47 Dresses Tested. 1 Dream Found.
        </text>
      </view>

      {/* Coming Soon Features */}
      <view className="mb-4">
        <text className="text-xs text-gold font-bold tracking-widest uppercase mb-3 text-center">
          Coming Soon
        </text>
      </view>

      <scroll-view scroll-x={true} className="flex-row w-full" style={{ gap: '12px' }}>
        {[
          { icon: '✨', name: 'Veils' },
          { icon: '👑', name: 'Tiaras' },
          { icon: '💎', name: 'Jewelry' },
          { icon: '💐', name: 'Bouquets' },
        ].map((item) => (
          <novia-liquid-glass
            key={item.name}
            glassStyle="clear"
            cornerRadius={16}
            addBorder={true}
            className="w-[100px] p-4 items-center mr-3"
          >
            <text className="text-2xl mb-2">{item.icon}</text>
            <text className="text-xs font-semibold text-foreground">
              {item.name}
            </text>
          </novia-liquid-glass>
        ))}
      </scroll-view>

      {/* Privacy Note */}
      <view className="mt-6 items-center">
        <text className="text-xs text-muted-foreground text-center">
          🔒 Your photos are strictly private and never shared
        </text>
      </view>
    </view>
  );
};

export default HomeScreen;
