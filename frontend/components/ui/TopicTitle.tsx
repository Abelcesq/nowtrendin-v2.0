import React from 'react';
import { Text, TextProps } from 'react-native';
import { titleCaseTopic } from '../../lib/signals';

// Aurora design-system TOPIC TITLE. Any trend / market / topic NAME shown to the
// user must render Title Case. Use this component (or call titleCaseTopic()) so a
// raw lowercase name from the engine ("correction", "quantum LLMs") never reaches
// the screen un-cased. New components showing a topic name should use this.
export function TopicTitle({ topic, ...props }: { topic?: string } & TextProps) {
  return <Text {...props}>{titleCaseTopic(topic)}</Text>;
}
