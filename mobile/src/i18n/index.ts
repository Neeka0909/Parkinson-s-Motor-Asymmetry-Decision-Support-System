export type Language = 'en' | 'si' | 'mixed';

const strings: Record<string, Record<Language, string>> = {
  appName: { en: 'Nipun', si: 'නිපුන්', mixed: 'Nipun / නිපුන්' },
  tagline: {
    en: 'Motor Health Assessment',
    si: 'Motor Health Assessment / ශරීර චලන ඇගයීම',
    mixed: 'Motor Health Assessment / ශරීර චලන ඇගයීම',
  },
  disclaimer: {
    en: 'This app provides exploratory data only. It does NOT diagnose Parkinson\'s Disease. Please consult a qualified neurologist.',
    si: 'මෙම යෙදුම exploratory දත්ත පමණක් සපයයි. Parkinson\'s Disease diagnose නොකරයි. වෛද්‍යවරයෙකු සම්බන්ධ කර ගන්න.',
    mixed: 'Exploratory data only / diagnose නොකරයි. Neurologist සම්බන්ධ වන්න.',
  },
  login: { en: 'Login', si: 'Login / පිවිසෙන්න', mixed: 'Login / පිවිසෙන්න' },
  register: { en: 'Register', si: 'Register / ලියාපදිංචි', mixed: 'Register / ලියාපදිංචි' },
  email: { en: 'Email', si: 'Email', mixed: 'Email' },
  password: { en: 'Password', si: 'Password / මුරපදය', mixed: 'Password' },
  fullName: { en: 'Full Name', si: 'Full Name / නම', mixed: 'Full Name / නම' },
  age: { en: 'Age', si: 'Age / වයස', mixed: 'Age / වයස' },
  home: { en: 'Home', si: 'Home / මුල් පිටුව', mixed: 'Home' },
  progress: { en: 'Progress', si: 'Progress / ප්‍රගතිය', mixed: 'Progress' },
  exercises: { en: 'Exercises', si: 'Exercises / ව්‍යායාම', mixed: 'Exercises' },
  report: { en: 'Report', si: 'Report / වාර්තාව', mixed: 'Report' },
  play: { en: 'Play', si: 'Play / ක්‍රීඩා කරන්න', mixed: 'Play' },
  score: { en: 'Score', si: 'Score / ලකුණු', mixed: 'Score' },
  bubblePop: { en: 'Bubble Pop', si: 'Bubble Pop / බුබුළු', mixed: 'Bubble Pop' },
  bubblePopDesc: {
    en: 'Tap bubbles as they appear. Tests reaction time.',
    si: 'බුබුළු පෙනෙන විට tap කරන්න. Reaction time පරීක්ෂා කරයි.',
    mixed: 'Tap bubbles — reaction time test',
  },
  pianoTiles: { en: 'Piano Tiles', si: 'Piano Tiles', mixed: 'Piano Tiles' },
  pianoTilesDesc: {
    en: 'Tap tiles as they fall. Tests flight time.',
    si: 'Tiles ව falling විට tap කරන්න. Flight time පරීක්ෂා කරයි.',
    mixed: 'Tap falling tiles — flight time test',
  },
  typingRace: { en: 'Typing Race', si: 'Typing Race / ටයිප්', mixed: 'Typing Race' },
  typingRaceDesc: {
    en: 'Type the words shown. Tests hold time & hand dynamics.',
    si: 'Words type කරන්න. Hold time සහ hand dynamics පරීක්ෂා කරයි.',
    mixed: 'Type words — hold time test',
  },
  startGame: { en: 'Start Game', si: 'Start / ආරම්භ', mixed: 'Start Game' },
  gameOver: { en: 'Game Over', si: 'Game Over / අවසන්', mixed: 'Game Over' },
  submit: { en: 'Submit Results', si: 'Submit / යවන්න', mixed: 'Submit' },
  totalSessions: { en: 'Total Sessions', si: 'Sessions / සැසි', mixed: 'Total Sessions' },
  streak: { en: 'Day Streak', si: 'Streak / දින', mixed: 'Day Streak' },
  generateReport: { en: 'Generate PDF Report', si: 'PDF Report / වාර්තාව', mixed: 'Generate Report' },
  analyze: { en: 'Run Analysis', si: 'Analysis / විශ්ලේෂණ', mixed: 'Run Analysis' },
  riskProfile: { en: 'Risk Profile', si: 'Risk Profile', mixed: 'Risk Profile' },
  consultNeurologist: {
    en: 'Please consult a neurologist if you notice sustained changes.',
    si: 'Sustained changes noticing නම් neurologist සම්බන්ධ වන්න.',
    mixed: 'Consult neurologist if sustained changes noticed.',
  },
  goodJob: { en: 'Great job!', si: 'Great job! / හොඳයි!', mixed: 'Great job!' },
  tapLeft: { en: 'Tap Left', si: 'Tap Left / වම', mixed: 'Tap Left' },
  tapRight: { en: 'Tap Right', si: 'Tap Right / දකුණ', mixed: 'Tap Right' },
  typeHere: { en: 'Type here...', si: 'Type here...', mixed: 'Type here...' },
};

export function t(key: string, lang: Language = 'mixed'): string {
  return strings[key]?.[lang] ?? strings[key]?.en ?? key;
}
