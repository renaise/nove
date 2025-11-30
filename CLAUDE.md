# CLAUDE.md - Novia Project Specification

## What is Novia?

**Novia** is an AI-powered mobile app to help brides visualize their wedding day. The name combines "bride" (novia in Spanish) with the essence of new life (nova). The MVP feature is **Virtual Try-On** - allowing brides to see themselves in different wedding dresses using AI models like Nano Banana Pro.

## Critical Framework: Lynx.js

**CRITICAL**: This is a **Lynx.js** project from ByteDance, NOT React or React Native.

### Lynx.js Essentials
- **Docs**: https://lynxjs.org
- **Version**: 3.4.1-dev (iOS)
- **JSX Support**: Yes, via `pluginReactLynx()` in `lynx.config.ts`
- **Event Handling**: `bindtap` (NOT `onPress`/`onClick`)
  ```tsx
  <view bindtap={handleTap}>Tap me</view>
  ```
- **Styling**: Inline JavaScript objects, standard CSS properties only
  - Use: `paddingTop`, `paddingBottom`, `paddingLeft`, `paddingRight`
  - NO: `paddingVertical`, `paddingHorizontal` (React Native shortcuts)

## Project Structure

```
novia/
├── src/                    # TypeScript source
│   ├── index.tsx           # App entry point
│   ├── App.tsx             # Root component
│   ├── App.css             # Global styles
│   ├── screens/            # Main app screens
│   │   ├── HomeScreen.tsx
│   │   └── TryOnScreen.tsx # MVP try-on feature
│   ├── components/
│   │   └── AppContent.tsx  # Screen router
│   ├── context/
│   │   └── AppContext.tsx  # Global state management
│   ├── types/
│   │   ├── jsx.d.ts        # Custom Lynx component types
│   │   └── native-modules.d.ts
│   ├── services/           # API/business logic
│   ├── utils/              # Utilities
│   └── assets/             # Images, fonts
├── ios/
│   └── Novia/              # Xcode project root
│       ├── Podfile         # CocoaPods dependencies
│       ├── Novia.xcworkspace
│       ├── Novia.xcodeproj
│       └── Novia/          # Native modules & components
│           ├── AppDelegate.m/h
│           ├── ViewController.m/h
│           ├── LynxInitProcessor.m/h
│           ├── *Provider.m/h   # Lynx providers
│           └── *Module.m/h     # Native modules
├── lynx.config.ts          # LynxJS build configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.ts      # Tailwind CSS configuration
└── package.json            # Node dependencies
```

## Technology Stack

- **Framework**: Lynx.js 3.4.1-dev
- **Language**: TypeScript 5.8.3
- **Build**: RSBuild/RSpeedy
- **iOS Native**: Swift 6.0 + Objective-C
- **iOS Min Version**: 16.0
- **Styling**: Tailwind CSS (Lynx preset)

## MVP Feature: Virtual Try-On

The north star feature allows brides to:
1. Upload a photo of themselves
2. Select a wedding dress from the catalog
3. AI generates a try-on image using models like Nano Banana Pro
4. View and save results

### Future Features
- Venue visualization
- Photo styling (lighting, staging)
- Video style preview

## Commands

```bash
# Development
npm run dev          # Start dev server with HMR
npm run dev:direct   # Direct dev server (no script wrapper)
npm run build        # Production build
npm run postbuild    # Copy dist to iOS bundle

# iOS
npm run ios:pods     # Install CocoaPods (in ios/Novia)
npm run ios:open     # Open Xcode workspace
npm run ios:clean    # Clean Xcode build

# Linting
npm run lint         # Run ESLint
npm run format       # Format with Prettier
```

## Development Setup

### First Time Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Install pods:**
   ```bash
   npm run ios:pods
   # or: cd ios/Novia && pod install
   ```

3. **Build JS bundle:**
   ```bash
   npm run build
   ```

4. **Open workspace:**
   ```bash
   npm run ios:open
   # Opens ios/Novia/Novia.xcworkspace
   ```

5. **Add native files to Xcode:**
   - In Xcode, add all .h/.m files from `ios/Novia/Novia/` to the project
   - Set bridging header: `$(SRCROOT)/Novia/Novia-Bridging-Header.h`

