// Reusable Google sign-in hook (expo-auth-session ID-token flow).
// Usage:
//   const { promptGoogle, googleBusy, googleError, ready } = useGoogleAuth();
//   <Button onPress={promptGoogle} disabled={!ready || googleBusy} />
import { useEffect, useState } from 'react';
import * as WebBrowser from 'expo-web-browser';
import * as Google from 'expo-auth-session/providers/google';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../store/auth.store';
import { loginWithGoogle } from './auth';
import {
  GOOGLE_WEB_CLIENT_ID,
  GOOGLE_IOS_CLIENT_ID,
  GOOGLE_ANDROID_CLIENT_ID,
} from '../constants/google';

// Required so the auth popup can close itself on web.
WebBrowser.maybeCompleteAuthSession();

export function useGoogleAuth() {
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);
  const [googleBusy, setGoogleBusy] = useState(false);
  const [googleError, setGoogleError] = useState<string | null>(null);

  const [request, response, promptAsync] = Google.useIdTokenAuthRequest({
    webClientId: GOOGLE_WEB_CLIENT_ID,
    iosClientId: GOOGLE_IOS_CLIENT_ID || undefined,
    androidClientId: GOOGLE_ANDROID_CLIENT_ID || undefined,
  });

  useEffect(() => {
    const run = async () => {
      if (!response) return;
      if (response.type === 'error') {
        setGoogleBusy(false);
        setGoogleError('Google sign-in failed. Please try again.');
        return;
      }
      if (response.type !== 'success') {
        setGoogleBusy(false); // dismissed / cancelled
        return;
      }
      const idToken =
        response.params?.id_token ?? (response.authentication as any)?.idToken;
      if (!idToken) {
        setGoogleBusy(false);
        setGoogleError('Google did not return a sign-in token.');
        return;
      }
      try {
        const { user, token } = await loginWithGoogle(idToken);
        setUser(user, token);
        router.replace(user.tier ? '/(app)' : '/membership');
      } catch (err: any) {
        setGoogleError(err?.data?.detail ?? 'Could not sign in with Google.');
      } finally {
        setGoogleBusy(false);
      }
    };
    run();
  }, [response]);

  const promptGoogle = async () => {
    setGoogleError(null);
    setGoogleBusy(true);
    try {
      await promptAsync();
    } catch {
      setGoogleBusy(false);
      setGoogleError('Could not open Google sign-in.');
    }
  };

  return { promptGoogle, googleBusy, googleError, ready: !!request };
}
