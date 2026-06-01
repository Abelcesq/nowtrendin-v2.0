import { Redirect } from 'expo-router';

// Entry point — always start at the animated splash, which decides where to go next.
export default function Index() {
  return <Redirect href="/splash" />;
}
