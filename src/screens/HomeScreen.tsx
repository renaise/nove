import { useApp } from '../context/AppContext.jsx';
import { DressIcon, HeartIcon } from '../components/Icons.jsx';

const HomeScreen = () => {
  const { navigateTo, state } = useApp();

  const handleTryOnPress = () => {
    navigateTo('marketplace');
  };

  return (
    <view className="flex-1 w-full pt-[70px] pb-10 px-6 App">
      {/* Header */}
      <view className="items-center mb-10">
        <text className="text-[40px] font-bold text-foreground mb-2">
          Novia
        </text>
        {state.user && (
          <text className="text-base text-muted-foreground">
            Welcome back, {state.user.name?.split(' ')[0] || 'there'}
          </text>
        )}
      </view>

      {/* Main CTA - Virtual Try-On */}
      <view
        bindtap={handleTryOnPress}
        className="mb-6 p-6 w-full bg-card rounded-3xl"
        style={{
          boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.05), 0 4px 6px -4px rgb(0 0 0 / 0.05)',
        }}
      >
        <view className="w-full h-[200px] bg-blush rounded-2xl mb-5 items-center justify-center">
          <DressIcon size={72} color="#E6B88A" />
        </view>

        <text className="text-2xl font-semibold text-foreground mb-3">
          Find Your Dream Dress
        </text>

        <text className="text-sm text-muted-foreground mb-6" style={{ lineHeight: '22px' }}>
          See yourself in stunning wedding dresses. Try on dozens of looks in minutes.
        </text>

        <view className="bg-primary py-4 px-6 rounded-2xl items-center">
          <text className="text-white font-semibold text-base">
            Start Browsing
          </text>
        </view>
      </view>

      {/* Stats/Social Proof */}
      <view className="flex-row items-center justify-center mb-8">
        <view className="flex-row mr-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <text key={i} style={{ fontSize: '14px', color: '#E6B88A' }}>★</text>
          ))}
        </view>
        <text className="text-sm text-muted-foreground">
          Loved by thousands of brides
        </text>
      </view>

      {/* Coming Soon Features */}
      <view className="mb-4">
        <text className="text-xs text-muted-foreground font-medium uppercase tracking-wider mb-4">
          Coming Soon
        </text>
      </view>

      <scroll-view scroll-x={true} className="flex-row w-full" style={{ gap: '16px' }}>
        {[
          { icon: '✨', name: 'Veils' },
          { icon: '👑', name: 'Tiaras' },
          { icon: '💎', name: 'Jewelry' },
          { icon: '💐', name: 'Bouquets' },
        ].map((item) => (
          <view
            key={item.name}
            className="bg-card rounded-2xl p-5 items-center"
            style={{
              width: '110px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)',
            }}
          >
            <text style={{ fontSize: '32px', marginBottom: '8px' }}>{item.icon}</text>
            <text className="text-xs font-medium text-foreground">
              {item.name}
            </text>
          </view>
        ))}
      </scroll-view>

      {/* Privacy Note */}
      <view className="mt-8 items-center">
        <text className="text-xs text-muted-foreground text-center">
          Your photos are private and secure
        </text>
      </view>
    </view>
  );
};

export default HomeScreen;
