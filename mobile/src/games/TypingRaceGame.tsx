import React, { useRef, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import * as Haptics from 'expo-haptics';
import { EventLogger, getKeyHandSide } from '../utils/eventLogger';
import { highResTimestamp } from '../services/api';

const WORDS = ['hello', 'world', 'park', 'health', 'brain', 'motor', 'touch', 'speed', 'left', 'right'];
const KEYBOARD = [
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
  ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
];

type Props = {
  onComplete: (score: number, events: EventLogger['events'], durationMs: number) => void;
};

export default function TypingRaceGame({ onComplete }: Props) {
  const [wordIndex, setWordIndex] = useState(0);
  const [typed, setTyped] = useState('');
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const logger = useRef(new EventLogger());
  const startTime = useRef(highResTimestamp());
  const keyDownRef = useRef<Record<string, number>>({});

  const target = WORDS[wordIndex % WORDS.length];

  const pressKey = (key: string) => {
    if (finished) return;
    const ts = highResTimestamp();
    keyDownRef.current[key] = ts;

    const next = typed + key;
    const correct = target.startsWith(next);
    if (!correct) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      setTyped('');
      return;
    }

    setTyped(next);
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

    setTimeout(() => {
      const holdTime = highResTimestamp() - (keyDownRef.current[key] ?? ts);
      logger.current.events.push({
        type: 'key',
        key,
        hand_side: getKeyHandSide(key),
        timestamp_ms: highResTimestamp(),
        hold_time_ms: holdTime,
        correct: true,
      });
    }, 50);

    if (next === target) {
      setScore((s) => s + target.length * 10);
      if (wordIndex >= WORDS.length - 1) {
        setFinished(true);
        onComplete(score + target.length * 10, logger.current.events, highResTimestamp() - startTime.current);
      } else {
        setWordIndex((i) => i + 1);
        setTyped('');
      }
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.score}>Score: {score}</Text>
      <Text style={styles.label}>Type this word:</Text>
      <Text style={styles.target}>{target}</Text>
      <Text style={styles.typed}>{typed}<Text style={styles.cursor}>|</Text></Text>
      <View style={styles.keyboard}>
        {KEYBOARD.map((row, ri) => (
          <View key={ri} style={styles.row}>
            {row.map((key) => (
              <Pressable
                key={key}
                style={[styles.key, getKeyHandSide(key) === 'left' ? styles.leftKey : styles.rightKey]}
                onPress={() => pressKey(key)}
              >
                <Text style={styles.keyText}>{key.toUpperCase()}</Text>
              </Pressable>
            ))}
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a2e', paddingTop: 60, paddingHorizontal: 16 },
  score: { color: '#fff', fontSize: 22, fontWeight: '700', marginBottom: 24 },
  label: { color: '#aaa', fontSize: 18 },
  target: { color: '#f1c40f', fontSize: 36, fontWeight: '800', marginVertical: 16, letterSpacing: 4 },
  typed: { color: '#fff', fontSize: 28, marginBottom: 32, minHeight: 40 },
  cursor: { color: '#3498db' },
  keyboard: { marginTop: 'auto', marginBottom: 20 },
  row: { flexDirection: 'row', justifyContent: 'center', marginBottom: 8 },
  key: { minWidth: 32, height: 48, margin: 3, borderRadius: 8, justifyContent: 'center', alignItems: 'center' },
  leftKey: { backgroundColor: '#2980b9' },
  rightKey: { backgroundColor: '#c0392b' },
  keyText: { color: '#fff', fontSize: 18, fontWeight: '700' },
});
