import { Antigravity } from "@/components/ui/antigravity";

export const AntigravityBackground = () => {
  return (
    <div className="fixed inset-0 z-0 bg-black">
      <Antigravity
        count={800}
        magnetRadius={250}
        particleSize={2}
        lerpSpeed={0.08}
        color="#ffffff"
        particleVariance={2}
        rotationSpeed={0}
        pulseSpeed={3}
        particleShape="capsule"
        fieldStrength={40}
      />
    </div>
  );
};
