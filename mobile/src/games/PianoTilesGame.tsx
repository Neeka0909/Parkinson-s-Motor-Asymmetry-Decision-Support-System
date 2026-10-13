import React, { useEffect, useRef, useState } from 'react';
import { Dimensions, Pressable, StyleSheet, Text, View } from 'react-native';
import * as Haptics from 'expo-haptics';
import { EventLogger } from '../utils/eventLogger';
import { highResTimestamp } from '../services/api';

const { width: W, height: H } = Dimensions.get('window');
const LANES = [W * 0.2, W * 0.5, W * 0.8];
const TILE_H = 70;
const LANE_BAR = 110;

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
  const scoreRef = useRef(0);
  const finishedRef = useRef(false);
  const onCompleteRef = useRef(onComplete);
  const fieldHeight = useRef(H);
  onCompleteRef.current = onComplete;

  const hitZone = () => Math.max(180, fieldHeight.current - LANE_BAR - TILE_H);

  useEffect(() => {
    const finish = () => {
      if (finishedRef.current) return;
      finishedRef.current = true;
      onCompleteRef.current(scoreRef.current, logger.current.events, highResTimestamp() - startTime.current);
    };

    const spawn = setInterval(() => {
      const lane = Math.floor(Math.random() * 3);
      const limit = fieldHeight.current - LANE_BAR;
      setTiles((prev) => [
        ...prev.filter((t) => t.y < limit),
        { id: idCounter.current++, lane, y: 90, spawnTime: highResTimestamp() },
      ]);
    }, 900);

    const move = setInterval(() => {
      const limit = fieldHeight.current - LANE_BAR + 10;
      setTiles((prev) => prev.map((t) => ({ ...t, y: t.y + 8 })).filter((t) => t.y < limit));
    }, 50);

    const timer = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          clearInterval(spawn);
          clearInterval(move);
          clearInterval(timer);
          setTimeout(finish, 0);
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
  }, []);

  const registerHit = (tile: Tile) => {
    const side = tile.lane === 0 ? 'left' : tile.lane === 2 ? 'right' : 'center';
    const ft = highResTimestamp() - tile.spawnTime;
    logger.current.events.push({
      type: 'tap',
      x: LANES[tile.lane],
      y: tile.y,
      hand_side: side,
      timestamp_ms: highResTimestamp(),
      flight_time_ms: ft,
      on_time: true,
    });
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setScore((s) => {
      const next = s + 10;
      scoreRef.current = next;
      return next;
    });
    setTiles((prev) => prev.filter((t) => t.id !== tile.id));
  };

  const tapLane = (lane: number) => {
    const zone = hitZone();
    const tile = tiles.find((t) => t.lane === lane && t.y >= zone - 40 && t.y <= zone + TILE_H);
    if (tile) {
      registerHit(tile);
      return;
    }
    logger.current.logTap(LANES[lane], zone, undefined, false);
  };

  return (
    <View style={styles.container} onLayout={(e) => { fieldHeight.current = e.nativeEvent.layout.height; }}>
      <View style={styles.hud} pointerEvents="box-none">
        <Text style={styles.hudText}>Score: {score}</Text>
        <Text style={styles.hudText}>Time: {timeLeft}s</Text>
      </View>
      {tiles.map((t) => (
        <Pressable
          key={t.id}
          hitSlop={8}
          onPress={() => registerHit(t)}
          style={[styles.tile, { left: LANES[t.lane] - 45, top: t.y, backgroundColor: ['#3498db', '#f4f6f7', '#e74c3c'][t.lane], zIndex: 2 }]}
        />
      ))}
      <View pointerEvents="none" style={[styles.hitLine, { top: hitZone() }]} />
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
  hud: { flexDirection: 'row', justifyContent: 'flex-start', gap: 18, paddingHorizontal: 16, paddingTop: 52, paddingRight: 100 },
  hudText: { color: '#fff', fontSize: 22, fontWeight: '700' },
  tile: { position: 'absolute', width: 90, height: TILE_H, borderRadius: 8 },
  hitLine: { position: 'absolute', left: 0, right: 0, height: 3, backgroundColor: '#f1c40f' },
  lanes: { position: 'absolute', bottom: 0, left: 0, right: 0, flexDirection: 'row', height: 100 },
  laneBtn: { flex: 1, backgroundColor: 'rgba(255,255,255,0.1)', justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: '#333' },
  laneText: { color: '#fff', fontSize: 28, fontWeight: '800' },
});
