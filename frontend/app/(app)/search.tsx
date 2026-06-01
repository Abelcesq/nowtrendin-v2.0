import { View, Text } from 'react-native';
import { Search as SearchIcon } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Input } from '../../components/ui/Input';

export default function Search() {
  return (
    <Screen scroll>
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-4">Search Signals</Text>
      <Input placeholder="Search topics..." icon={<SearchIcon size={18} color="#94A3B8" />} />
      <View className="items-center mt-16">
        <SearchIcon size={48} color="#1E2D3D" />
        <Text className="text-textMuted text-sm mt-4">Search the signal history for any topic.</Text>
      </View>
    </Screen>
  );
}
