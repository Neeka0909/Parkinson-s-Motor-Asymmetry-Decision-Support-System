import React, { useState } from 'react';
import { Alert, View } from 'react-native';
import BubblePopGame from '../games/BubblePopGame';
import PianoTilesGame from '../games/PianoTilesGame';
import TypingRaceGame from '../games/TypingRaceGame';
import BigButton from '../components/BigButton';
import { api, getTimeOfDay, nowISO } from '../services/api';
import { TapEvent } from '../utils/eventLogger';
import { t } from '../i18n';

type Props = {
  gameType: 'bubble_pop' | 'piano_tiles' | 'typing_race';
  onDone: () => void;
};

export default function GameScreen({ gameType, onDone }: Props) {
  const [submitting, setSubmitting] = useState(false);
  const startedAt = nowISO();

  const handleComplete = async (score: number, events: TapEvent[], durationMs: number) => {
    setSubmitting(true);
    try {
      await api.submitSession({
        game_type: gameType,
        device_orientation: 'portrait',
        time_of_day: getTimeOfDay(),
        score,
        duration_ms: Math.round(durationMs),
        raw_events: events,
        started_at: startedAt,
        completed_at: nowISO(),
      });
      Alert.alert(t('gameOver'), `${t('score')}: ${score}\n${t('goodJob')}`, [{ text: 'OK', onPress: onDone }]);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Submit failed');
      onDone();
    } finally {
      setSubmitting(false);
    }
  };

  const GameComponent =
    gameType === 'bubble_pop' ? BubblePopGame :
    gameType === 'piano_tiles' ? PianoTilesGame : TypingRaceGame;

  return (
    <View style={{ flex: 1 }}>
      <GameComponent onComplete={handleComplete} />
      {!submitting && (
        <BigButton title="Exit" onPress={onDone} variant="danger" style={{ position: 'absolute', top: 50, right: 16, paddingVertical: 8, minHeight: 40 }} />
      )}
    </View>
  );
}
