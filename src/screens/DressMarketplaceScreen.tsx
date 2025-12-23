import { useState, useRef } from '@lynx-js/react';
import { useApp } from '../context/AppContext.jsx';
import { BackIcon, HeartIcon } from '../components/Icons.jsx';

// Wedding dress categories
const CATEGORIES = [
  { id: 'all', name: 'All Styles' },
  { id: 'ballgown', name: 'Ball Gown' },
  { id: 'aline', name: 'A-Line' },
  { id: 'mermaid', name: 'Mermaid' },
  { id: 'sheath', name: 'Sheath' },
  { id: 'bohemian', name: 'Bohemian' },
] as const;

type CategoryId = (typeof CATEGORIES)[number]['id'];

// Sample dress data - in production this would come from an API
const DRESSES = [
  {
    id: '1',
    name: 'Enchanted Garden',
    category: 'ballgown',
    price: '$2,800',
    image: 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=400&q=80',
    height: 280,
  },
  {
    id: '2',
    name: 'Modern Romance',
    category: 'aline',
    price: '$1,950',
    image: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=400&q=80',
    height: 320,
  },
  {
    id: '3',
    name: 'Ocean Breeze',
    category: 'bohemian',
    price: '$1,400',
    image: 'https://images.unsplash.com/photo-1522653216850-4f1415a174fb?w=400&q=80',
    height: 260,
  },
  {
    id: '4',
    name: 'Royal Elegance',
    category: 'ballgown',
    price: '$4,200',
    image: 'https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=400&q=80',
    height: 340,
  },
  {
    id: '5',
    name: 'Sleek Silhouette',
    category: 'mermaid',
    price: '$2,100',
    image: 'https://images.unsplash.com/photo-1550005809-91ad75fb315f?w=400&q=80',
    height: 300,
  },
  {
    id: '6',
    name: 'Timeless Classic',
    category: 'sheath',
    price: '$1,650',
    image: 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=400&q=80',
    height: 290,
  },
  {
    id: '7',
    name: 'Fairy Tale Dream',
    category: 'ballgown',
    price: '$3,500',
    image: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=400&q=80',
    height: 310,
  },
  {
    id: '8',
    name: 'Boho Chic',
    category: 'bohemian',
    price: '$1,250',
    image: 'https://images.unsplash.com/photo-1525257944581-1bcb36a54be3?w=400&q=80',
    height: 270,
  },
  {
    id: '9',
    name: 'Sculpted Beauty',
    category: 'mermaid',
    price: '$2,400',
    image: 'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=400&q=80',
    height: 330,
  },
  {
    id: '10',
    name: 'Graceful Flow',
    category: 'aline',
    price: '$1,800',
    image: 'https://images.unsplash.com/photo-1518889735218-3e3c81fc4906?w=400&q=80',
    height: 285,
  },
  {
    id: '11',
    name: 'Minimalist Bride',
    category: 'sheath',
    price: '$1,350',
    image: 'https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=400&q=80',
    height: 295,
  },
  {
    id: '12',
    name: 'Romantic Lace',
    category: 'aline',
    price: '$2,200',
    image: 'https://images.unsplash.com/photo-1549416853-67360aed1e10?w=400&q=80',
    height: 315,
  },
];

