// Icons for the wedding app using native novia-svg component

interface IconProps {
    size?: number;
    color?: string;
    className?: string;
}

// Helper to create SVG icons using native novia-svg component
const createIcon = (pathD: string, viewBox = '0 0 24 24', strokeWidth = '2') => {
    return ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
        const svgContent = `<svg viewBox="${viewBox}"><path d="${pathD}" fill="none" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
        return (
            <novia-svg
                content={svgContent}
                className={className}
                style={{ width: `${size}px`, height: `${size}px` }}
            />
        );
    };
};

// Helper for filled icons
const createFilledIcon = (pathD: string, viewBox = '0 0 24 24') => {
    return ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
        const svgContent = `<svg viewBox="${viewBox}"><path d="${pathD}" fill="${color}"/></svg>`;
        return (
            <novia-svg
                content={svgContent}
                className={className}
                style={{ width: `${size}px`, height: `${size}px` }}
            />
        );
    };
};

// Dress Icon
export const DressIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M12 2C10 2 9 4 9 4H6L7 8L4 22H20L17 8L18 4H15C15 4 14 2 12 2Z" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 2V8" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Venue Icon
export const VenueIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M3 21h18" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M5 21V7l8-4 8 4v14" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M8 21v-9a4 4 0 0 1 8 0v9" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Camera Icon
export const CameraIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 17a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Light Icon (Lightbulb)
export const LightIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M9 18h6" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M10 22h4" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 2v1" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 7a5 5 0 0 1 5 5c0 2.76-2.5 5-5 5s-5-2.24-5-5a5 5 0 0 1 5-5z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M20 12h1" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M3 12h1" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M5.6 5.6l.7.7" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M17.7 5.6l.7.7" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Gallery Icon (Image)
export const GalleryIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M8.5 10a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M21 15l-5-5L5 21" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Selfie Icon (Smartphone with face)
export const SelfieIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M5 2h14a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 18h.01" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 14a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Back Icon (Arrow left)
export const BackIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M19 12H5" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 19l-7-7 7-7" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Check Icon
export const CheckIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M20 6L9 17l-5-5" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Heart Icon
export const HeartIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Plus Icon
export const PlusIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M12 5v14" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M5 12h14" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Close/X Icon
export const CloseIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M18 6L6 18" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M6 6l12 12" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Settings/Gear Icon
export const SettingsIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Share Icon
export const ShareIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M16 6l-4-4-4 4" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 2v13" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};

// Download Icon
export const DownloadIcon = ({ size = 24, color = '#2D2D2D', className }: IconProps) => {
    const svgContent = `<svg viewBox="0 0 24 24">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M7 10l5 5 5-5" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M12 15V3" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
    return (
        <novia-svg
            content={svgContent}
            className={className}
            style={{ width: `${size}px`, height: `${size}px` }}
        />
    );
};
