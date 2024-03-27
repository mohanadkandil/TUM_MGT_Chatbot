import { create } from 'zustand';

interface SelectedMajorState {
  selectedMajor: string;
  setSelectedMajor: (major: string) => void;
}

export const useSelectedMajorStore = create<SelectedMajorState>((set) => ({
  selectedMajor: '',
  setSelectedMajor: (major) => set({ selectedMajor: major }),
}));
