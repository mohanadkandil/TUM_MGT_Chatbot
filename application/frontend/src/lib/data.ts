export interface FaqSection {
  title: string;
  questions: Record<string, string>;
}

export const faqData: Record<string, FaqSection> = {
  coursesAndCredits: {
    title: "Credit Recognition",
    questions: {
      "Recognition": "I want to obtain recognition for credits taken at a different University than TUM, which steps do I have to take?",
      "Study Progress": "I am missing some exams, which Study Progress Requirements do I have to fulfill?",
      "Contact": "Who do I have to contact If I am failing to meet the Study Progress Requirements?"
    },
  },
  finalThesis: {
    title: "Final Thesis",
    questions: {
      "Finding topics": "Who can I contact to find a Bachelor Thesis topic and how much In advance should I do it?",
      "Time": "In which Semesters is it possible to write the bachelor thesis?",
      "Company Partners": "How can I write a bachelor’s thesis together with a company?"
    },
  },
  examp: {
    title: "Technical Specialization",
    questions: {
      "Types": "Which technical specializations are available for selection?",
      "Selection": "When do I have to select my technical specialization, and can the decision be changed?",
      "Exchange Semester": "How does my Technical Specialization affect my possible exchange semester times?"
    },
  },
};
