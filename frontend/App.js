import { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

const API_URL = 'https://nowtrendin-backend-acb79c396814.herokuapp.com/api/todos/';

export default function App() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodos();
  }, []);

  async function fetchTodos() {
    try {
      const res = await fetch(API_URL);
      const data = await res.json();
      setTodos(data);
    } finally {
      setLoading(false);
    }
  }

  async function addTodo() {
    const title = input.trim();
    if (!title) return;
    setInput('');
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
    const newTodo = await res.json();
    setTodos((prev) => [newTodo, ...prev]);
  }

  async function toggleTodo(todo) {
    const res = await fetch(`${API_URL}${todo.id}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: !todo.completed }),
    });
    const updated = await res.json();
    setTodos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
  }

  async function deleteTodo(id) {
    await fetch(`${API_URL}${id}/`, { method: 'DELETE' });
    setTodos((prev) => prev.filter((t) => t.id !== id));
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar style="dark" />
      <Text style={styles.heading}>To-Do List</Text>

      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Add a new task..."
          value={input}
          onChangeText={setInput}
          onSubmitEditing={addTodo}
          returnKeyType="done"
        />
        <Pressable style={styles.addBtn} onPress={addTodo}>
          <Text style={styles.addBtnText}>Add</Text>
        </Pressable>
      </View>

      {loading ? (
        <ActivityIndicator style={{ marginTop: 40 }} size="large" color="#6C63FF" />
      ) : (
        <FlatList
          data={todos}
          keyExtractor={(item) => String(item.id)}
          contentContainerStyle={{ paddingBottom: 40 }}
          renderItem={({ item }) => (
            <View style={styles.todoRow}>
              <Pressable style={styles.todoText} onPress={() => toggleTodo(item)}>
                <Text style={[styles.title, item.completed && styles.completed]}>
                  {item.title}
                </Text>
              </Pressable>
              <Pressable onPress={() => deleteTodo(item.id)}>
                <Text style={styles.deleteBtn}>✕</Text>
              </Pressable>
            </View>
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>No tasks yet. Add one above!</Text>
          }
        />
      )}
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    paddingTop: 60,
    paddingHorizontal: 20,
  },
  heading: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 20,
    color: '#1a1a2e',
  },
  inputRow: {
    flexDirection: 'row',
    marginBottom: 20,
    gap: 10,
  },
  input: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  addBtn: {
    backgroundColor: '#6C63FF',
    borderRadius: 10,
    paddingHorizontal: 18,
    justifyContent: 'center',
  },
  addBtnText: {
    color: '#fff',
    fontWeight: '700',
    fontSize: 16,
  },
  todoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 3,
    elevation: 1,
  },
  todoText: {
    flex: 1,
  },
  title: {
    fontSize: 16,
    color: '#333',
  },
  completed: {
    textDecorationLine: 'line-through',
    color: '#aaa',
  },
  deleteBtn: {
    color: '#ff4d4d',
    fontSize: 16,
    paddingLeft: 12,
  },
  empty: {
    textAlign: 'center',
    color: '#aaa',
    marginTop: 60,
    fontSize: 16,
  },
});
