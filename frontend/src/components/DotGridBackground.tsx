import DotGrid from "@/components/ui/dot-grid";

export const DotGridBackground = () => {
  return (
    <DotGrid
      dotSize={3}
      gap={30}
      baseColor="rgba(100, 100, 255, 0.4)"
      activeColor="rgba(82, 39, 255, 1)"
      proximity={150}
      shockRadius={250}
      shockStrength={5}
      resistance={750}
      returnDuration={1.5}
      className="opacity-100"
      style={{ backgroundColor: '#0a0a14' }}
    />
  );
};
