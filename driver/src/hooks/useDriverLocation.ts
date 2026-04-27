import { useEffect, useRef, useState } from "react";
import { AppState, type AppStateStatus } from "react-native";
import * as Location from "expo-location";
import { driversApi } from "@/api/drivers";

export interface Coords {
  lat: number;
  lng: number;
}

interface Options {
  /** How often to ping the server, ms. Default 30s. */
  reportEvery?: number;
  /** Whether GPS reporting is active (e.g. tab focused, user authenticated). */
  enabled?: boolean;
}

/**
 * Tracks driver's GPS position in foreground and pings backend.
 * Returns the latest known position (or null) so callers can compute distance.
 */
export function useDriverLocation({ reportEvery = 30_000, enabled = true }: Options = {}) {
  const [coords, setCoords] = useState<Coords | null>(null);
  const [error, setError] = useState<string | null>(null);
  const watchSub = useRef<Location.LocationSubscription | null>(null);
  const reportTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const lastReported = useRef<Coords | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;

    async function start() {
      try {
        const perm = await Location.requestForegroundPermissionsAsync();
        if (perm.status !== "granted") {
          setError("Joylashuv ruxsati berilmagan");
          return;
        }

        const initial = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.Balanced,
        });
        if (cancelled) return;
        const c = { lat: initial.coords.latitude, lng: initial.coords.longitude };
        setCoords(c);
        report(c);

        // Live updates while foregrounded
        watchSub.current = await Location.watchPositionAsync(
          {
            accuracy: Location.Accuracy.Balanced,
            distanceInterval: 25, // metr — har 25 m da yangilanadi
            timeInterval: 10_000,
          },
          (loc) => {
            const next = { lat: loc.coords.latitude, lng: loc.coords.longitude };
            setCoords(next);
          },
        );

        // Periodic server report
        reportTimer.current = setInterval(() => {
          // re-read latest from state via callback ref
          const c = lastSeen.current;
          if (c) report(c);
        }, reportEvery);
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "GPS xatosi");
      }
    }

    start();

    const sub = AppState.addEventListener("change", (s: AppStateStatus) => {
      if (s === "active" && enabled) {
        // Force a fresh report when returning to foreground
        Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced })
          .then((loc) => {
            const next = { lat: loc.coords.latitude, lng: loc.coords.longitude };
            setCoords(next);
            report(next);
          })
          .catch(() => undefined);
      }
    });

    return () => {
      cancelled = true;
      watchSub.current?.remove();
      if (reportTimer.current) clearInterval(reportTimer.current);
      sub.remove();
    };
  }, [enabled, reportEvery]);

  // Track latest coord without retriggering effect
  const lastSeen = useRef<Coords | null>(null);
  useEffect(() => {
    lastSeen.current = coords;
  }, [coords]);

  function report(c: Coords) {
    // Skip if we reported the same point recently (within ~10 m)
    if (lastReported.current && haversineKm(lastReported.current, c) < 0.01) {
      return;
    }
    lastReported.current = c;
    driversApi.reportLocation(c.lat, c.lng).catch(() => undefined);
  }

  return { coords, error };
}

// ----- Geometry helpers -----

export function haversineKm(a: Coords, b: Coords): number {
  const R = 6371;
  const dLat = toRad(b.lat - a.lat);
  const dLng = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat);
  const lat2 = toRad(b.lat);
  const sinDLat = Math.sin(dLat / 2);
  const sinDLng = Math.sin(dLng / 2);
  const x = sinDLat * sinDLat + Math.cos(lat1) * Math.cos(lat2) * sinDLng * sinDLng;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(x)));
}

function toRad(d: number): number {
  return (d * Math.PI) / 180;
}
