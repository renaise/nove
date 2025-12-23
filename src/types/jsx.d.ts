import * as Lynx from '@lynx-js/types';
import {
  NoviaPhotoGalleryAssetSelectedEvent,
  NoviaPhotoGalleryPermissionsEvent,
  NoviaPhotoGalleryMediaTypeEvent,
  NoviaVideoLoadStartEvent,
  NoviaVideoReadyEvent,
  NoviaVideoEndedEvent,
  NoviaVideoErrorEvent,
} from './native-modules';

// Extend CSSProperties to include Lynx list-specific styles
declare module '@lynx-js/types' {
  interface CSSProperties {
    listMainAxisGap?: string;
    listCrossAxisGap?: string;
  }
}

declare module '@lynx-js/react' {
  namespace JSX {
    interface IntrinsicElements {
      'novia-photo-gallery': {
        mediaType?: 'all' | 'photos' | 'videos' | 'live';
        pageSize?: number;
        currentPage?: number;
        autoLoadPermissions?: boolean;
        selections?: Record<string, number>;
        bindassetselected?: (e: NoviaPhotoGalleryAssetSelectedEvent) => void;
        bindpermissionschanged?: (e: NoviaPhotoGalleryPermissionsEvent) => void;
        bindmediatypechanged?: (e: NoviaPhotoGalleryMediaTypeEvent) => void;
        style?: string | Lynx.CSSProperties;
        className?: string;
      };
      'novia-video': {
        url?: string;
        autoplay?: boolean;
        muted?: boolean;
        loop?: boolean;
        paused?: boolean;
        resizeMode?: 'cover' | 'contain' | 'stretch';
        bindloadstart?: (e: NoviaVideoLoadStartEvent) => void;
        bindready?: (e: NoviaVideoReadyEvent) => void;
        bindended?: (e: NoviaVideoEndedEvent) => void;
        binderror?: (e: NoviaVideoErrorEvent) => void;
        style?: string | Lynx.CSSProperties;
        className?: string;
      };
      'novia-liquid-glass': {
        key?: string | number;
        glassStyle?: 'regular' | 'clear' | 0 | 1;
        tintColor?: string;
        tintAlpha?: number;
        cornerRadius?: number;
        interactive?: boolean;
        addBorder?: boolean;
        bindtap?: (e: Lynx.TouchEvent) => void;
        style?: string | Lynx.CSSProperties;
        className?: string;
        children?: React.ReactNode;
      };
      'novia-svg': {
        content?: string;
        tintColor?: string;
        style?: string | Lynx.CSSProperties;
        className?: string;
      };
    }
  }
}
