import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import DisclaimerBanner from '../components/DisclaimerBanner';
import { t } from '../i18n';

type Props = {
  onPlayGame: (game: 'bubble_pop' | 'piano_tiles' | 'typing_race') => void;
  onProgress: () => void;
  onExercises: () => void;
  onReport: () => void;
  onLogout: () => void;
};

const GAMES = [
  { key: 'bubble_pop' as const, title: 'bubblePop', desc: 'bubblePopDesc', color: '#3498db' },
  { key: 'piano_tiles' as const, title: 'pianoTiles', desc: 'pianoTilesDesc', color: '#9b59b6' },
  { key: 'typing_race' as const, title: 'typingRace', desc: 'typingRaceDesc', color: '#e67e22' },
];

export default function HomeScreen({ onPlayGame, onProgress, onExercises, onReport, onLogout }: Props) {
  return (
    <ScreenContainer title={t('appName')} subtitle={t('tagline')}>
      <DisclaimerBanner />
      <Text style={styles.section}>{t('startGame')}</Text>
      {GAMES.map((g) => (
        <View key={g.key} style={[styles.card, { borderLeftColor: g.color }]}>
          <Text style={styles.cardTitle}>{t(g.title)}</Text>
          <Text style={styles.cardDesc}>{t(g.desc)}</Text>
          <BigButton title={t('play')} onPress={() => onPlayGame(g.key)} style={styles.playBtn} />
        </View>
      ))}
      <View style={styles.navRow}>
        <BigButton title={t('progress')} onPress={onProgress} variant="secondary" style={styles.navBtn} />
        <BigButton title={t('exercises')} onPress={onExercises} variant="secondary" style={styles.navBtn} />
      </View>
      <BigButton title={t('report')} onPress={onReport} />
      <BigButton title="Logout" onPress={onLogout} variant="danger" />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  section: { fontSize: 20, fontWeight: '700', color: '#333', marginBottom: 12 },
  card: {
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    marginBottom: 14,
    borderLeftWidth: 5,
    elevation: 2,
  },
  cardTitle: { fontSize: 22, fontWeight: '800', color: '#1a5276' },
  cardDesc: { fontSize: 15, color: '#666', marginVertical: 8, lineHeight: 22 },
  playBtn: { marginVertical: 4 },
  navRow: { flexDirection: 'row', gap: 8 },
  navBtn: { flex: 1 },
});
