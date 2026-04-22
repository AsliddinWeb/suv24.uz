import { useMemo } from "react";
import { StyleSheet, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  interpolate,
  runOnJS,
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
} from "react-native-reanimated";
import { useTheme } from "@/stores/theme";

interface Props {
  label: string;
  onConfirm: () => void | Promise<void>;
  color?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  loading?: boolean;
  disabled?: boolean;
  width?: number;
}

const THUMB_SIZE = 52;
const TRACK_HEIGHT = 62;

export default function SwipeToConfirm({
  label,
  onConfirm,
  color,
  icon = "arrow-forward",
  loading = false,
  disabled = false,
  width = 320,
}: Props) {
  const { colors } = useTheme();
  const trackColor = color || colors.brand;
  const styles = useMemo(() => makeStyles(), []);

  const translateX = useSharedValue(0);
  const thresholdHit = useSharedValue(0);

  const MAX_X = width - THUMB_SIZE - 8;
  const THRESHOLD = MAX_X * 0.85;

  function triggerHaptic(type: "begin" | "threshold" | "confirm") {
    if (type === "begin") Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    else if (type === "threshold") Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    else Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  }

  const gesture = Gesture.Pan()
    .enabled(!disabled && !loading)
    .onBegin(() => {
      runOnJS(triggerHaptic)("begin");
    })
    .onUpdate((e) => {
      const next = Math.max(0, Math.min(e.translationX, MAX_X));
      translateX.value = next;
      if (next >= THRESHOLD && thresholdHit.value === 0) {
        thresholdHit.value = 1;
        runOnJS(triggerHaptic)("threshold");
      } else if (next < THRESHOLD && thresholdHit.value === 1) {
        thresholdHit.value = 0;
      }
    })
    .onEnd(() => {
      if (translateX.value >= THRESHOLD) {
        translateX.value = withTiming(MAX_X, { duration: 150 });
        runOnJS(triggerHaptic)("confirm");
        runOnJS(onConfirm)();
      } else {
        translateX.value = withSpring(0);
        thresholdHit.value = 0;
      }
    });

  const thumbStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  const trackFillStyle = useAnimatedStyle(() => ({
    width: translateX.value + THUMB_SIZE,
  }));

  const labelStyle = useAnimatedStyle(() => {
    const opacity = interpolate(translateX.value, [0, MAX_X * 0.5], [1, 0]);
    return { opacity };
  });

  return (
    <View
      style={[
        styles.track,
        {
          width,
          backgroundColor: trackColor + "20",
          borderColor: trackColor + "30",
        },
        disabled && { opacity: 0.4 },
      ]}
    >
      <Animated.View
        style={[
          StyleSheet.absoluteFillObject,
          { backgroundColor: trackColor, borderRadius: TRACK_HEIGHT / 2 },
          trackFillStyle,
        ]}
      />
      <Animated.View style={[styles.label, labelStyle]}>
        <Ionicons name="chevron-forward" size={18} color={trackColor} style={{ marginRight: 2 }} />
        <Ionicons
          name="chevron-forward"
          size={18}
          color={trackColor}
          style={{ marginRight: 2, opacity: 0.6 }}
        />
        <Ionicons
          name="chevron-forward"
          size={18}
          color={trackColor}
          style={{ marginRight: 8, opacity: 0.3 }}
        />
        <Text style={[styles.labelText, { color: trackColor }]}>{label}</Text>
      </Animated.View>
      <GestureDetector gesture={gesture}>
        <Animated.View style={[styles.thumb, { backgroundColor: trackColor }, thumbStyle]}>
          <Ionicons name={loading ? "ellipsis-horizontal" : icon} size={24} color="#fff" />
        </Animated.View>
      </GestureDetector>
    </View>
  );
}

const makeStyles = () =>
  StyleSheet.create({
    track: {
      height: TRACK_HEIGHT,
      borderRadius: TRACK_HEIGHT / 2,
      borderWidth: 1,
      overflow: "hidden",
      justifyContent: "center",
      alignSelf: "center",
    },
    thumb: {
      position: "absolute",
      left: 4,
      width: THUMB_SIZE,
      height: THUMB_SIZE,
      borderRadius: THUMB_SIZE / 2,
      alignItems: "center",
      justifyContent: "center",
      shadowColor: "#000",
      shadowOpacity: 0.2,
      shadowRadius: 6,
      shadowOffset: { width: 0, height: 4 },
      elevation: 4,
    },
    label: {
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "center",
    },
    labelText: {
      fontSize: 16,
      fontWeight: "700",
      textTransform: "uppercase",
      letterSpacing: 0.5,
    },
  });
