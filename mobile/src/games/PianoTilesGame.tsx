import React, { useEffect, useRef, useState } from 'react';
import { Dimensions, Pressable, StyleSheet, Text, View } from 'react-native';
import * as Haptics from 'expo-haptics';
import { EventLogger } from '../utils/eventLogger';
import { highResTimestamp } from '../services/api';

const { width: W } = Dimensions.get('window');
const LANES = [W * 0.2, W * 0.5, W * 0.8];
const TILE_H = 60;

type Tile = { id: number; lane: number; y: number; spawnTime: number };

type Props = {
  onComplete: (score: number, events: EventLogger['events'], durationMs: number) => void;
};

export default function PianoTilesGame({ onComplete }: Props) {
  const [score, setScore] = useState(0);
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [timeLeft, setTimeLeft] = useState(30);
  const logger = useRef(new EventLogger());
  const startTime = useRef(highResTimestamp());
  const idCounter = useRef(0);

  useEffect(() => {
    const spawn = setInterval(() => {
      const lane = Math.floor(Math.random() * 3);
      setTiles((prev) => [
        ...prev.filter((t) => t.y < 800),
        { id: idCounter.current++, lane, y: -TILE_H, spawnTime: highResTimestamp() },
      ]);
    }, 800);

    const move = setInterval(() => {
      setTiles((prev) => prev.map((t) => ({ ...t, y: t.y + 12 })).filter((t) => t.y < 900));
    }, 50);

    const timer = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(spawn);
          clearInterval(move);
          clearInterval(timer);
          onComplete(score, logger.current.events, highResTimestamp() - startTime.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);

    return () => {
      clearInterval(spawn);
      clearInterval(move);
      clearInterval(timer);
    };
  }, [onComplete, score]);

  const tapLane = (lane: number) => {
    const hitZone = 700;
    const tile = tiles.find((t) => t.lane === lane && Math.abs(t.y - hitZone) < 40);
    const x = LANES[lane];
    const side = lane === 0 ? 'left' : lane === 2 ? 'right' : 'center';

    if (tile) {
      const ft = highResTimestamp() - tile.spawnTime;
      logger.current.events.push({
        type: 'tap',
        x,
        y: hitZone,
        hand_side: side,
        timestamp_ms: highResTimestamp(),
        flight_time_ms: ft,
        on_time: true,
      });
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      setScore((s) => s + 10);
      setTiles((prev) => prev.filter((t) => t.id !== tile.id));
    } else {
      logger.current.logTap(x, hitZone, undefined, false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.hud}>
        <Text style={styles.hudText}>Score: {score}</Text>
        <Text style={styles.hudText}>Time: {timeLeft}s</Text>
      </View>
      {tiles.map((t) => (
        <View
          key={t.id}
          style={[styles.tile, { left: LANES[t.lane] - 40, top: t.y, backgroundColor: ['#3498db', '#fff', '#e74c3c'][t.lane] }]}
        />
      ))}
      <View style={styles.hitLine} />
      <View style={styles.lanes}>
        {[0, 1, 2].map((lane) => (
          <Pressable key={lane} style={styles.laneBtn} onPress={() => tapLane(lane)}>
            <Text style={styles.laneText}>{lane === 0 ? 'L' : lane === 2 ? 'R' : 'C'}</Text>
          </Pressable>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f0f23' },
  hud: { flexDirection: 'row', justifyContent: 'space-between', padding: 20, paddingTop: 50 },
  hudText: { color: '#fff', fontSize: 22, fontWeight: '700' },
  tile: { position: 'absolute', width: 80, height: TILE_H, borderRadius: 8 },
  hitLine: { position: 'absolute', top: 700, left: 0, right: 0, height: 3, backgroundColor: '#f1c40f' },
  lanes: { position: 'absolute', bottom: 0, left: 0, right: 0, flexDirection: 'row', height: 100 },
  laneBtn: { flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#333' },
  laneText: { color: '#fff', fontSize: 28, fontWeight: '800' },
});