const DressMarketplaceScreen = () => {
  const { goBack, setSelectedDress, navigateTo, state } = useApp();
  const [selectedCategory, setSelectedCategory] = useState<CategoryId>('all');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const listRef = useRef(null);

  const handleBackPress = () => {
    goBack();
  };

  const handleCategorySelect = (categoryId: CategoryId) => {
    setSelectedCategory(categoryId);
  };

  const handleDressSelect = (dressId: string) => {
    setSelectedDress(dressId);
    navigateTo('tryon');
  };

  const handleFavoriteToggle = (dressId: string, e: any) => {
    e.stopPropagation?.();
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(dressId)) {
        next.delete(dressId);
      } else {
        next.add(dressId);
      }
      return next;
    });
  };

  // Filter dresses by category
  const filteredDresses =
    selectedCategory === 'all'
      ? DRESSES
      : DRESSES.filter((d) => d.category === selectedCategory);

  return (
    <view className="flex-1 w-full bg-ivory">
      {/* Header */}
      <novia-liquid-glass
        glassStyle="clear"
        tintColor="#FFFFFF"
        tintAlpha={0.8}
        addBorder={false}
        className="pt-[60px] pb-3 px-5"
      >
        <view className="flex-row items-center mb-4">
          <view bindtap={handleBackPress} className="p-2 mr-2">
            <BackIcon size={24} color="#2D2D2D" />
          </view>
          <view className="flex-1">
            <text className="text-2xl font-bold text-foreground">
              Wedding Dresses
            </text>
            <text className="text-sm text-muted-foreground">
              {filteredDresses.length} styles to discover
            </text>
          </view>
        </view>

        {/* Category Filters */}
        <scroll-view scroll-x={true} className="flex-row" style={{ marginLeft: '-20px', marginRight: '-20px', paddingLeft: '20px', paddingRight: '20px' }}>
          {CATEGORIES.map((category) => (
            <view
              key={category.id}
              bindtap={() => handleCategorySelect(category.id)}
              className="mr-2 px-4 py-2 rounded-full"
              style={{
                backgroundColor: selectedCategory === category.id ? '#D4AF37' : '#F8E8E8',
              }}
            >
              <text
                className="text-sm font-medium"
                style={{
                  color: selectedCategory === category.id ? '#FFFFFF' : '#2D2D2D',
                }}
              >
                {category.name}
              </text>
            </view>
          ))}
        </scroll-view>
      </novia-liquid-glass>

      {/* Dress Grid - Waterfall Layout */}
      <list
        ref={listRef}
        list-type="waterfall"
        span-count={2}
        scroll-orientation="vertical"
        style={{
          width: '100%',
          height: '80vh',
          paddingLeft: '12px',
          paddingRight: '12px',
          paddingTop: '12px',
          paddingBottom: state.selectedPhoto ? '100px' : '20px',
          listMainAxisGap: '12px',
          listCrossAxisGap: '12px',
        } as any}
      >
        {filteredDresses.map((dress, index) => (
          <list-item
            key={dress.id}
            item-key={dress.id}
            estimated-main-axis-size-px={dress.height + 80}
          >
            <view
              bindtap={() => handleDressSelect(dress.id)}
              className="bg-white rounded-2xl overflow-hidden"
            >
              {/* Dress Image */}
              <view
                className="w-full bg-blush overflow-hidden"
                style={{ height: `${dress.height}px` }}
              >
                <image
                  src={dress.image}
                  className="w-full h-full"
                  mode="aspectFill"
                />
                {/* Favorite Button */}
                <view
                  bindtap={(e: any) => handleFavoriteToggle(dress.id, e)}
                  className="absolute top-2 right-2 w-9 h-9 rounded-full items-center justify-center"
                  style={{
                    backgroundColor: favorites.has(dress.id) ? '#D4AF37' : 'rgba(255,255,255,0.9)',
                  }}
                >
                  <HeartIcon
                    size={18}
                    color={favorites.has(dress.id) ? '#FFFFFF' : '#D4AF37'}
                  />
                </view>
              </view>

              {/* Dress Info */}
              <view className="p-3">
                <text
                  className="text-sm font-semibold text-foreground mb-1"
                  style={{ lineHeight: '18px' }}
                >
                  {dress.name}
                </text>
                <text className="text-xs text-muted-foreground capitalize">
                  {dress.category}
                </text>
                <text className="text-sm font-bold text-gold mt-1">
                  {dress.price}
                </text>
              </view>
            </view>
          </list-item>
        ))}
      </list>

      {/* Selected Photo Indicator */}
      {state.selectedPhoto && (
        <view className="absolute bottom-6 left-5 right-5">
          <novia-liquid-glass
            glassStyle="regular"
            tintColor="#D4AF37"
            tintAlpha={0.9}
            cornerRadius={16}
            addBorder={false}
            className="flex-row items-center p-3"
          >
            <view className="w-12 h-12 rounded-lg overflow-hidden mr-3">
              <image
                src={state.selectedPhoto}
                className="w-full h-full"
                mode="aspectFill"
              />
            </view>
            <view className="flex-1">
              <text className="text-sm font-semibold text-white">
                Your photo is ready
              </text>
              <text className="text-xs text-white/80">
                Tap any dress to try it on
              </text>
            </view>
          </novia-liquid-glass>
        </view>
      )}
    </view>
  );
};

export default DressMarketplaceScreen;