### Development Workflow

1. Start dev server:
   ```bash
   npm run dev
   ```

2. Build and run in Xcode (⌘R)

3. Hot reload on save for TypeScript changes

### Debugging

Use `NativeModules.ConsoleLynxProvider.logToConsole()` for ALL logging:

```typescript
// Correct - Will show in dev console
NativeModules.ConsoleLynxProvider?.logToConsole('Debug message');

// Wrong - Won't show in mobile dev mode
console.log('This will not appear');
```

## Styling & Design

### Wedding Theme Colors
```typescript
const COLORS = {
  ivory: '#FFFFF0',      // Background
  gold: '#D4AF37',       // Primary/CTA
  blush: '#F8E8E8',      // Secondary
  rose: '#E8B4B8',       // Accent
  champagne: '#F7E7CE',  // Highlights
  text: '#2D2D2D',       // Dark text
  muted: '#737373',      // Muted text
};
```

## Lynx.js CSS Guide

**CRITICAL**: Lynx.js is NOT React Native. CSS works differently!

### Primary Approach: Tailwind `className`

Use Tailwind utility classes as the **primary** styling method:

```tsx
// ✅ CORRECT - Use className with Tailwind utilities
<view className="flex-1 w-full pt-[60px] pb-10 px-5 bg-ivory">
  <text className="text-[32px] font-bold text-gold mb-2">Title</text>
</view>

// ❌ WRONG - Verbose inline styles
<view style={{ flex: 1, width: '100%', paddingTop: '60px', ... }}>
```

### When to Use Inline `style`

Only use inline `style` for:
1. **Dynamic values** (computed at runtime)
2. **Non-standard properties** not in Tailwind
3. **Properties requiring `px` units** that Tailwind doesn't handle well

```tsx
// Dynamic values - must use style
<view style={{ opacity: isActive ? 1 : 0.5 }}>
<view style={{ backgroundColor: selected ? '#D4AF37' : '#E5E5E5' }}>

// Non-standard properties
<view style={{ aspectRatio: 0.75 }}>
<view style={{ gap: '12px' }}>
<text style={{ lineHeight: '20px' }}>
```

### CSS Value Rules

**ALL numeric values in inline styles MUST have `px` units as strings:**

```tsx
// ✅ CORRECT
style={{ fontSize: '24px' }}
style={{ gap: '12px' }}
style={{ lineHeight: '20px' }}

// ❌ WRONG - Numbers without units
style={{ fontSize: 24 }}
style={{ gap: 12 }}
```

**Exceptions (unitless values):**
- `opacity: 0.5` - always 0-1
- `aspectRatio: 0.75` - ratio value
- `flex: 1` - flex grow value
- `zIndex: 10` - integer

### Properties NOT Supported

```tsx
// ❌ NO shadows in Lynx.js
shadowColor, shadowOffset, shadowOpacity, shadowRadius

// ❌ NO React Native shortcuts
paddingVertical, paddingHorizontal, marginVertical, marginHorizontal
```

### Tailwind Classes Available

The Lynx preset provides these utilities:

**Layout:**
- `flex-1`, `flex-row`, `flex-col`
- `items-center`, `justify-center`, `justify-between`
- `w-full`, `h-full`, `w-[200px]`, `h-[60px]`

**Spacing:**
- `p-4`, `px-5`, `py-3`, `pt-6`, `pb-4`, `pl-2`, `pr-2`
- `m-4`, `mx-5`, `my-3`, `mt-6`, `mb-4`, `ml-2`, `mr-2`
- `pt-[60px]` - arbitrary values in brackets

**Typography:**
- `text-sm`, `text-base`, `text-lg`, `text-xl`, `text-[32px]`
- `font-medium`, `font-semibold`, `font-bold`
- `text-center`, `text-left`, `text-right`

**Colors (custom defined in tailwind.config.ts):**
- `bg-ivory`, `bg-gold`, `bg-blush`, `bg-rose`, `bg-champagne`
- `bg-card`, `bg-muted`, `bg-white`, `bg-black`
- `text-foreground`, `text-muted-foreground`, `text-gold`, `text-white`
- `border-border`

**Border & Rounded:**
- `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-full`
- `border`, `border-b`, `border-t`

