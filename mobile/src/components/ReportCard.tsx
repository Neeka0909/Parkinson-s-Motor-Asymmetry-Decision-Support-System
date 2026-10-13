import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

const RISK_COLOR: Record<string, string> = {
  baseline: '#1e8449',
  monitor: '#b7950b',
  elevated: '#d68910',
  referral: '#c0392b',
};

const FEATURE_LABELS: Record<string, string> = {
  rt_rolling_mean_7d: '7-day reaction time (ms)',
  rt_rolling_std_7d: 'Reaction time variability',
  ft_mean: 'Flight time mean (ms)',
  ft_std: 'Flight time variability',
  ht_mean: 'Hold time mean (ms)',
  ht_std: 'Hold time variability',
  ft_asymmetry_trend: 'Asymmetry trend',
  session_consistency: 'Session consistency',
  sustained_asymmetry_flag: 'Sustained asymmetry',
  performance_degradation_rate: 'Performance change',
  total_sessions: 'Sessions in window',
  accuracy_mean: 'Mean accuracy (%)',
};

export type ReportData = {
  risk_profile?: string;
  confidence?: number;
  recommendation?: string;
  feature_summary?: Record<string, number>;
  total_sessions?: number;
  period?: string;
};

type Props = { report: ReportData };

export default function ReportCard({ report }: Props) {
  const risk = String(report.risk_profile ?? 'baseline').toLowerCase();
  const features = report.feature_summary ?? {};
  const rows = Object.entries(FEATURE_LABELS)
    .filter(([key]) => features[key] !== undefined && features[key] !== null)
    .map(([key, label]) => ({ label, value: features[key] }));

  return (
    <View style={styles.card}>
      <Text style={styles.kicker}>Decision-support report</Text>
      <View style={[styles.badge, { backgroundColor: RISK_COLOR[risk] ?? '#1a5276' }]}>
        <Text style={styles.badgeText}>{risk.toUpperCase()}</Text>
      </View>
      <Text style={styles.confidence}>
        Confidence {((Number(report.confidence) || 0) * 100).toFixed(0)}%
      </Text>
      <Text style={styles.recommendation}>{report.recommendation}</Text>
      {(report.total_sessions != null || report.period) && (
        <Text style={styles.meta}>
          {report.total_sessions != null ? `${report.total_sessions} sessions` : ''}
          {report.period ? `  ·  ${report.period}` : ''}
        </Text>
      )}
      {rows.map((row) => (
        <View key={row.label} style={styles.row}>
          <Text style={styles.rowLabel}>{row.label}</Text>
          <Text style={styles.rowValue}>
            {typeof row.value === 'number' ? row.value.toFixed(row.value % 1 === 0 ? 0 : 2) : String(row.value)}
          </Text>
        </View>
      ))}
      <Text style={styles.disclaimer}>
        Exploratory data only. This is not a diagnosis. A neurologist should review these findings.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginVertical: 12,
    borderWidth: 1,
    borderColor: '#d6e2ee',
  },
  kicker: { fontSize: 13, fontWeight: '700', color: '#5d6d7e', letterSpacing: 0.4, marginBottom: 10 },
  badge: { alignSelf: 'flex-start', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6 },
  badgeText: { color: '#fff', fontSize: 18, fontWeight: '800' },
  confidence: { marginTop: 10, fontSize: 16, fontWeight: '700', color: '#1a5276' },
  recommendation: { marginTop: 8, fontSize: 16, lineHeight: 23, color: '#222' },
  meta: { marginTop: 8, fontSize: 14, color: '#666' },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eef2f5',
  },
  rowLabel: { flex: 1, fontSize: 14, color: '#555' },
  rowValue: { fontSize: 14, fontWeight: '700', color: '#1a5276' },
  disclaimer: { marginTop: 12, fontSize: 12, lineHeight: 18, color: '#922b21' },
});
