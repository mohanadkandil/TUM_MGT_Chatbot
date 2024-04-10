import { create } from 'zustand';

interface DisclaimerState {
  hasAccepted: boolean;
  setAccepted: (choice: boolean) => void;
}

export const useDisclaimerChoice = create<DisclaimerState>((set) => ({
  hasAccepted: false,
  setAccepted: (state) => set({ hasAccepted: state }),
}));
