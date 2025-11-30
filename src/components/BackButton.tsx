import * as Lynx from '@lynx-js/types';

interface BackButtonProps {
  onTap: () => void;
  style?: Lynx.CSSProperties;
  className?: string;
}

export const BackButton = ({ onTap, style, className }: BackButtonProps) => (
  <view
    bindtap={onTap}
    className={`p-2 ${className ?? ''}`}
    style={style}
  >
    <text style={{ fontSize: '24px' }}>{"←"}</text>
  </view>
);
