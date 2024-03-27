import { create } from 'zustand'

interface SelectedQuestionState {
  selectedQuestion: string;
  setSelectedQuestion: (question: string) => void;
}

export const useSelectedQuestionStore = create<SelectedQuestionState>((set) => ({
  selectedQuestion: '',
  setSelectedQuestion: (question: string) => set({selectedQuestion: question})
}))