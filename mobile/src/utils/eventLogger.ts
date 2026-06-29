import { Dimensions } from 'react-native';

const { width: SCREEN_W } = Dimensions.get('window');

export type TapEvent = {
  type: 'tap' | 'key';
  x?: number;
  y?: number;
  key?: string;
  hand_side: 'left' | 'right' | 'center';
  timestamp_ms: number;
  reaction_time_ms?: number;
  flight_time_ms?: number;
  hold_time_ms?: number;
  hit?: boolean;
  on_time?: boolean;
  correct?: boolean;
};

export function getHandSide(x: number, screenWidth = SCREEN_W): 'left' | 'right' | 'center' {
  const third = screenWidth / 3;
  if (x < third) return 'left';
  if (x > third * 2) return 'right';
  return 'center';
}

const LEFT_KEYS = new Set(['q', 'w', 'e', 'r', 't', 'a', 's', 'd', 'f', 'g', 'z', 'x', 'c', 'v', 'b']);
const RIGHT_KEYS = new Set(['y', 'u', 'i', 'o', 'p', 'h', 'j', 'k', 'l', 'n', 'm']);

export function getKeyHandSide(key: string): 'left' | 'right' {
  const k = key.toLowerCase();
  if (LEFT_KEYS.has(k)) return 'left';
  if (RIGHT_KEYS.has(k)) return 'right';
  return 'left';
}

export class EventLogger {
  events: TapEvent[] = [];
  private lastTimestamp = 0;
  private keyDownTimes: Record<string, number> = {};

  logTap(x: number, y: number, reactionTimeMs?: number, hit = true) {
    const ts = performance.now();
    const event: TapEvent = {
      type: 'tap',
      x,
      y,
      hand_side: getHandSide(x),
      timestamp_ms: ts,
      reaction_time_ms: reactionTimeMs,
      flight_time_ms: this.lastTimestamp ? ts - this.lastTimestamp : undefined,
      hit,
    };
    this.events.push(event);
    this.lastTimestamp = ts;
  }

  logKeyDown(key: string) {
    this.keyDownTimes[key] = performance.now();
  }

  logKeyUp(key: string, correct = true) {
    const down = this.keyDownTimes[key];
    const ts = performance.now();
    const holdTime = down ? ts - down : undefined;
    const event: TapEvent = {
      type: 'key',
      key,
      hand_side: getKeyHandSide(key),
      timestamp_ms: ts,
      hold_time_ms: holdTime,
      flight_time_ms: this.lastTimestamp ? ts - this.lastTimestamp : undefined,
      correct,
    };
    this.events.push(event);
    this.lastTimestamp = ts;
    delete this.keyDownTimes[key];
  }
}
