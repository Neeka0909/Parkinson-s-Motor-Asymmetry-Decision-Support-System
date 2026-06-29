import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Dimensions, Pressable, StyleSheet, Text, View } from 'react-native';
import * as Haptics from 'expo-haptics';
import { EventLogger } from '../utils/eventLogger';
import { highResTimestamp } from '../services/api';

const { width: W, height: H } = Dimensions.get('window');

type Bubble = {
  id: number;
  x: number;
  y: number;
  side: 'left' | 'right' | 'center';
  spawnTime: number;
};

type Props = {
  onComplete: (score: number, events: EventLogger['events'], durationMs: number) => void;
};

export default function BubblePopGame({ onComplete }: Props) {
  const [score, setScore] = useState(0);
  const [bubbles, setBubbles] = useState<Bubble[]>([]);
  const [timeLeft, setTimeLeft] = useState(30);
  const logger = useRef(new EventLogger());
  const startTime = useRef(highResTimestamp());
  const idCounter = useRef(0);

  const spawnBubble = useCallback(() => {
    const third = W / 3;
    const zones: Array<'left' | 'center' | 'right'> = ['left', 'center', 'right'];
    const zone = zones[Math.floor(Math.random() * 3)];
    const x = zone === 'left' ? third * 0.5 : zone === 'right' ? third * 2.5 : third * 1.5;
    const bubble: Bubble = {
      id: idCounter.current++,
      x: x - 40,
      y: Math.random() * (H * 0.5) + H * 0.15,
      side: zone,
      spawnTime: highResTimestamp(),
    };
    setBubbles((prev) => [...prev.slice(-8), bubble]);
  }, []);

  useEffect(() => {
    const spawnInterval = setInterval(spawnBubble, 1200);
    const timer = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(timer);
          clearInterval(spawnInterval);
          onComplete(score, logger.current.events, highResTimestamp() - startTime.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    spawnBubble();
    return () => {
      clearInterval(spawnInterval);
      clearInterval(timer);
    };
  }, [spawnBubble, onComplete, score]);

  const popBubble = (bubble: Bubble) => {
    const rt = highResTimestamp() - bubble.spawnTime;
    logger.current.logTap(bubble.x + 40, bubble.y + 40, rt, true);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setScore((s) => s + Math.max(1, Math.round(500 / rt)));
    setBubbles((prev) => prev.filter((b) => b.id !== bubble.id));
  };

  return (
    <View style={styles.container}>
      <View style={styles.hud}>
        <Text style={styles.hudText}>Score: {score}</Text>
        <Text style={styles.hudText}>Time: {timeLeft}s</Text>
      </View>
      <View style={styles.zoneLabels}>
        <Text style={styles.zoneText}>LEFT</Text>
        <Text style={styles.zoneText}>CENTER</Text>
        <Text style={styles.zoneText}>RIGHT</Text>
      </View>
      {bubbles.map((b) => (
        <Pressable
          key={b.id}
          style={[styles.bubble, { left: b.x, top: b.y, backgroundColor: b.side === 'left' ? '#3498db' : b.side === 'right' ? '#e74c3c' : '#2ecc71' }]}
          onPress={() => popBubble(b)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a2e' },
  hud: { flexDirection: 'row', justifyContent: 'space-between', padding: 20, paddingTop: 50 },
  hudText: { color: '#fff', fontSize: 22, fontWeight: '700' },
  zoneLabels: { flexDirection: 'row', justifyContent: 'space-around', paddingVertical: 8 },
  zoneText: { color: '#888', fontSize: 14, fontWeight: '600' },
  bubble: {
    position: 'absolute',
    width: 80,
    height: 80,
    borderRadius: 40,
    borderWidth: 3,
    borderColor: '#fff',
  },
});
