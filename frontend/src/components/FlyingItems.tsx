import { useEffect, useState } from 'react';

interface FlyingItem {
  id: number;
  src: string;
  alt: string;
  x: number;
  y: number;
  rotation: number;
  scale: number;
  delay: number;
  duration: number;
  direction: 'left-to-right' | 'right-to-left' | 'top-to-bottom' | 'bottom-to-top';
}

const items = [
  { src: '/items/pokeball.webp', alt: 'Pokeball' },
  { src: '/items/greatball.webp', alt: 'Great Ball' },
  { src: '/items/ultraball.webp', alt: 'Ultra Ball' },
  { src: '/items/masterball.webp', alt: 'Master Ball' },
];

const FlyingItems = () => {
  const [flyingItems, setFlyingItems] = useState<FlyingItem[]>([]);

  useEffect(() => {
    const createFlyingItem = (): FlyingItem => {
      const item = items[Math.floor(Math.random() * items.length)];
      const startSide = Math.floor(Math.random() * 4);
      
      const containerWidth = 1200;
      const containerHeight = 500;
      
      let x, y;
      switch (startSide) {
        case 0: // left
          x = -100;
          y = Math.random() * (containerHeight - 100);
          break;
        case 1: // top
          x = Math.random() * (containerWidth - 100);
          y = -100;
          break;
        case 2: // right
          x = containerWidth + 100;
          y = Math.random() * (containerHeight - 100);
          break;
        case 3: // bottom
          x = Math.random() * (containerWidth - 100);
          y = containerHeight + 100;
          break;
        default:
          x = -100;
          y = Math.random() * (containerHeight - 100);
      }

      const directions: ('left-to-right' | 'right-to-left' | 'top-to-bottom' | 'bottom-to-top')[] = [
        'left-to-right',
        'right-to-left', 
        'top-to-bottom',
        'bottom-to-top'
      ];
      
      return {
        id: Date.now() + Math.random(),
        src: item.src,
        alt: item.alt,
        x,
        y,
        rotation: Math.random() * 360,
        scale: 0.6 + Math.random() * 0.6,
        delay: Math.random() * 1000,
        duration: 6000 + Math.random() * 3000,
        direction: directions[startSide],
      };
    };

    const addItem = () => {
      setFlyingItems(prev => {
        // Limit to 15 items on screen at once
        if (prev.length >= 15) {
          return prev;
        }
        return [...prev, createFlyingItem()];
      });
    };

    // Add items periodically with more frequent spawning
    const interval = setInterval(addItem, 1800);

    // Clean up items after animation
    const cleanupInterval = setInterval(() => {
      setFlyingItems(prev => prev.filter(item => 
        Date.now() - item.id < item.duration + 2000
      ));
    }, 2000);

    return () => {
      clearInterval(interval);
      clearInterval(cleanupInterval);
    };
  }, []);

  return (
    <div className="absolute inset-0 pointer-events-none z-10 overflow-hidden">
      {flyingItems.map((item) => (
        <div
          key={item.id}
          className={`absolute animate-fly-${item.direction}`}
          style={{
            '--start-x': `${item.x}px`,
            '--start-y': `${item.y}px`,
            '--initial-rotation': `${item.rotation}deg`,
            '--initial-scale': `${item.scale}`,
            animationDelay: `${item.delay}ms`,
            animationDuration: `${item.duration}ms`,
            animationFillMode: 'both',
          } as React.CSSProperties}
        >
          <img
            src={item.src}
            alt={item.alt}
            className="w-16 h-16 object-contain drop-shadow-lg"
          />
        </div>
      ))}
    </div>
  );
};

export default FlyingItems; 