**Overflow:**
- `overflow-hidden`

### Component Pattern

Create reusable components that accept both `className` and `style`:

```tsx
interface CardProps {
  children: JSX.Element | JSX.Element[];
  onTap?: () => void;
  style?: Lynx.CSSProperties;
  className?: string;
}

export const Card = ({ children, onTap, style, className }: CardProps) => (
  <view
    bindtap={onTap}
    className={`bg-card rounded-xl overflow-hidden ${className ?? ''}`}
    style={style}
  >
    {children}
  </view>
);
```

### Real Examples

**Header with back button:**
```tsx
<view className="flex-row items-center pt-[60px] pb-4 px-5 bg-card border-b border-border">
  <view bindtap={handleBack} className="p-2">
    <text style={{ fontSize: '24px' }}>{"←"}</text>
  </view>
  <text className="flex-1 text-xl font-semibold text-foreground text-center">
    Title
  </text>
</view>
```

**Button with conditional styling:**
```tsx
<view
  className="py-4 rounded-lg items-center"
  style={{ backgroundColor: isEnabled ? '#D4AF37' : '#E5E5E5' }}
>
  <text
    className="font-semibold text-lg"
    style={{ color: isEnabled ? '#FFFFFF' : '#737373' }}
  >
    Submit
  </text>
</view>
```

**Grid with gap:**
```tsx
<view className="flex-row" style={{ gap: '12px' }}>
  <view className="flex-1 bg-card rounded-lg p-4 items-center">
    <text className="text-sm font-semibold">Item 1</text>
  </view>
  <view className="flex-1 bg-card rounded-lg p-4 items-center">
    <text className="text-sm font-semibold">Item 2</text>
  </view>
</view>
```

### Quick Reference

| Use Case | Method |
|----------|--------|
| Standard spacing | `className="px-5 py-4"` |
| Colors | `className="bg-gold text-white"` |
| Typography | `className="text-lg font-bold"` |
| Layout | `className="flex-1 flex-row items-center"` |
| Borders | `className="rounded-xl border-b border-border"` |
| Dynamic colors | `style={{ backgroundColor: condition ? '#A' : '#B' }}` |
| Gap between items | `style={{ gap: '12px' }}` |
| Line height | `style={{ lineHeight: '20px' }}` |
| Aspect ratio | `style={{ aspectRatio: 0.75 }}` |
| Opacity | `style={{ opacity: 0.5 }}` |

## Important Patterns

### Event Handling
```tsx
// Correct
<view bindtap={handleTap}>

// Wrong (React Native)
<view onPress={handleTap}>
```

### Navigation
Custom navigation via AppContext (no react-navigation):
```typescript
const { navigateTo, goBack } = useApp();
navigateTo('tryon');
goBack();
```

### Type Definitions
Custom components in `src/types/jsx.d.ts`:
```typescript
declare module '@lynx-js/react' {
  namespace JSX {
    interface IntrinsicElements {
      'novia-video': { url?: string; autoplay?: boolean; /* ... */ };
    }
  }
}
```

## Native Modules to Implement

For the try-on MVP:

1. **NoviaGalleryPickerModule** - Photo selection from gallery/camera
2. **NoviaVideoPlayerManager** - Video playback for results
3. **NoviaImageProcessingModule** - Image preprocessing before AI

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/context/AppContext.tsx` | Global state management |
| `src/screens/TryOnScreen.tsx` | MVP try-on feature |
| `src/types/jsx.d.ts` | Custom Lynx component types |
| `ios/Novia/Novia/LynxInitProcessor.m` | Native module registration |
| `ios/Novia/Podfile` | CocoaPods dependencies |

## Context Recovery Checklist

When starting a new session:
- [ ] This is Lynx.js, not React Native
- [ ] Use `bindtap` not `onPress`
- [ ] No React Native styling shortcuts
- [ ] Use `NativeModules.ConsoleLynxProvider.logToConsole()` for debugging
- [ ] Native modules are in `ios/Novia/Novia/`
- [ ] Custom components require type definitions in `jsx.d.ts`
- [ ] Deep link scheme is `novia://`

---

**Remember**: Lynx.js documentation at https://lynxjs.org is the source of truth.
