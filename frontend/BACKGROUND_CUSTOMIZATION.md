# 🎨 Background Customization Guide

## Quick Color Presets

### Purple/Pink (Current)
```tsx
color="#FF9FFC"
```
Perfect for: Modern, creative, tech portfolios

### Cyan/Blue
```tsx
color="#00D9FF"
```
Perfect for: Professional, corporate, clean look

### Green/Mint
```tsx
color="#00FF88"
```
Perfect for: Fresh, eco-friendly, health tech

### Red/Orange
```tsx
color="#FF6B6B"
```
Perfect for: Bold, energetic, attention-grabbing

### Gold/Yellow
```tsx
color="#FFD700"
```
Perfect for: Premium, luxury, high-end

### Multi-Color (Advanced)
For gradient effects, you can modify the component to use multiple colors.

## Particle Density Presets

### Minimal (Performance)
```tsx
count={100}
particleSize={3}
```
Best for: Older devices, mobile-first

### Balanced (Current)
```tsx
count={300}
particleSize={2}
```
Best for: Most use cases

### Dense (Impressive)
```tsx
count={500}
particleSize={1.5}
```
Best for: High-end demos, desktop-only

### Ultra Dense (Wow Factor)
```tsx
count={800}
particleSize={1}
```
Best for: Screenshots, hero sections

## Animation Speed Presets

### Calm
```tsx
waveSpeed={0.2}
pulseSpeed={1}
```
Subtle, professional

### Moderate (Current)
```tsx
waveSpeed={0.4}
pulseSpeed={3}
```
Balanced, engaging

### Energetic
```tsx
waveSpeed={0.8}
pulseSpeed={5}
```
Dynamic, exciting

### Hyperactive
```tsx
waveSpeed={1.5}
pulseSpeed={8}
```
Intense, attention-grabbing

## Interaction Strength Presets

### Gentle
```tsx
magnetRadius={5}
fieldStrength={5}
```
Subtle mouse interaction

### Moderate (Current)
```tsx
magnetRadius={10}
fieldStrength={10}
```
Noticeable but not overwhelming

### Strong
```tsx
magnetRadius={15}
fieldStrength={20}
```
Very responsive to mouse

### Extreme
```tsx
magnetRadius={25}
fieldStrength={40}
```
Dramatic particle movement

## Complete Theme Examples

### Cyberpunk Theme
```tsx
<Antigravity
  count={400}
  color="#00FFFF"
  particleSize={1.5}
  waveSpeed={0.8}
  pulseSpeed={5}
  fieldStrength={15}
  particleShape="capsule"
/>
```

### Minimal Professional
```tsx
<Antigravity
  count={150}
  color="#4A90E2"
  particleSize={2}
  waveSpeed={0.2}
  pulseSpeed={1}
  fieldStrength={5}
  particleShape="circle"
/>
```

### Vibrant Creative
```tsx
<Antigravity
  count={500}
  color="#FF6B6B"
  particleSize={2}
  waveSpeed={0.6}
  pulseSpeed={4}
  fieldStrength={12}
  particleShape="capsule"
/>
```

### Elegant Luxury
```tsx
<Antigravity
  count={250}
  color="#FFD700"
  particleSize={2.5}
  waveSpeed={0.3}
  pulseSpeed={2}
  fieldStrength={8}
  particleShape="circle"
/>
```

## Background Color Combinations

### Dark Themes
```tsx
// Black + Pink (Current)
bg-black + color="#FF9FFC"

// Dark Blue + Cyan
bg-slate-900 + color="#00D9FF"

// Dark Purple + Pink
bg-purple-950 + color="#FF6BFF"

// Charcoal + Green
bg-gray-900 + color="#00FF88"
```

### Light Themes (Advanced)
```tsx
// White + Purple
bg-white + color="#9B59B6"

// Light Gray + Blue
bg-gray-100 + color="#3498DB"
```

## Card Transparency Options

### More Transparent (Show more background)
```tsx
className="bg-background/60 backdrop-blur-xl"
```

### Current (Balanced)
```tsx
className="bg-background/80 backdrop-blur-xl"
```

### Less Transparent (More readable)
```tsx
className="bg-background/95 backdrop-blur-lg"
```

### Solid (No transparency)
```tsx
className="bg-background backdrop-blur-none"
```

## How to Apply Changes

1. Open `frontend/src/pages/Login.tsx`
2. Find the `<Antigravity>` component
3. Change the props you want
4. Save and rebuild:
   ```bash
   npm run build
   ```

## Testing Locally

```bash
cd frontend
npm run dev
```

Visit `http://localhost:8080` to see your changes in real-time!

## Pro Tips

1. **Match your brand colors** - Use your portfolio's color scheme
2. **Test on mobile** - Reduce particle count for better performance
3. **Consider accessibility** - Some users may prefer reduced motion
4. **Take screenshots** - Capture the best moments for your portfolio
5. **A/B test** - Try different colors and see what gets more attention

## Performance Optimization

If the animation is slow:
1. Reduce `count` (fewer particles)
2. Increase `lerpSpeed` (faster settling)
3. Reduce `fieldStrength` (less computation)
4. Use `particleShape="circle"` (simpler rendering)

## Accessibility Note

For users who prefer reduced motion, you can add:

```tsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

{!prefersReducedMotion && <Antigravity ... />}
```

---

**Experiment and find the perfect look for your portfolio!** 🎨
