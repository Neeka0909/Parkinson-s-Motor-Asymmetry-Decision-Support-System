import React, { useState } from 'react';
import { Alert } from 'react-native';
import ScreenContainer from '../components/ScreenContainer';
import BigButton from '../components/BigButton';
import DisclaimerBanner from '../components/DisclaimerBanner';
import ReportCard, { ReportData } from '../components/ReportCard';
import { api } from '../services/api';
import { t } from '../i18n';

type Props = { onBack: () => void };

export default function ReportScreen({ onBack }: Props) {
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [report, setReport] = useState<(ReportData & { report_id?: string }) | null>(null);

  const generate = async () => {
    setLoading(true);
    try {
      const result = await api.generateReport();
      setReport(result);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Report generation failed');
    } finally {
      setLoading(false);
    }
  };

  const download = async () => {
    if (!report?.report_id) return;
    setDownloading(true);
    try {
      await api.downloadReport(report.report_id);
    } catch (e: unknown) {
      Alert.alert('Error', e instanceof Error ? e.message : 'Could not download the report');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <ScreenContainer title={t('report')} subtitle="For your neurologist">
      <DisclaimerBanner />
      <BigButton title={loading ? 'Preparing report...' : t('generateReport')} onPress={generate} />
      {report && (
        <>
          <ReportCard report={report} />
          <BigButton title={downloading ? 'Preparing PDF...' : 'Download PDF'} onPress={download} variant="secondary" />
        </>
      )}
      <BigButton title="Back" onPress={onBack} variant="secondary" />
    </ScreenContainer>
  );
}
