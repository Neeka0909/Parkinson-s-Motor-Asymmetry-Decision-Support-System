import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import * as SecureStore from 'expo-secure-store';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import GameScreen from './src/screens/GameScreen';
import ProgressScreen from './src/screens/ProgressScreen';
import ExercisesScreen from './src/screens/ExercisesScreen';
import ReportScreen from './src/screens/ReportScreen';
import { api } from './src/services/api';

type Screen = 'login' | 'register' | 'home' | 'game' | 'progress' | 'exercises' | 'report';
type GameType = 'bubble_pop' | 'piano_tiles' | 'typing_race';

export default function App() {
  const [screen, setScreen] = useState<Screen>('login');
  const [gameType, setGameType] = useState<GameType>('bubble_pop');
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    SecureStore.getItemAsync('access_token').then((token) => {
      if (token) setScreen('home');
      setChecking(false);
    });
  }, []);

  const logout = async () => {
    await api.logout();
    setScreen('login');
  };

  if (checking) return null;

  return (
    <>
      <StatusBar style="auto" />
      {screen === 'login' && (
        <LoginScreen onLogin={() => setScreen('home')} onGoRegister={() => setScreen('register')} />
      )}
      {screen === 'register' && (
        <RegisterScreen onRegistered={() => setScreen('home')} onBack={() => setScreen('login')} />
      )}
      {screen === 'home' && (
        <HomeScreen
          onPlayGame={(g) => { setGameType(g); setScreen('game'); }}
          onProgress={() => setScreen('progress')}
          onExercises={() => setScreen('exercises')}
          onReport={() => setScreen('report')}
          onLogout={logout}
        />
      )}
      {screen === 'game' && (
        <GameScreen gameType={gameType} onDone={() => setScreen('home')} />
      )}
      {screen === 'progress' && (
        <ProgressScreen onBack={() => setScreen('home')} />
      )}
      {screen === 'exercises' && (
        <ExercisesScreen onBack={() => setScreen('home')} />
      )}
      {screen === 'report' && (
        <ReportScreen onBack={() => setScreen('home')} />
      )}
    </>
  );
}
