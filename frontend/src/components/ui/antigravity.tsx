import React, { useEffect, useRef } from 'react';

interface AntigravityProps {
  count?: number;
  magnetRadius?: number;
  ringRadius?: number;
  waveSpeed?: number;
  waveAmplitude?: number;
  particleSize?: number;
  lerpSpeed?: number;
  color?: string;
  autoAnimate?: boolean;
  particleVariance?: number;
  rotationSpeed?: number;
  depthFactor?: number;
  pulseSpeed?: number;
  particleShape?: 'circle' | 'capsule';
  fieldStrength?: number;
}

export const Antigravity: React.FC<AntigravityProps> = ({
  count = 800,
  magnetRadius = 250,
  ringRadius = 10,
  waveSpeed = 0.02,
  waveAmplitude = 0.5,
  particleSize = 2,
  lerpSpeed = 0.08,
  color = '#ffffff',
  autoAnimate = true,
  particleVariance = 2,
  rotationSpeed = 0,
  depthFactor = 1,
  pulseSpeed = 3,
  particleShape = 'capsule',
  fieldStrength = 40,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: -1000, y: -1000 });
  const particlesRef = useRef<any[]>([]);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { alpha: false });
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    const initParticles = () => {
      particlesRef.current = [];
      // Distribute particles evenly across the entire screen
      const cols = Math.ceil(Math.sqrt(count * (canvas.width / canvas.height)));
      const rows = Math.ceil(count / cols);
      const spacingX = canvas.width / cols;
      const spacingY = canvas.height / rows;

      for (let i = 0; i < count; i++) {
        const col = i % cols;
        const row = Math.floor(i / cols);
        const baseX = col * spacingX + spacingX / 2 + (Math.random() - 0.5) * spacingX * 0.5;
        const baseY = row * spacingY + spacingY / 2 + (Math.random() - 0.5) * spacingY * 0.5;

        particlesRef.current.push({
          x: baseX,
          y: baseY,
          baseX: baseX,
          baseY: baseY,
          vx: 0,
          vy: 0,
          size: particleSize + Math.random() * particleVariance,
          angle: Math.random() * Math.PI * 2,
          rotationSpeed: (Math.random() - 0.5) * 0.03,
          depth: Math.random(),
          pulseOffset: Math.random() * Math.PI * 2,
        });
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    const handleMouseLeave = () => {
      mouseRef.current = { x: -1000, y: -1000 };
    };

    const hexToRgb = (hex: string) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : { r: 255, g: 255, b: 255 };
    };

    const rgb = hexToRgb(color);
    let time = 0;

    const animate = () => {
      time += 0.01;
      
      // Clear canvas
      ctx.fillStyle = '#000000';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach((particle) => {
        // Calculate distance to mouse
        const dx = mouseRef.current.x - particle.x;
        const dy = mouseRef.current.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Strong attraction to mouse
        if (distance < magnetRadius && distance > 1) {
          const force = ((magnetRadius - distance) / magnetRadius) * fieldStrength;
          const angle = Math.atan2(dy, dx);
          particle.vx += Math.cos(angle) * force * 0.02;
          particle.vy += Math.sin(angle) * force * 0.02;
        }

        // Apply velocity
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Gentle pull back to base position
        const returnForce = distance > magnetRadius ? lerpSpeed : lerpSpeed * 0.3;
        particle.x += (particle.baseX - particle.x) * returnForce * 0.01;
        particle.y += (particle.baseY - particle.y) * returnForce * 0.01;

        // Damping
        particle.vx *= 0.90;
        particle.vy *= 0.90;

        // Wrap around edges
        if (particle.x < -50) particle.x = canvas.width + 50;
        if (particle.x > canvas.width + 50) particle.x = -50;
        if (particle.y < -50) particle.y = canvas.height + 50;
        if (particle.y > canvas.height + 50) particle.y = -50;

        // Update rotation
        particle.angle += particle.rotationSpeed;

        // Pulsing effect
        const pulse = Math.sin(time * pulseSpeed + particle.pulseOffset) * 0.3 + 0.7;
        
        // Depth-based opacity and size
        const depthScale = 0.4 + particle.depth * 0.6;
        const opacity = (0.5 + particle.depth * 0.3) * pulse;

        // Draw particle
        ctx.save();
        ctx.translate(particle.x, particle.y);
        ctx.rotate(particle.angle);
        ctx.globalAlpha = opacity;

        if (particleShape === 'capsule') {
          // Draw capsule (elongated pill shape)
          const width = particle.size * 5 * depthScale;
          const height = particle.size * 1.2 * depthScale;
          
          ctx.fillStyle = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
          ctx.beginPath();
          
          // Draw rounded rectangle (capsule)
          const radius = height / 2;
          ctx.moveTo(-width / 2 + radius, -height / 2);
          ctx.lineTo(width / 2 - radius, -height / 2);
          ctx.arc(width / 2 - radius, 0, radius, -Math.PI / 2, Math.PI / 2);
          ctx.lineTo(-width / 2 + radius, height / 2);
          ctx.arc(-width / 2 + radius, 0, radius, Math.PI / 2, -Math.PI / 2);
          ctx.closePath();
          ctx.fill();
        } else {
          // Draw circle
          ctx.fillStyle = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
          ctx.beginPath();
          ctx.arc(0, 0, particle.size * depthScale, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.restore();
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [
    count,
    magnetRadius,
    ringRadius,
    waveSpeed,
    waveAmplitude,
    particleSize,
    lerpSpeed,
    color,
    autoAnimate,
    particleVariance,
    rotationSpeed,
    depthFactor,
    pulseSpeed,
    particleShape,
    fieldStrength,
  ]);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full pointer-events-none"
      style={{ background: '#000000' }}
    />
  );
};
