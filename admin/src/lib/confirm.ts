import { reactive } from "vue";

export type ConfirmTone = "danger" | "primary" | "warning";

export interface ConfirmOptions {
  title: string;
  description?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  tone?: ConfirmTone;
}

type Resolver = (ok: boolean) => void;

interface State {
  open: boolean;
  options: ConfirmOptions;
  loading: boolean;
  resolver: Resolver | null;
}

export const confirmState = reactive<State>({
  open: false,
  options: { title: "" },
  loading: false,
  resolver: null,
});

export function useConfirm() {
  return (options: ConfirmOptions) =>
    new Promise<boolean>((resolve) => {
      confirmState.options = {
        confirmLabel: "Tasdiqlash",
        cancelLabel: "Bekor qilish",
        tone: "danger",
        ...options,
      };
      confirmState.loading = false;
      confirmState.resolver = resolve;
      confirmState.open = true;
    });
}

export function resolveConfirm(ok: boolean) {
  const r = confirmState.resolver;
  confirmState.open = false;
  confirmState.resolver = null;
  confirmState.loading = false;
  r?.(ok);
}

export function setConfirmLoading(v: boolean) {
  confirmState.loading = v;
}
