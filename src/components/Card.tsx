import * as Lynx from '@lynx-js/types';

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
